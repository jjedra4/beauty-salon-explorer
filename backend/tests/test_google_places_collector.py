"""Unit tests for the Google Places collector.

The HTTP layer is mocked with ``httpx.MockTransport`` and recorded-style
fixtures, so these tests run offline and never hit the network or need a key.
They verify field mapping, pagination, within-run dedup, and the retry policy.
"""

import json

import httpx

from pipeline.collectors.google_places import GooglePlacesCollector, _is_retryable
from pipeline.collectors.warsaw_districts import DistrictCentroid


def _place(place_id: str, name: str) -> dict:
    """A representative Places API place object."""
    return {
        "id": place_id,
        "displayName": {"text": name},
        "formattedAddress": "ul. Testowa 1, Warszawa",
        "location": {"latitude": 52.23, "longitude": 21.01},
        "rating": 4.6,
        "userRatingCount": 132,
        "priceLevel": "PRICE_LEVEL_MODERATE",
        "types": ["hair_salon", "beauty_salon"],
        "nationalPhoneNumber": "+48 22 123 45 67",
        "websiteUri": "https://example.pl",
        "reviews": [{"text": {"text": "Great cut!"}}, {"text": {"text": "Friendly staff."}}],
        "editorialSummary": {"text": "Cosy neighbourhood hair studio."},
    }


def _single_district_collector(handler) -> GooglePlacesCollector:
    """A collector scoped to one district/query, wired to a mock transport."""
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return GooglePlacesCollector(
        api_key="test-key",
        client=client,
        districts=(DistrictCentroid("Mokotów", 52.19, 21.03),),
        queries=("fryzjer",),
        max_pages=2,
        sleep=lambda _seconds: None,  # no real delays in tests
    )


def test_parses_fields_and_paginates_and_dedupes() -> None:
    # Page 1 returns A and B with a next-page token; page 2 returns B (dup) + C.
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        if "pageToken" not in body:
            return httpx.Response(
                200,
                json={"places": [_place("A", "Alpha"), _place("B", "Beta")],
                      "nextPageToken": "tok"},
            )
        return httpx.Response(200, json={"places": [_place("B", "Beta"), _place("C", "Gamma")]})

    salons = list(_single_district_collector(handler).collect())

    # B is deduplicated across pages -> A, B, C.
    assert [s.source_id for s in salons] == ["A", "B", "C"]

    alpha = salons[0]
    assert alpha.name == "Alpha"
    assert alpha.address == "ul. Testowa 1, Warszawa"
    assert alpha.rating == 4.6
    assert alpha.review_count == 132
    assert alpha.price_level == "PRICE_LEVEL_MODERATE"
    assert alpha.phone == "+48 22 123 45 67"
    assert alpha.website == "https://example.pl"
    assert alpha.reviews == ["Great cut!", "Friendly staff."]
    assert alpha.types == ["hair_salon", "beauty_salon"]
    assert alpha.raw_services_text == "Cosy neighbourhood hair studio."
    assert alpha.district_hint == "Mokotów"
    assert alpha.source == "google_places"


def test_empty_results_yield_nothing() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    assert list(_single_district_collector(handler).collect()) == []


def test_falls_back_to_types_when_no_editorial_summary() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        place = _place("A", "Alpha")
        del place["editorialSummary"]
        return httpx.Response(200, json={"places": [place]})

    salon = next(iter(_single_district_collector(handler).collect()))
    assert salon.raw_services_text == "hair_salon beauty_salon"


def test_is_retryable_classifies_errors() -> None:
    request = httpx.Request("POST", "https://example.com")

    def status_error(code: int) -> httpx.HTTPStatusError:
        return httpx.HTTPStatusError(
            "err", request=request, response=httpx.Response(code, request=request)
        )

    assert _is_retryable(status_error(429)) is True
    assert _is_retryable(status_error(503)) is True
    assert _is_retryable(status_error(400)) is False
    assert _is_retryable(httpx.ConnectError("boom", request=request)) is True
    assert _is_retryable(ValueError("unrelated")) is False
