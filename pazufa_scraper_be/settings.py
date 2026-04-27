# Scrapy settings for pazufa_scraper_be project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import uuid
from pathlib import Path

from pazufa_scraper_be.pipelines import (
    AddAdditionalUrls,
    BuildPaZuFaVorgang,
    DownloadAndCacheDocuments,
    ExtractTextFromPDF,
    FixMissingDokUrl,
    ReportAndDropErrors,
    SubmitVorgang,
    SummarizeExtractedPDFText,
)

# Custom Settings
LOG_LEVEL = "INFO"
SCRAPER_UUID = uuid.UUID("05dc56fc-24e1-442b-9f97-91d596d50471")
WAHLPERIODE = 19

CACHE_DIR = Path(".cache")
ERRORS_DIR = Path(".errors")

API_SUBMIT = bool(os.environ.get("PAZUFA_API_SUBMIT"))
API_BASE_URL = os.environ.get("PAZUFA_API_BASE_URL", "http://localhost:8080")
API_TOKEN = os.environ.get("PAZUFA_API_TOKEN", "tegernsee-apfelsaft-co2grenzwert")

# Scray Settings
BOT_NAME = "PaZuFa_Berlin_Scraper"

SPIDER_MODULES = ["pazufa_scraper_be.spiders"]
NEWSPIDER_MODULE = "pazufa_scraper_be.spiders"

ADDONS = {}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "pazufa_scraper_be (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # NOTE: this is not nice

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "pazufa_scraper_be.middlewares.ScraperBeSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "pazufa_scraper_be.middlewares.ScraperBeDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "pazufa_scraper_be.pipelines.ScraperBePipeline": 300,
# }
ITEM_PIPELINES = {
    # NOTE: Pipelines with <100 get proper items or dicts, which contain data an error.
    ReportAndDropErrors: 99,
    # NOTE: Pipelines with >= 100 only get properly parsed items.
    FixMissingDokUrl: 100,
    AddAdditionalUrls: 101,
    DownloadAndCacheDocuments: 110,
    ExtractTextFromPDF: 120,
    SummarizeExtractedPDFText: 130,
    BuildPaZuFaVorgang: 999,
    SubmitVorgang: 1000,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
