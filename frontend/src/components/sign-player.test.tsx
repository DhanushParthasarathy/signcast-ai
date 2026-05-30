import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SignPlayer } from "@/components/sign-player";

describe("SignPlayer", () => {
  it("renders generated sign tokens", () => {
    render(
      <SignPlayer
        sequence={[
          { token: "NASA", clip_url: "/signs/nasa.mp4", status: "ready" },
          { token: "CLIMATE", clip_url: null, status: "missing" }
        ]}
      />
    );

    expect(screen.getByText("Sign Animation Player")).toBeInTheDocument();
    expect(screen.getByText("NASA")).toBeInTheDocument();
    expect(screen.getByText("CLIMATE")).toBeInTheDocument();
  });
});
