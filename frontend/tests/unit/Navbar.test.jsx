import { render, fireEvent, screen } from "@testing-library/react";
import Navbar from "../../src/layouts/Navbar";
import { BrowserRouter } from "react-router-dom";

test("toggles dark mode", () => {
  render(
    <BrowserRouter>
      <Navbar />
    </BrowserRouter>
  );

  const toggleBtn = screen.getByRole("button");
  fireEvent.click(toggleBtn);
  expect(document.documentElement.classList.contains("dark")).toBe(true);
});
