import axios from "axios";

const defaultBaseURL = "http://127.0.0.1:8000/api";
const baseURL = (process.env.NEXT_PUBLIC_API_BASE_URL || defaultBaseURL).replace(/\/+$/, "");

const api = axios.create({
  baseURL,
  timeout: 10000,
});

export default api;
