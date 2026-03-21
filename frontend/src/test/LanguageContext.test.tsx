import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { LanguageProvider } from "../contexts/LanguageContext";

describe("LanguageContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should render LanguageProvider without crashing", () => {
    const { container } = render(
      <LanguageProvider>
        <div data-testid="child">Hello</div>
      </LanguageProvider>
    );
    expect(screen.getByTestId("child")).toBeTruthy();
  });

  it("should wrap children correctly", () => {
    render(
      <LanguageProvider>
        <span data-testid="inner">Content</span>
      </LanguageProvider>
    );
    expect(screen.getByTestId("inner").textContent).toBe("Content");
  });
});
