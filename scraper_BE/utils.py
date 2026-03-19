import uuid
from enum import Enum

from scraper_BE.settings import SCRAPER_UUID


class UUID_Generator(Enum):
    VORGANG = uuid.uuid5(SCRAPER_UUID, "VORGANG")
    DOKUMENT = uuid.uuid5(SCRAPER_UUID, "DOKUMENT")

    def generate(self, name: str) -> str:
        """Generate a UUID5 using this namespace and the provided name."""
        return str(uuid.uuid5(self.value, name))
