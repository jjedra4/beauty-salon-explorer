"""End-to-end data pipeline CLI: collect → enrich → write seed.

Run with real API keys via ``make pipeline`` (or directly). This regenerates
the committed seed dataset from live Google Places data:

    python -m pipeline.run_pipeline                # collect + enrich
    python -m pipeline.run_pipeline --skip-collect  # re-enrich existing raw data

Requires ``OPENAI_API_KEY`` (enrichment) and, unless ``--skip-collect``,
``GOOGLE_MAPS_API_KEY`` (collection).
"""

import argparse

from app.ai import get_embedding_client, get_llm_client
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from pipeline.collectors.google_places import GooglePlacesCollector
from pipeline.enrichment.pipeline import enrich_salons
from pipeline.storage import read_raw_salons, write_enriched_salons, write_raw_salons

logger = get_logger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect and enrich Warsaw salon data.")
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Reuse previously collected raw data instead of calling Google Places.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of raw salons processed (useful for cheap test runs).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    configure_logging()

    llm = get_llm_client()
    embedder = get_embedding_client()
    if llm is None or embedder is None:
        raise SystemExit("OPENAI_API_KEY is required to run enrichment. Set it in .env.")

    if args.skip_collect:
        raw_salons = read_raw_salons()
        logger.info("Loaded %d raw salons from disk", len(raw_salons))
    else:
        if not settings.google_maps_api_key:
            raise SystemExit(
                "GOOGLE_MAPS_API_KEY is required to collect. "
                "Use --skip-collect to reuse existing raw data."
            )
        collector = GooglePlacesCollector(settings.google_maps_api_key)
        raw_salons = list(collector.collect())
        write_raw_salons(raw_salons)

    if args.limit:
        raw_salons = raw_salons[: args.limit]

    enriched = enrich_salons(raw_salons, llm=llm, embedder=embedder)
    written = write_enriched_salons(enriched)
    logger.info("Wrote %d enriched salons to the seed dataset", written)


if __name__ == "__main__":
    main()
