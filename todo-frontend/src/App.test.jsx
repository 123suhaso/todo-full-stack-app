import { render, screen } from "@testing-library/react";
import App from "./App";

describe("Todo App", () => {
  it("renders app title", () => {
    render(<App />);
    expect(screen.getByText(/Todo List/i)).toBeInTheDocument();
  });
});
