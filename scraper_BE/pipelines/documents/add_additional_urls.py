import logging
from http import HTTPStatus
from typing import Self

from pydantic import HttpUrl
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem
from scrapy.http.request import NO_CALLBACK

from scraper_BE.pardok import APrDokument, GesetzVorgang

logger = logging.getLogger(__name__)


class AddAdditionalUrls:
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler=crawler)

    def __init__(self: Self, crawler: Crawler) -> None:
        self.crawler = crawler

    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            # Ausschussprotokolle can have up to three documents: Beschlussprotokoll, Inhaltsprotokoll and Wortprotokoll.
            # The last two are optional but the pardok XML does not always serve the first one.
            # So we check which exit and add all to the list.
            if isinstance(dokument, APrDokument) and dokument.lok_url is not None:
                original_url = str(dokument.lok_url)
                dokument.lok_url = None

                for abbr in ("bp", "ip", "wp"):
                    url = original_url = original_url[:-6] + abbr + original_url[-4:]

                    request = Request(url, method="HEAD", callback=NO_CALLBACK)
                    response = await self.crawler.engine.download_async(request)  # ty:ignore[unresolved-attribute]
                    if response.status == HTTPStatus.OK:
                        http_url = HttpUrl(url)

                        # Using above priority, we set primary url and continue
                        if dokument.lok_url is None:
                            dokument.lok_url = http_url
                            continue

                        if dokument.additional_urls is None:
                            dokument.additional_urls = []

                        dokument.additional_urls.append(http_url)

        return vorgang
