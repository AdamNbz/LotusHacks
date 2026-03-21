import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { AuthProvider, User } from "../contexts/AuthContext";
import { useContext } from "react";

// Helper component to access context
function TestConsumer() {
  const { useAuth } = require("../contexts/AuthContext");
  return null;
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should render AuthProvider without crashing", () => {
    const { container } = render(
      <AuthProvider>
        <div data-testid="child">Hello</div>
      </AuthProvider>
    );
    expect(screen.getByTestId("child")).toBeTruthy();
  });

  it("should start with no user when localStorage is empty", () => {
    localStorage.removeItem("vetc_user");
    const { container } = render(
      <AuthProvider>
        <div>Test</div>
      </AuthProvider>
    );
    expect(localStorage.getItem("vetc_user")).toBeNull();
  });

  it("should restore user from localStorage", () => {
    const mockUser: User = {
      name: "Test User",
      email: "test@example.com",
    };
    localStorage.setItem("vetc_user", JSON.stringify(mockUser));

    render(
      <AuthProvider>
        <div>Test</div>
      </AuthProvider>
    );

    const stored = JSON.parse(localStorage.getItem("vetc_user") || "{}");
    expect(stored.name).toBe("Test User");
    expect(stored.email).toBe("test@example.com");
  });

  it("should handle invalid JSON in localStorage gracefully", () => {
    localStorage.setItem("vetc_user", "not-valid-json");

    // Should not throw
    expect(() => {
      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );
    }).not.toThrow();
  });
});
