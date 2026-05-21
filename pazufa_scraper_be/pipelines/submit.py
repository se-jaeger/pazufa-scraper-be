import logging
from http import HTTPStatus
from typing import Self

from pazufa_corelib.api_client.models.vorgang import Vorgang
from scrapy.exceptions import DropItem

from pazufa_scraper_be.pipelines._base import ApiPipeline

logger = logging.getLogger(__name__)


class SubmitVorgang(ApiPipeline):
    """Pipeline that submits a built Vorgang to the PaZuFa API."""

    async def process_item(self: Self, vorgang: Vorgang) -> None:
        """Submit the Vorgang to the PaZuFa API via HTTP PUT."""
        if not isinstance(vorgang, Vorgang):
            msg = f"Expected {Vorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        response = await self.put_vorgang(vorgang)
        if response is None:
            return

        if response.status_code != HTTPStatus.CREATED:
            id_ = vorgang.ids[0].id if vorgang.ids else vorgang.api_id
            url_part = f"URL: {vorgang.links[0]} " if vorgang.links else ""

            msg = f"[{id_}]: Got {response.status_code} status code when submitting to PaZuFa API. {url_part}Response: {response.content.decode('utf-8')}"
            logger.warning(msg)
