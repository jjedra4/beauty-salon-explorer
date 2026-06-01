"""Live smoke test against the real Google Places API (New).

Marked ``live`` and excluded from the default run / CI. Run explicitly with a
real key via ``make places-check``.

It performs a single, minimal search (one district × one query × one page ≈ one
billed request, a few cents) to verify that the key is valid, the **Places API
(New)** is enabled, the field mask is accepted, and our parsing produces a
populated :class:`RawSalon`.
"""

import pytest

from app.core.config import settings
from pipeline.collectors.google_places import GooglePlacesCollector
from pipeline.collectors.warsaw_districts import DistrictCentroid

pytestmark = pytest.mark.live


@pytest.fixture
def collector() -> GooglePlacesCollector:
    """A collector scoped to a single search, or skip if no key is set."""
    if not settings.google_maps_api_key:
        pytest.skip("GOOGLE_MAPS_API_KEY not set; skipping live Google Places check")
    # Minimal scope keeps the check to ~1 billed request.
    return GooglePlacesCollector(
        settings.google_maps_api_key,
        districts=(DistrictCentroid("Śródmieście", 52.2300, 21.0120),),
        queries=("fryzjer",),
        max_pages=1,
    )


def test_collect_returns_real_salons(collector: GooglePlacesCollector) -> None:
    salons = list(collector.collect())

    assert salons, "Expected at least one salon from Google Places"
    first = salons[0]
    assert first.source == "google_places"
    assert first.source_id, "Place id should be populated"
    assert first.name, "Salon name should be populated"
    assert first.district_hint == "Śródmieście"
    # A central-Warsaw 'fryzjer' search should yield addresses for most results.
    assert any(salon.address for salon in salons)
