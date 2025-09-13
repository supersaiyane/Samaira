import axios from "axios";
import axiosClient from "../api/axiosClient";

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

export const queryAI = (queryTest) =>
  axiosClient.post("/ai/query", { query: queryTest });

export default axiosClient;
