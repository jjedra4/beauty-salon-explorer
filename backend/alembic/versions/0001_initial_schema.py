"""Initial schema: extensions, services, salons, association, indexes.

Revision ID: 0001
Revises:
Create Date: 2026-05-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op
from app.core.constants import EMBEDDING_DIM

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Extensions: pgvector for embeddings, pg_trgm for the keyword search
    # fallback (trigram similarity / fast ILIKE).
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_services_slug", "services", ["slug"], unique=True)
    op.create_index("ix_services_category", "services", ["category"])

    op.create_table(
        "salons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=512), nullable=False),
        sa.Column("district", sa.String(length=64), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("website", sa.String(length=512), nullable=True),
        sa.Column("price_range", sa.String(length=8), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("raw_services_text", sa.Text(), nullable=True),
        sa.Column("review_summary", sa.Text(), nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source", "source_id", name="uq_salon_source"),
    )
    op.create_index("ix_salons_name", "salons", ["name"])
    op.create_index("ix_salons_district", "salons", ["district"])
    op.create_index("ix_salons_source", "salons", ["source"])

    # Trigram index on name for the keyword search fallback (M5).
    op.execute("CREATE INDEX ix_salons_name_trgm ON salons USING gin (name gin_trgm_ops)")
    # HNSW index for cosine-distance vector search (M5).
    op.execute(
        "CREATE INDEX ix_salons_embedding_hnsw ON salons "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "salon_services",
        sa.Column("salon_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["salon_id"], ["salons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("salon_id", "service_id"),
    )


def downgrade() -> None:
    op.drop_table("salon_services")
    op.drop_index("ix_salons_embedding_hnsw", table_name="salons")
    op.drop_index("ix_salons_name_trgm", table_name="salons")
    op.drop_index("ix_salons_source", table_name="salons")
    op.drop_index("ix_salons_district", table_name="salons")
    op.drop_index("ix_salons_name", table_name="salons")
    op.drop_table("salons")
    op.drop_index("ix_services_category", table_name="services")
    op.drop_index("ix_services_slug", table_name="services")
    op.drop_table("services")
