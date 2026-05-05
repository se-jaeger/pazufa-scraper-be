import logging
from http import HTTPStatus
from typing import Self

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.http.request import NO_CALLBACK

from pazufa_scraper_be.pardok import GesetzVorgang
from pazufa_scraper_be.pipelines._base import BasePipeline

logger = logging.getLogger(__name__)


class RemoveBrokenUrl(BasePipeline):
    def init(self) -> None: ...

    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        new_dokumente = []
        for dokument in vorgang.dokumente:
            url = str(dokument.lok_url)
            request = Request(url, method="HEAD", callback=NO_CALLBACK)
            response = await self.crawler.engine.download_async(request)  # ty:ignore[unresolved-attribute]
            if response.status == HTTPStatus.OK:
                new_dokumente.append(dokument)

        vorgang.dokumente = new_dokumente
        return vorgang
