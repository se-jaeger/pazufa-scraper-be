import logging
from http import HTTPStatus
from typing import Self

from pazufa_corelib.api_client import AuthenticatedClient
from pazufa_corelib.api_client.api.vorgang import vorgang_put
from pazufa_corelib.api_client.models.vorgang import Vorgang
from scrapy.exceptions import DropItem

from pazufa_scraper_be.pipelines._base import ApiPipeline

logger = logging.getLogger(__name__)


class SubmitVorgang(ApiPipeline):
    async def process_item(self: Self, pazufa_vorgang: Vorgang) -> None:
        if not self.api_submit:
            return

        if not isinstance(pazufa_vorgang, Vorgang):
            msg = f"Expected {Vorgang.__name__} object but got {pazufa_vorgang.__class__.__name__}."
            raise DropItem(msg)

        client = AuthenticatedClient(base_url=self.api_base_url, token=self.api_token, prefix="", auth_header_name="X-API-Key")

        async with client:
            response = await vorgang_put.asyncio_detailed(client=client, body=pazufa_vorgang, x_scraper_id=str(self.scraper_uuid))

        if response.status_code != HTTPStatus.CREATED:
            id_ = pazufa_vorgang.ids[0].id if pazufa_vorgang.ids else pazufa_vorgang.api_id
            url_part = f"URL: {pazufa_vorgang.links[0]} " if pazufa_vorgang.links else ""

            msg = f"[{id_}]: Got {response.status_code} status code when submitting to PaZuFa API. {url_part}Response: {response.content.decode('utf-8')}"
            logger.warning(msg)
