import logging
from typing import Self

import kreuzberg
import magic
from scrapy.exceptions import DropItem

from pazufa_scraper_be.pardok import GesetzVorgang
from pazufa_scraper_be.pipelines._base import CacheDirPipeline, StatsPipeline
from pazufa_scraper_be.pipelines.stats_counter import TextCounter

logger = logging.getLogger(__name__)


class ExtractTextFromPDF(CacheDirPipeline, StatsPipeline):
    """Pipeline that extracts plain text from cached PDF documents using kreuzberg."""

    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        """Extract text from cached PDFs for each document in the Vorgang."""
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            for dokument_url in dokument.all_urls:
                document_cache = self.get_document_cache(document=dokument, document_url=dokument_url)

                if document_cache.document_file.exists():
                    if document_cache.text_file.exists():
                        self.increment_stats(TextCounter.CACHE_HIT)
                        continue

                    self.increment_stats(TextCounter.CACHE_MISS)
                    pdf = await kreuzberg.extract_file(
                        document_cache.document_file,
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
                        # TODO(se-jaeger): Use OCR as fallback
                        self.increment_stats(TextCounter.EXTRACT_FAILED_EMPTY_TEXT)
                        msg = f"[{vorgang.id} - {dokument.id}]: No text extracted."
                        logger.warning(msg)

                    elif magic.from_buffer(text, mime=True) != "text/plain":
                        error_file = self.get_errors_dir() / f"{dokument.id}.text"
                        error_file.write_text(text)

                        # NOTE: This is a hack, where the mime type of the saved file gets 'text/plain', which is causing issues
                        if magic.from_file(error_file, mime=True) == "text/plain":
                            error_file.rename(document_cache.text_file)

                        else:
                            self.increment_stats(TextCounter.EXTRACT_FAILED_NOT_PLAIN_TEXT)
                            msg = f"[{vorgang.id} - {dokument.id}]: Extracted text is not plain text."
                            logger.warning(msg)

                    else:
                        self.increment_stats(TextCounter.EXTRACT_DONE)
                        document_cache.text_file.write_text(text)

        return vorgang
