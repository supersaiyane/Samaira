import axiosClient from "./axiosClient";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

export const getAccounts = () => axiosClient.get("/accounts");
export const getServices = () => axiosClient.get("/services");
export const getInsightsSummary = () => axiosClient.get("/insights/summary");
export const getSavingsSummary = () => axiosClient.get("/savings/summary");
export const getRecommendations = () => axiosClient.get("/recommendations");
export const getAnomalies = () => axiosClient.get("/anomalies");
export const getForecasts = () => axiosClient.get("/forecasts");
export const getBudgets = () => axiosClient.get("/budgets");
export const queryAI = (query) => axiosClient.post("/ai/query", { query });

export const getAnomaliesCount = () => axios.get(`${API_BASE}/metrics/anomalies/count`);
export const getSavingsTotal = () => axios.get(`${API_BASE}/metrics/savings/total`);
export const getBudgetBreaches = () => axios.get(`${API_BASE}/metrics/budgets/breaches`);
export const getClustersCount = () => axios.get(`${API_BASE}/metrics/clusters/count`);
export const getIdleEC2Count = () => axios.get(`${API_BASE}/metrics/ec2/idle`);
