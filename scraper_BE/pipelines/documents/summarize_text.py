import logging
from typing import Self

import magic
from scrapy.exceptions import DropItem

from scraper_BE.constants import SUMMARY_FILE_NAME, TEXT_FILE_NAME
from scraper_BE.pardok import GesetzVorgang
from scraper_BE.pipelines._base import CacheDirPipeline

logger = logging.getLogger(__name__)


class SummarizeExtractedPDFText(CacheDirPipeline):
    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            for dokument_url in dokument.all_urls:
                if dokument_dir := self.get_dokument_cache_dir(dokument=dokument, url=dokument_url):
                    dokument_text_file = dokument_dir / TEXT_FILE_NAME
                    dokument_summary_file = dokument_dir / SUMMARY_FILE_NAME

                    if dokument_text_file.exists() and not dokument_summary_file.exists():
                        # TODO: here we ask a LLM to get the summary
                        summary = "TODO: summary coming soon!"

                        if len(summary) == 0:
                            msg = f"[{vorgang.id} - {dokument.id}]: Summary is empty!"
                            logger.warning(msg)

                        elif magic.from_buffer(summary, mime=True) != "text/plain":
                            error_file = self.get_errors_dir() / f"{dokument.id}.summary"
                            error_file.write_text(summary)

                            msg = f"[{vorgang.id} - {dokument.id}]: Summary is not plain text!"
                            logger.warning(msg)

                        else:
                            dokument_summary_file.write_text(summary)

        return vorgang
