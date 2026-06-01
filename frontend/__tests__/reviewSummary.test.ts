import { describe, expect, it } from "vitest";

import { parseReviewSummary } from "@/lib/reviewSummary";

describe("parseReviewSummary", () => {
  it("splits the synthetic seed format (comma list) into vibe + pros + cons", () => {
    const { vibe, pros, cons } = parseReviewSummary(
      "Cosy nail bar. Pros: long-lasting hybrids, creative nail art, spotless tools. " +
        "Cons: limited parking nearby.",
    );
    expect(vibe).toBe("Cosy nail bar.");
    expect(pros).toEqual(["long-lasting hybrids", "creative nail art", "spotless tools"]);
    expect(cons).toEqual(["limited parking nearby"]);
  });

  it("handles markdown bold and semicolon-separated real-data summaries", () => {
    const { vibe, pros, cons } = parseReviewSummary(
      "Overall vibe: upbeat, professional barber. **Pros:** skilled barbers; great fades; " +
        "good hygiene **Cons:** cash only; small waiting area",
    );
    expect(vibe).toBe("upbeat, professional barber.");
    expect(pros).toEqual(["skilled barbers", "great fades", "good hygiene"]);
    expect(cons).toEqual(["cash only", "small waiting area"]);
  });

  it("falls back to plain prose when there are no Pros/Cons labels", () => {
    const { vibe, pros, cons } = parseReviewSummary("A small, low-crowd spot, convenient for errands.");
    expect(vibe).toBe("A small, low-crowd spot, convenient for errands.");
    expect(pros).toEqual([]);
    expect(cons).toEqual([]);
  });
});
