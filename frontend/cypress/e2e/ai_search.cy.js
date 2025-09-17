describe("AI Search", () => {
  it("runs a query and shows results", () => {
    cy.visit("http://localhost:3000");
    cy.get("input[placeholder*='Ask FinOps AI']").type("top services{enter}");
    cy.contains("Top 5 services").should("exist");
  });
});
