import logging
from typing import Self

import kreuzberg
import magic
from scrapy.exceptions import DropItem

from pazufa_scraper_be.constants import DOKUMENT_FILE_NAME, TEXT_FILE_NAME
from pazufa_scraper_be.pardok import GesetzVorgang
from pazufa_scraper_be.pipelines._base import CacheDirPipeline

logger = logging.getLogger(__name__)


class ExtractTextFromPDF(CacheDirPipeline):
    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            for dokument_url in dokument.all_urls:
                if dokument_dir := self.get_dokument_cache_dir(dokument=dokument, url=dokument_url):
                    dokument_file = dokument_dir / DOKUMENT_FILE_NAME
                    dokument_text_file = dokument_dir / TEXT_FILE_NAME

                    if dokument_file.exists() and not dokument_text_file.exists():
                        pdf = await kreuzberg.extract_file(
                            dokument_file,
                            config=kreuzberg.ExtractionConfig(enable_quality_processing=True, pages=kreuzberg.PageConfig(extract_pages=True), use_cache=False),
                        )
                        text = "\n".join([page.get("content", "") for page in pdf.pages or []])

                        # fmt: off
                        # Some postprocessing that was necessary after eyeballing documents
                        text = (
                            text
                            .strip()                                                      # remove leading/trailing spaces
                            .replace("\x02", "")                                          # hyphens (line-breaks with -)
                            .replace("\x15", "").replace("\x16", "").replace("\x18", "")  # showed up when bold face Drucksache Nummer could not be extracted
                        )
                        # fmt: on

                        if len(text) == 0:
                            # TODO: Use OCR as fallback
                            msg = f"[{vorgang.id} - {dokument.id}]: No text extracted."
                            logger.warning(msg)

                        elif magic.from_buffer(text, mime=True) != "text/plain":
                            error_file = self.get_errors_dir() / f"{dokument.id}.text"
                            error_file.write_text(text)

                            # NOTE: This is a hack, where the mime type of the saved file gets 'text/plain', which is causing issues
                            if magic.from_file(error_file, mime=True) == "text/plain":
                                error_file.rename(dokument_text_file)

                            else:
                                msg = f"[{vorgang.id} - {dokument.id}]: Extracted text is not plain text."
                                logger.warning(msg)

                        else:
                            dokument_text_file.write_text(text)

        return vorgang
