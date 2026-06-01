import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Pagination } from "@/components/Pagination";

describe("Pagination", () => {
  it("renders nothing when all results fit on one page", () => {
    const { container } = render(
      <Pagination total={5} limit={12} offset={0} onChange={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("disables Previous on the first page and advances on Next", async () => {
    const onChange = vi.fn();
    render(<Pagination total={30} limit={12} offset={0} onChange={onChange} />);

    expect(screen.getByRole("button", { name: /Prev/ })).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: /Next/ }));
    expect(onChange).toHaveBeenCalledWith(12);
  });
});
