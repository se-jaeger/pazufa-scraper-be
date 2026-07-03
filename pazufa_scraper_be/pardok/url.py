import asyncio
from dataclasses import dataclass
from http import HTTPStatus
from typing import Self

from pydantic import HttpUrl
from scrapy import Request
from scrapy.core.engine import ExecutionEngine
from scrapy.http.request import NO_CALLBACK

from pazufa_scraper_be.constants import DOK_BASE_URL
from pazufa_scraper_be.pardok import AnyGesetzDokument
from pazufa_scraper_be.pardok.dokument import AusschussprotokollTyp


def build_plenarprotokoll_url(wahlperiode: int, dokument_nr: str) -> HttpUrl | None:
    """Build a PlPr LokURL from a DokNr like "19/2" → p19-002-wp.pdf.

    Returns None if DokNr has no numeric second segment.
    """
    parts = dokument_nr.split("/")
    n_parts = 2
    if len(parts) < n_parts or not parts[1].isdigit():
        return None

    nr = int(parts[1])
    # TODO(se-jaeger): is the suffix 'bp' from AusschussprotokollTyp.Beschluss really the one we want to use here or a bug?
    # (The suffix was kept from before the refactor, so a persisting aspect)
    url = f"{DOK_BASE_URL}/{wahlperiode}/PlenarPr/p{wahlperiode}-{nr:03d}-{AusschussprotokollTyp.Beschluss}.pdf"

    return HttpUrl(url)


def build_ausschussprotokoll_variant_url(url: HttpUrl, typ: AusschussprotokollTyp) -> HttpUrl:
    """Return the URL for a specific APr variant by swapping the trailing-typ segment.

    Robust to non-3-digit numbering (ParlKBB19-001) and arbitrary abbrpaths;
    only assumes the variant is the segment after the final '-' before .pdf.
    """
    if url.path is None:
        msg = f"{url=} should contain the path to a file but lacks any path."
        raise ValueError(msg)

    stem, dot, ext = url.path.rpartition(".")
    base_stem, sep, _old = stem.rpartition("-")
    if not sep or dot != "." or ext != "pdf":
        msg = f"Cannot derive APr variant from {url=}"
        raise ValueError(msg)

    new_path = f"{base_stem}-{typ}{dot}{ext}"
    return HttpUrl(str(url).replace(url.path, new_path))


@dataclass
class UrlResolution:
    """Data container summarizing resolve_dokument_urls outcome."""

    primary_was_reachable: bool
    recovered_from: HttpUrl | None
    pruned: list[HttpUrl]

    @property
    def missing_primary(self: Self) -> bool:
        """Denotes weather primary URL is missing."""
        return not self.primary_was_reachable and self.recovered_from is None


async def url_is_reachable(engine: ExecutionEngine, url: HttpUrl) -> bool:
    """HEAD-check a URL; treats non-OK or exceptions as unreachable."""
    request = Request(str(url), method="HEAD", callback=NO_CALLBACK)
    try:
        response = await engine.download_async(request)

    except Exception:  # noqa: BLE001
        return False

    return response.status == HTTPStatus.OK


async def resolve_document_urls(dokument: AnyGesetzDokument, engine: ExecutionEngine) -> UrlResolution:
    """Single pass: probe primary once, probe each additional once, then mutate."""
    additional_urls = dokument.additional_urls or []

    primary_ok = await url_is_reachable(engine, dokument.lok_url)
    additional_ok = await asyncio.gather(*(url_is_reachable(engine, u) for u in additional_urls))

    reachable, pruned = [], []
    for url, ok in zip(additional_urls, additional_ok, strict=True):
        if ok:
            reachable.append(url)

        else:
            pruned.append(url)

    recovered_from = None
    if not primary_ok and reachable:
        recovered_from = reachable.pop(0)
        dokument.lok_url = recovered_from

    dokument.additional_urls = reachable or None
    return UrlResolution(
        primary_was_reachable=primary_ok,
        recovered_from=recovered_from,
        pruned=pruned,
    )
