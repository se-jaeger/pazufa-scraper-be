import logging
from pathlib import Path
from typing import Self

from pydantic import HttpUrl

from pazufa_scraper_be.constants import (
    DOK_BASE_URL,
    DOK_CACHE_HISTORY_SUB_DIR_NAME,
    DOKUMENT_FILE_NAME,
    DOWNLOAD_TIME_FILE_NAME,
    FILE_BYTE_HASH_FILE_NAME,
    LAST_CHECKED_FILE_NAME,
    LAST_MODIFIED_FILE_NAME,
    SUMMARY_FILE_NAME,
    SUMMARY_IGNORE_FILE_NAME,
    TEXT_FILE_NAME,
    URL_FILE_NAME,
)
from pazufa_scraper_be.pardok import AnyGesetzDokument

logger = logging.getLogger(__name__)


class DocumentCache:
    """Container for document cache."""

    def __init__(self: Self, document: AnyGesetzDokument, document_url: HttpUrl, document_cache_dir: Path, wahlperiode: int) -> None:
        """Initialize DocumentCache and make sure directory exists."""
        if document_url != document.lok_url and document.additional_urls and document_url not in document.additional_urls:
            msg = f"[{document.vorgang.id} - {document.id}]: Did not setup dokument cache because given URL is unknown: {document_url}"
            raise ValueError(msg)

        # Document cache directory is Dokument URL without constant base, we replace 'Dok Art' part to be consistent
        # with rest of code base and drop the '.pdf' suffix in directory name.
        self.directory = (document_cache_dir / document.art).joinpath(
            *Path(str(document_url).removeprefix(f"{DOK_BASE_URL}/{wahlperiode}/")).with_suffix("").parts[1:]
        )
        self.history_directory = self.directory / DOK_CACHE_HISTORY_SUB_DIR_NAME
        self.document_file = self.directory / DOKUMENT_FILE_NAME
        self.url_file = self.directory / URL_FILE_NAME
        self.download_time_file = self.directory / DOWNLOAD_TIME_FILE_NAME
        self.last_modified_file = self.directory / LAST_MODIFIED_FILE_NAME
        self.last_checked_file = self.directory / LAST_CHECKED_FILE_NAME
        self.file_byte_hash_file = self.directory / FILE_BYTE_HASH_FILE_NAME
        self.text_file = self.directory / TEXT_FILE_NAME
        self.summary_file = self.directory / SUMMARY_FILE_NAME
        self.summary_ignore_file = self.directory / SUMMARY_IGNORE_FILE_NAME

        self.directory.mkdir(parents=True, exist_ok=True)

    def reset(self: Self) -> None:
        """Reset cache by moving all files into history directory."""
        history_dir = self.history_directory / self.last_modified_file.read_text()
        history_dir.mkdir(parents=True, exist_ok=True)

        for file in self.directory.iterdir():
            if file.is_file():
                file.rename(history_dir / file.name)
