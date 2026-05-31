import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { SearchBar } from "@/components/SearchBar";

describe("SearchBar", () => {
  it("submits the trimmed query", async () => {
    const onSearch = vi.fn();
    render(<SearchBar initialQuery="" onSearch={onSearch} onClear={vi.fn()} />);

    await userEvent.type(screen.getByRole("searchbox"), "  cheap barber  ");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith("cheap barber");
  });

  it("shows a clear button only when there is an active query", () => {
    const { rerender } = render(
      <SearchBar initialQuery="" onSearch={vi.fn()} onClear={vi.fn()} />,
    );
    expect(screen.queryByRole("button", { name: "Clear" })).not.toBeInTheDocument();

    rerender(<SearchBar initialQuery="barber" onSearch={vi.fn()} onClear={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Clear" })).toBeInTheDocument();
  });
});
