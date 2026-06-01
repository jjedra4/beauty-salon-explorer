"""Live smoke tests against the real OpenAI API.

Marked ``live`` and **excluded from the default test run** (see
``addopts = -m 'not live'`` in pyproject) and from CI. Run explicitly, with a
real key configured, via ``make ai-check``.

The faked unit/integration suite verifies our *logic* but never touches OpenAI.
These few low-cost calls verify the other half: that the **configured models
actually work** through the app's real code paths — embeddings come back at the
expected dimension, structured outputs parse, and free-text completion returns
text. Run this once after changing ``OPENAI_CHAT_MODEL`` /
``OPENAI_EMBEDDING_MODEL``.
"""

import pytest

from app.ai import get_openai_client
from app.ai.openai_client import OpenAIClient
from app.ai.query_parser import QueryParser
from app.core.constants import EMBEDDING_DIM
from app.core.taxonomy import VALID_SERVICE_SLUGS
from pipeline.collectors.base import RawSalon
from pipeline.enrichment.normalizer import SalonNormalizer
from pipeline.enrichment.summarizer import ReviewSummarizer

pytestmark = pytest.mark.live

_VALID_PRICES = {None, "$", "$$", "$$$"}


@pytest.fixture
def client() -> OpenAIClient:
    """The configured OpenAI client, or skip if no key is set."""
    openai = get_openai_client()
    if openai is None:
        pytest.skip("OPENAI_API_KEY not set; skipping live OpenAI checks")
    return openai


def test_embeddings_match_db_dimension(client: OpenAIClient) -> None:
    """`.embed` works and returns vectors matching the DB column dimension.

    This is the highest-value check: a wrong embedding model would silently
    produce vectors that don't fit the ``Vector(1536)`` column.
    """
    vectors = client.embed(["women's haircut and balayage in Mokotów", "barber shop"])
    assert len(vectors) == 2
    assert all(len(vector) == EMBEDDING_DIM for vector in vectors)


def test_structured_output_query_parsing(client: OpenAIClient) -> None:
    """`.parse` (structured outputs) works through the real QueryParser."""
    filters = QueryParser(client).parse("tani fryzjer na Mokotowie z dobrymi opiniami")
    # We assert domain validity (guaranteed by our sanitization), not the
    # model's exact extraction — the point is that structured parsing works.
    assert all(slug in VALID_SERVICE_SLUGS for slug in filters.service_slugs)
    assert filters.price_range in _VALID_PRICES
    assert filters.min_rating is None or 0.0 <= filters.min_rating <= 5.0


def test_service_classification(client: OpenAIClient) -> None:
    """`.parse` classifies messy multilingual text into valid taxonomy slugs."""
    raw = RawSalon(
        source="live",
        source_id="x",
        name="Studio Koloru",
        raw_services_text="koloryzacja, baleyage, strzyżenie damskie, manicure hybrydowy",
    )
    result = SalonNormalizer(client).normalize(raw)
    assert result.service_slugs
    assert all(slug in VALID_SERVICE_SLUGS for slug in result.service_slugs)


def test_review_summary(client: OpenAIClient) -> None:
    """`.complete` returns a non-empty free-text summary."""
    summary = ReviewSummarizer(client).summarize(
        "Test Salon",
        ["Świetna obsługa i miła atmosfera.", "Great cut, friendly staff, a bit pricey."],
    )
    assert summary and isinstance(summary, str)
