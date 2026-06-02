"""Google Places API (New) collector.

Fans out a Text Search over every (district centroid × query term) pair, pages
through the results, and maps each place into a :class:`RawSalon`. A rich field
mask pulls contact info, ratings, types, and review snippets in the search
response itself, avoiding a second Place Details round-trip per result.

Why Google Places: it is an official, licensed source with the widest field
coverage and a reproducible query model — see ``docs/architecture.md``.
"""

import time
from collections.abc import Callable, Iterator
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.core.logging import get_logger
from pipeline.collectors.base import RawSalon, SalonCollector
from pipeline.collectors.warsaw_districts import (
    SEARCH_QUERIES,
    WARSAW_DISTRICT_CENTROIDS,
    DistrictCentroid,
)

logger = get_logger(__name__)

_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Fields requested from the API. Narrowing the mask keeps the response small
# and the per-request billing tier predictable.
_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        "places.types",
        "places.primaryType",
        "places.primaryTypeDisplayName",
        "places.businessStatus",
        "places.regularOpeningHours",
        "places.nationalPhoneNumber",
        "places.websiteUri",
        "places.reviews",
        "places.editorialSummary",
        "nextPageToken",
    ]
)

# HTTP statuses worth retrying (rate limiting + transient server errors).
_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


def _is_retryable(exc: BaseException) -> bool:
    """Return whether an exception should trigger a retry."""
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUSES
    return False


class GooglePlacesCollector(SalonCollector):
    """Collects Warsaw salons from the Google Places API (New)."""

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.Client | None = None,
        districts: tuple[DistrictCentroid, ...] = WARSAW_DISTRICT_CENTROIDS,
        queries: tuple[str, ...] = SEARCH_QUERIES,
        radius_m: float = 3000.0,
        max_pages: int = 2,
        request_delay_s: float = 0.2,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._api_key = api_key
        self._client = client or httpx.Client(timeout=20.0)
        self._districts = districts
        self._queries = queries
        self._radius_m = radius_m
        self._max_pages = max_pages
        self._request_delay_s = request_delay_s
        self._sleep = sleep

    @property
    def source_name(self) -> str:
        return "google_places"

    def collect(self) -> Iterator[RawSalon]:
        """Yield unique, operational salons across all district × query searches."""
        seen: set[str] = set()
        skipped_closed = 0
        for district in self._districts:
            for query in self._queries:
                for place in self._search_all_pages(query, district):
                    place_id = place.get("id")
                    if not place_id or place_id in seen:
                        continue
                    seen.add(place_id)
                    # Drop permanently-closed places — stale listings hurt data quality.
                    if place.get("businessStatus") == "CLOSED_PERMANENTLY":
                        skipped_closed += 1
                        continue
                    yield self._to_raw_salon(place, district.name)
        logger.info(
            "Collected %d unique places from Google Places (skipped %d closed)",
            len(seen) - skipped_closed,
            skipped_closed,
        )

    # ── HTTP ───────────────────────────────────────────────────────────────
    def _search_all_pages(self, query: str, district: DistrictCentroid) -> Iterator[dict[str, Any]]:
        """Yield places for one query, following pagination tokens."""
        page_token: str | None = None
        for page in range(self._max_pages):
            body = self._build_body(query, district, page_token)
            data = self._post(body)
            yield from data.get("places", [])

            page_token = data.get("nextPageToken")
            if not page_token:
                break
            # The next-page token needs a brief moment to become valid.
            self._sleep(self._request_delay_s + 1.0 if page == 0 else self._request_delay_s)

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        """POST a search request, retrying transient failures."""
        response = self._client.post(
            _SEARCH_URL,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self._api_key,
                "X-Goog-FieldMask": _FIELD_MASK,
            },
            json=body,
        )
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result

    def _build_body(
        self, query: str, district: DistrictCentroid, page_token: str | None
    ) -> dict[str, Any]:
        """Build the Text Search request body for a district-biased query."""
        body: dict[str, Any] = {
            "textQuery": f"{query} {district.name} Warszawa",
            "languageCode": "pl",
            "regionCode": "PL",
            "pageSize": 20,
            "locationBias": {
                "circle": {
                    "center": {"latitude": district.latitude, "longitude": district.longitude},
                    "radius": self._radius_m,
                }
            },
        }
        if page_token:
            body["pageToken"] = page_token
        return body

    # ── Parsing ──────────────────────────────────────────────────────────────
    def _to_raw_salon(self, place: dict[str, Any], district_hint: str) -> RawSalon:
        """Map a Places API place object into a :class:`RawSalon`."""
        reviews = [
            review["text"]["text"]
            for review in place.get("reviews", [])
            if review.get("text", {}).get("text")
        ]
        editorial = place.get("editorialSummary", {}).get("text")
        types = place.get("types", [])
        primary_type_display = place.get("primaryTypeDisplayName", {}).get("text")
        # Prefer the editorial blurb, then the human category label, then raw types.
        raw_services_text = editorial or primary_type_display or " ".join(types) or None
        location = place.get("location", {})

        return RawSalon(
            source=self.source_name,
            source_id=place["id"],
            name=place.get("displayName", {}).get("text", "Unknown"),
            address=place.get("formattedAddress"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            phone=place.get("nationalPhoneNumber"),
            website=place.get("websiteUri"),
            rating=place.get("rating"),
            review_count=place.get("userRatingCount"),
            price_level=place.get("priceLevel"),
            types=types,
            primary_type=place.get("primaryType"),
            primary_type_display=primary_type_display,
            business_status=place.get("businessStatus"),
            opening_hours=place.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
            reviews=reviews,
            raw_services_text=raw_services_text,
            district_hint=district_hint,
        )
