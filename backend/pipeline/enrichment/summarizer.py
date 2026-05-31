"""Review summarization stage.

Condenses raw review snippets into a short, scannable summary (a one-line
"vibe" plus brief pros/cons) shown on the salon detail page. Returns ``None``
when there are no reviews, so the field is honestly empty rather than invented.
"""

from app.ai.base import LLMClient
from app.core.logging import get_logger

logger = get_logger(__name__)

_MAX_REVIEWS = 10

_SYSTEM_PROMPT = (
    "You summarize customer reviews of a beauty/hair salon for a listings site. "
    "Write in English, 2-4 short lines: a one-line overall vibe, then brief "
    "Pros and Cons. Be specific and neutral; do not invent details not present "
    "in the reviews."
)


class ReviewSummarizer:
    """Summarizes a salon's reviews into a short blurb via the LLM."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def summarize(self, name: str, reviews: list[str]) -> str | None:
        """Return a short review summary, or ``None`` if there are no reviews."""
        if not reviews:
            return None
        joined = "\n".join(f"- {review}" for review in reviews[:_MAX_REVIEWS])
        summary = self._llm.complete(
            system=_SYSTEM_PROMPT,
            user=f"Salon: {name}\nReviews:\n{joined}",
        ).strip()
        return summary or None
