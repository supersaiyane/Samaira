import axiosClient from "./axiosClient";

export const getAccounts = () => axiosClient.get("/accounts");
export const getServices = () => axiosClient.get("/services");
export const getInsightsSummary = () => axiosClient.get("/insights/summary");
export const getSavingsSummary = () => axiosClient.get("/savings/summary");
export const getRecommendations = () => axiosClient.get("/recommendations");
export const getAnomalies = () => axiosClient.get("/anomalies");
export const getForecasts = () => axiosClient.get("/forecasts");
export const getBudgets = () => axiosClient.get("/budgets");
export const queryAI = (query) => axiosClient.post("/ai/query", { query });
