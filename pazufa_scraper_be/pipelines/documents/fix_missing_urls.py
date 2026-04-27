import logging
from http import HTTPStatus
from typing import Self

from pydantic import HttpUrl
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.http.request import NO_CALLBACK

from pazufa_scraper_be.constants import DOK_BASE_URL
from pazufa_scraper_be.pardok import GesetzVorgang, PlPrDokument
from pazufa_scraper_be.pipelines._base import BasePipeline

logger = logging.getLogger(__name__)


class FixMissingDokUrl(BasePipeline):
    def init(self) -> None: ...

    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            if isinstance(dokument, PlPrDokument) and dokument.lok_url is None and (dokument_nr := dokument.nr.split("/")[1]):
                for abbr in ("bp", "ip", "wp"):
                    url = f"{DOK_BASE_URL}/{self.wahlperiode}/PlenarPr/p{self.wahlperiode}-{int(dokument_nr):03d}-{abbr}.pdf"

                    request = Request(url, method="HEAD", callback=NO_CALLBACK)
                    response = await self.crawler.engine.download_async(request)  # ty:ignore[unresolved-attribute]
                    if response.status == HTTPStatus.OK:
                        dokument.lok_url = HttpUrl(url)
                        break

            # TODO: Similarly could work for Ausschussprotokolle but those are trickier due to their URL containing abbreviation of Ausschussname

        return vorgang
