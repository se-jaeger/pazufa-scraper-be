import uuid
from enum import Enum

from scraper_BE.settings import SCRAPER_UUID


class BE_UUID_Generator(Enum):
    VORGANG = uuid.uuid5(SCRAPER_UUID, "VORGANG")

    def generate(self, name: str) -> uuid.UUID:
        """Generate a UUID5 using this namespace and the provided name."""
        return uuid.uuid5(self.value, name)

    def __str__(self):
        return self.name
