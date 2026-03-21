import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../contexts/AuthContext";
import { LanguageProvider } from "../contexts/LanguageContext";
import Navbar from "../components/landing/Navbar";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>{ui}</AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
}

describe("Navbar Component", () => {
  it("should render without crashing", () => {
    const { container } = renderWithProviders(<Navbar />);
    expect(container).toBeTruthy();
  });

  it("should contain navigation elements", () => {
    const { container } = renderWithProviders(<Navbar />);
    // Navbar should have at least one link or button
    const links = container.querySelectorAll("a, button");
    expect(links.length).toBeGreaterThan(0);
  });
});
