/**
 * Thin, typed client for the backend REST API.
 *
 * All requests run in the browser, so the base URL points at the host-exposed
 * backend port (`NEXT_PUBLIC_API_BASE_URL`). Every function throws `ApiError`
 * on a non-2xx response, surfacing the backend's `detail` message for the UI.
 */

import type {
  PaginatedSalons,
  SalonDetail,
  SalonListParams,
  SalonUpdate,
  SearchResponse,
  Service,
} from "@/lib/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Perform a JSON request and unwrap the response, throwing `ApiError` on failure. */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!response.ok) {
    const detail = await response
      .json()
      .then((body) => body?.detail)
      .catch(() => null);
    throw new ApiError(detail ?? `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export function listSalons(params: SalonListParams = {}): Promise<PaginatedSalons> {
  return request<PaginatedSalons>(`/salons${buildQuery({ ...params })}`);
}

export function getSalon(id: number): Promise<SalonDetail> {
  return request<SalonDetail>(`/salons/${id}`);
}

export function updateSalon(id: number, payload: SalonUpdate): Promise<SalonDetail> {
  return request<SalonDetail>(`/salons/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function searchSalons(query: string, limit = 24): Promise<SearchResponse> {
  return request<SearchResponse>(`/salons/search${buildQuery({ q: query, limit })}`);
}

export function getDistricts(): Promise<string[]> {
  return request<string[]>("/districts");
}

export function getServices(): Promise<Service[]> {
  return request<Service[]>("/services");
}
