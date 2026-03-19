from pathlib import Path
from typing import Self

from scrapy.crawler import Crawler

from scraper_BE.pardok import AnyGesetzDokument, GesetzVorgang


class CacheDirPipeline:
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler=crawler)

    def __init__(self: Self, crawler: Crawler) -> None:
        self.crawler = crawler

        self.wahlperiode = self.crawler.settings.getint("WAHLPERIODE")
        self.cache_dir = Path(self.crawler.settings.get("CACHE_DIR")) / str(self.wahlperiode)

    def get_vorgang_cache_dir(self: Self, vorgang: GesetzVorgang) -> Path:
        return self.cache_dir / "vorgaenge" / vorgang.id

    def get_dokument_cache_dir(self: Self, dokument: AnyGesetzDokument) -> Path:
        return self.get_vorgang_cache_dir(dokument.vorgang) / "dokumente" / dokument.id
