from typing import Self

from scrapy.exceptions import DropItem

from pazufa_scraper_be.pardok import GesetzVorgang


class ReportAndDropErrors:
    def process_item(self: Self, item: dict | GesetzVorgang) -> GesetzVorgang:
        if isinstance(item, GesetzVorgang):
            return item

        if isinstance(item, dict):
            msg = f"Could not properly parse Vorgang '{item['dict']['VID']}', handling error and moving on."
            raise DropItem(msg)

        msg = "This should not happen!"
        raise DropItem(msg)
