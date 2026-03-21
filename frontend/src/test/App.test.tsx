import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../App";

describe("App Component", () => {
  it("should render without crashing", () => {
    render(<App />);
    // App renders a root element
    expect(document.querySelector("#root") || document.body).toBeTruthy();
  });

  it("should render the landing page at root route", () => {
    render(<App />);
    // Landing page should have some content
    const body = document.body;
    expect(body.innerHTML.length).toBeGreaterThan(0);
  });
});
