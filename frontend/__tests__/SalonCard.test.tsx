import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SalonCard } from "@/components/SalonCard";
import type { SalonSummary } from "@/lib/types";

const salon: SalonSummary = {
  id: 7,
  name: "Studio Aurora",
  district: "Mokotów",
  rating: 4.8,
  review_count: 210,
  price_range: "$$",
  services: [
    { id: 1, slug: "hair-coloring", name: "Hair coloring", category: "hair" },
    { id: 2, slug: "balayage-highlights", name: "Balayage & highlights", category: "hair" },
    { id: 3, slug: "manicure", name: "Manicure", category: "nails" },
    { id: 4, slug: "pedicure", name: "Pedicure", category: "nails" },
    { id: 5, slug: "facial", name: "Facial treatment", category: "spa" },
  ],
};

describe("SalonCard", () => {
  it("renders key info and links to the detail page", () => {
    render(<SalonCard salon={salon} />);

    expect(screen.getByRole("heading", { name: "Studio Aurora" })).toBeInTheDocument();
    expect(screen.getByText("Mokotów")).toBeInTheDocument();
    expect(screen.getByText("$$")).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute("href", "/salons/7");
  });

  it("limits service tags and shows an overflow indicator", () => {
    render(<SalonCard salon={salon} />);
    // 5 services, max 4 shown -> "+1" overflow pill.
    expect(screen.getByText("+1")).toBeInTheDocument();
  });
});
