import logging
from pathlib import Path
from typing import Self

import anyio
import magic
from pazufa_corelib.llm import LLMConnector, LLMProviderError
from scrapy.exceptions import DropItem

from pazufa_scraper_be.constants import SUMMARY_FILE_NAME, TEXT_FILE_NAME
from pazufa_scraper_be.pardok import BaseGesetzDokument, DrsDokument, GesetzVorgang, GVBlDokument
from pazufa_scraper_be.pardok.dokument import Protokoll
from pazufa_scraper_be.pipelines._base import CacheDirPipeline, LLMPipeline

logger = logging.getLogger(__name__)


class LLMSummaryNotImplementedError(NotImplementedError):
    """Summary for document not (yet) implemented."""


async def summarize(llm_connector: LLMConnector, dokument: BaseGesetzDokument, text_file: Path) -> str | None:
    """Summarize extracted document text via the LLM connector, dispatching by document type."""
    if len(dokument.vorgang.dokumente) > 0:
        titel = getattr(dokument.vorgang.dokumente[0], "titel", "")
        vorgang_vnr = dokument.vorgang.dokumente[0].nr or ""

    else:
        titel = vorgang_vnr = ""

    text = await anyio.Path(text_file).read_text()

    if isinstance(dokument, Protokoll):
        if relevant_section := await llm_connector.extract_relevant_section(text=text, vorgang_titel=titel, vorgang_vnr=vorgang_vnr):
            return await llm_connector.summarize_dokument(titel=titel, text=relevant_section)

    elif isinstance(dokument, GVBlDokument):
        return await llm_connector.summarize_gesetzentwurf(titel=titel, text=text)

    elif isinstance(dokument, DrsDokument):
        return await llm_connector.summarize_dokument(titel=titel, text=text)

    return None


class SummarizeExtractedPDFText(CacheDirPipeline, LLMPipeline):
    """Pipeline that summarizes extracted document text via an LLM."""

    def link(self: Self, summary_file: Path, model_specific_summary_file: Path) -> None:
        """Create a symlink from summary_file pointing to the model-specific summary file."""
        summary_file.unlink(missing_ok=True)
        summary_file.symlink_to(model_specific_summary_file.relative_to(summary_file.parent))

    # TODO(se-jaeger): refactor to reduce complexity
    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:  # noqa: C901, PLR0912
        """Summarize extracted text for each document in the Vorgang and cache the result."""
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        if self.llm_connector is None:
            return vorgang

        for dokument in vorgang.dokumente:
            for dokument_url in dokument.all_urls:
                if dokument_dir := self.get_dokument_cache_dir(dokument=dokument, url=dokument_url):
                    text_file = dokument_dir / TEXT_FILE_NAME
                    summary_file = dokument_dir / SUMMARY_FILE_NAME

                    # There is no text to summarize => skip
                    if not text_file.exists():
                        continue

                    # If model specific summary exist => link and skip
                    if self.llm_model_name is not None:
                        model_specific_summary_file = dokument_dir / str(summary_file.stem + "_" + self.llm_model_name.replace("/", "__") + summary_file.suffix)

                        if model_specific_summary_file.exists():
                            self.link(summary_file=summary_file, model_specific_summary_file=model_specific_summary_file)
                            continue

                    # If model is not specified but there is a summary file => skip
                    if self.llm_model_name is None and summary_file.exists():
                        continue

                    try:
                        summary = await summarize(self.llm_connector, dokument, text_file)

                    except LLMProviderError:
                        msg = f"[{vorgang.id} - {dokument.id}]: LLM summarization failed due to provider problem."
                        logger.warning(msg)
                        continue

                    if summary is None:
                        msg = f"[{vorgang.id} - {dokument.id}]: LLM summarization failed due to application problem."
                        logger.warning(msg)

                    elif len(summary) == 0:
                        msg = f"[{vorgang.id} - {dokument.id}]: Summary is empty."
                        logger.warning(msg)

                    elif magic.from_buffer(summary, mime=True) != "text/plain":
                        error_file = self.get_errors_dir() / f"{dokument.id}__{self.llm_model_name.replace('/', '__')}.summary"
                        error_file.write_text(summary)

                        # NOTE: This is a hack, where the mime type of the saved file gets 'text/plain', which is causing issues
                        if magic.from_file(error_file, mime=True) == "text/plain":
                            error_file.rename(model_specific_summary_file)
                            self.link(summary_file=summary_file, model_specific_summary_file=model_specific_summary_file)

                        else:
                            msg = f"[{vorgang.id} - {dokument.id}]: Summary is not plain text."
                            logger.warning(msg)

                    else:
                        model_specific_summary_file.write_text(summary)
                        self.link(summary_file=summary_file, model_specific_summary_file=model_specific_summary_file)

        return vorgang
