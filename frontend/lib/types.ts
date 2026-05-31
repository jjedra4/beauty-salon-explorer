/**
 * TypeScript types mirroring the backend's API schemas (see the OpenAPI doc at
 * `/openapi.json`). Kept in one place as the single source of truth for the
 * shapes the client consumes.
 */

export interface Service {
  id: number;
  slug: string;
  name: string;
  category: string;
}

export interface SalonSummary {
  id: number;
  name: string;
  district: string;
  rating: number | null;
  review_count: number | null;
  price_range: string | null;
  services: Service[];
}

export interface SalonDetail extends SalonSummary {
  address: string;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  website: string | null;
  review_summary: string | null;
}

export interface PaginatedSalons {
  items: SalonSummary[];
  total: number;
  limit: number;
  offset: number;
}

export type SearchMode = "semantic" | "keyword";

export interface SalonSearchResult extends SalonSummary {
  score: number;
}

export interface SearchResponse {
  query: string;
  mode: SearchMode;
  items: SalonSearchResult[];
}

/** Partial update payload for `PATCH /salons/{id}`. */
export interface SalonUpdate {
  name?: string;
  address?: string;
  district?: string;
  phone?: string | null;
  website?: string | null;
  price_range?: string | null;
  rating?: number | null;
  review_summary?: string | null;
  service_slugs?: string[];
}

/** Filters applied to the listing endpoint. */
export interface SalonListParams {
  district?: string;
  service?: string;
  limit?: number;
  offset?: number;
}
