from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

from pydantic import HttpUrl
from scrapy.crawler import Crawler
from scrapy.statscollectors import StatsCollector

from scraper_BE.constants import DOK_BASE_URL
from scraper_BE.pardok import AnyGesetzDokument


class BasePipeline(ABC):
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler=crawler)

    def __init__(self: Self, crawler: Crawler) -> None:
        self.crawler = crawler
        self.wahlperiode = self.crawler.settings.getint("WAHLPERIODE")

        if not self.wahlperiode:
            msg = "Missing WAHLPERIODE setting."
            raise ValueError(msg)

        self.init()

    @abstractmethod
    def init(self: Self) -> None: ...


class CacheDirPipeline(BasePipeline):
    def init(self: Self) -> None:
        self._cache_dir = Path(self.crawler.settings.get("CACHE_DIR")) / str(self.wahlperiode)
        self._errors_dir = Path(self.crawler.settings.get("ERRORS_DIR")) / str(self.wahlperiode)

        if not self._cache_dir:
            msg = "Missing CACHE_DIR setting."
            raise ValueError(msg)

        if not self._errors_dir:
            msg = "Missing ERRORS_DIR setting."
            raise ValueError(msg)

    def get_dokument_cache_dir(self: Self, dokument: AnyGesetzDokument, url: HttpUrl) -> Path | None:
        if url != dokument.lok_url and dokument.additional_urls and url not in dokument.additional_urls:
            return None

        # NOTE: cache dir is Dokument URL without constant base, we replace 'Dok Art' part to be consistent with rest of code base and drop the '.pdf' suffix in dir name.
        dokument_cache_dir = self._cache_dir / "dokument" / dokument.art
        dokument_cache_dir = dokument_cache_dir.joinpath(*Path(str(url).removeprefix(f"{DOK_BASE_URL}/{self.wahlperiode}/")).with_suffix("").parts[1:])

        dokument_cache_dir.mkdir(parents=True, exist_ok=True)
        return dokument_cache_dir

    def get_errors_dir(self: Self) -> Path:
        crawl_start_time = self.crawler.stats.get_value("start_time").strftime("%Y-%m-%dT%H:%M:%S") if isinstance(self.crawler.stats, StatsCollector) else ""
        errors_dir = self._errors_dir / crawl_start_time
        errors_dir.mkdir(parents=True, exist_ok=True)
        return errors_dir


class ApiPipeline(BasePipeline):
    def init(self: Self) -> None:
        self.api_submit = self.crawler.settings.getbool("API_SUBMIT")
        self.api_base_url = self.crawler.settings.get("API_BASE_URL")
        self.api_token = self.crawler.settings.get("API_TOKEN")
        self.scraper_uuid = self.crawler.settings.get("SCRAPER_UUID")

        if not self.api_base_url:
            msg = "Missing API_BASE_URL setting."
            raise ValueError(msg)

        if not self.api_token:
            msg = "Missing API_TOKEN setting."
            raise ValueError(msg)

        if not self.scraper_uuid:
            msg = "Missing SCRAPER_UUID setting."
            raise ValueError(msg)
