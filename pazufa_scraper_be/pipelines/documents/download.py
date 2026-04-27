import hashlib
import logging
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Self

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.http import Response
from scrapy.http.request import NO_CALLBACK

from pazufa_scraper_be.constants import DOKUMENT_FILE_NAME, DOWNLOAD_TIME_FILE_NAME, FILE_BYTE_HASH_FILE_NAME, LAST_MODIFIED_FILE_NAME, URL_FILE_NAME
from pazufa_scraper_be.pardok import GesetzVorgang
from pazufa_scraper_be.pipelines._base import CacheDirPipeline

logger = logging.getLogger(__name__)


class DownloadAndCacheDocuments(CacheDirPipeline):
    async def process_item(self: Self, vorgang: GesetzVorgang) -> GesetzVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        for dokument in vorgang.dokumente:
            if dokument.wp != self.wahlperiode:
                msg = (
                    f"[{vorgang.id} - {dokument.id}]: Wahlperiode from scraping run ('{self.wahlperiode}') "
                    + f"differs from this document's metadata: '{dokument.wp}'"
                )
                logger.warning(msg)
                continue

            for dokument_url in dokument.all_urls:
                dokument_cache_dir = self.get_dokument_cache_dir(dokument=dokument, url=dokument_url)
                if dokument_cache_dir is None:
                    msg = f"[{vorgang.id} - {dokument.id}]: Did not get cache dir for additional URL: {dokument_url}"
                    logger.warning(msg)
                    continue

                dokument_file = dokument_cache_dir / DOKUMENT_FILE_NAME
                dokument_url_file = dokument_cache_dir / URL_FILE_NAME
                dokument_download_time_file = dokument_cache_dir / DOWNLOAD_TIME_FILE_NAME
                dokument_last_modified_file = dokument_cache_dir / LAST_MODIFIED_FILE_NAME
                dokument_file_byte_hash_file = dokument_cache_dir / FILE_BYTE_HASH_FILE_NAME

                if dokument_url and not dokument_file.exists():
                    download_time = datetime.now(tz=UTC)
                    request = Request(dokument_url.encoded_string(), callback=NO_CALLBACK)
                    response = await self.crawler.engine.download_async(request)  # ty:ignore[unresolved-attribute]

                    if not isinstance(response, Response):
                        msg = f"[{vorgang.id} - {dokument.id}]: Expected 'scrapy.Response' but got '{type(response)}'"

                        logger.warning(msg)
                        continue

                    if response.status != HTTPStatus.OK:
                        msg = f"[{vorgang.id} - {dokument.id}]: Got {response.status} status code for URL: {response.url}"

                        logger.warning(msg)
                        continue

                    if last_modified_header_as_byte := response.headers.get("Last-Modified"):
                        last_modified_as_iso = datetime.strptime(last_modified_header_as_byte.decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z").isoformat()
                        dokument_last_modified_file.write_text(last_modified_as_iso)

                    dokument_file_byte_hash = hashlib.sha256(response.body).hexdigest()
                    dokument_file_byte_hash_file.write_text(dokument_file_byte_hash)

                    dokument_url_file.write_text(response.url)
                    dokument_download_time_file.write_text(download_time.isoformat())
                    dokument_file.write_bytes(response.body)

                # NOTE: We can at least check check if the document was changed since we downloaded it
                # TODO: I think, however, this case might be a bit more complex than just wipe dir and re-download.
                # We should at least save the history.
                else:
                    # request = Request(url, method="HEAD", callback=NO_CALLBACK)
                    # response = await self.crawler.engine.download_async(request)  # ty:ignore[unresolved-attribute]
                    # if last_modified_header_as_byte := response.headers.get("Last-Modified"):
                    #     last_modified_header = datetime.strptime(last_modified_header_as_byte.decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z").isoformat()
                    #     download_tiem_cache = datetime.fromisoformat(dokument_download_time_file.read_text())

                    pass

        return vorgang
