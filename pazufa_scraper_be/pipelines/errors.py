from typing import Self

from scrapy.exceptions import DropItem

from pazufa_scraper_be.pardok import GesetzVorgang


class ReportAndDropErrors:
    """Pipeline that reports parse errors and drops malformed items."""

    def process_item(self: Self, item: dict | GesetzVorgang) -> GesetzVorgang:
        """Pass through valid GesetzVorgang items; raise DropItem for error dicts."""
        if isinstance(item, GesetzVorgang):
            return item

        if isinstance(item, dict):
            msg = f"Could not properly parse Vorgang '{item['dict']['VID']}', handling error and moving on."
            raise DropItem(msg)

        msg = "This should not happen."
        raise DropItem(msg)
