import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RatingStars } from "@/components/RatingStars";

describe("RatingStars", () => {
  it("shows the rating and review count", () => {
    render(<RatingStars rating={4.65} reviewCount={132} />);
    expect(screen.getByText("4.7")).toBeInTheDocument();
    expect(screen.getByText("(132)")).toBeInTheDocument();
  });

  it("shows a placeholder when there is no rating", () => {
    render(<RatingStars rating={null} reviewCount={null} />);
    expect(screen.getByText("No rating")).toBeInTheDocument();
  });
});
