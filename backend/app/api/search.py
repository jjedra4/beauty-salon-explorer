"""Natural-language search endpoint.

``GET /salons/search`` runs semantic search (LLM filter extraction + vector
ranking) when AI is configured, otherwise a keyword fallback. The route is
registered before ``/salons/{salon_id}`` so "search" is never parsed as an id.
"""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_search_service
from app.schemas.salon import SalonSummary
from app.schemas.search import SalonSearchResult, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["search"])


def _to_score(raw: float) -> float:
    """Clamp/round a relevance score for display.

    Both paths already produce a 0..1 score where higher is better — semantic
    is the service's blended relevance, keyword is trigram similarity.
    """
    return round(max(0.0, min(1.0, raw)), 4)


@router.get("/salons/search", response_model=SearchResponse, summary="Natural-language search")
def search_salons(
    q: str = Query(
        ...,
        min_length=1,
        description="Natural-language query, e.g. 'cheap barber in Mokotów with good reviews'.",
    ),
    limit: int = Query(20, ge=1, le=50, description="Maximum results."),
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Return salons ranked by relevance to a natural-language query."""
    outcome = service.search(q, limit)
    items = [
        SalonSearchResult(
            **SalonSummary.model_validate(salon).model_dump(),
            score=_to_score(raw_score),
        )
        for salon, raw_score in outcome.results
    ]
    return SearchResponse(query=q, mode=outcome.mode, items=items)
