import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";
import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";

import { PromptSearch } from "@/components/PromptSearch";

// The bar navigates via the App Router; stub it so we can assert the URL.
vi.mock("next/navigation", () => ({ useRouter: vi.fn() }));

describe("PromptSearch", () => {
  const push = vi.fn();

  beforeEach(() => {
    push.mockClear();
    (useRouter as Mock).mockReturnValue({ push });
  });

  it("routes to the search page with the trimmed, encoded query", async () => {
    render(<PromptSearch size="hero" />);

    await userEvent.type(screen.getByRole("searchbox"), "  cheap barber in Mokotów  ");
    await userEvent.click(screen.getByRole("button", { name: "Ask" }));

    expect(push).toHaveBeenCalledWith("/search?q=cheap%20barber%20in%20Mokot%C3%B3w");
  });

  it("ignores an empty submission", async () => {
    render(<PromptSearch size="hero" />);
    await userEvent.click(screen.getByRole("button", { name: "Ask" }));
    expect(push).not.toHaveBeenCalled();
  });

  it("runs an example chip as a query", async () => {
    render(<PromptSearch size="hero" />);
    // The first quick chip mirrors the first example prompt.
    await userEvent.click(
      screen.getByRole("button", { name: "tani fryzjer na Mokotowie z dobrymi opiniami" }),
    );
    expect(push).toHaveBeenCalledWith(
      "/search?q=tani%20fryzjer%20na%20Mokotowie%20z%20dobrymi%20opiniami",
    );
  });
});
