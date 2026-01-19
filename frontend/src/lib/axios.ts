import axios from "axios";

const defaultBaseURL = "http://127.0.0.1:8000/api";
const baseURL = (process.env.NEXT_PUBLIC_API_BASE_URL || defaultBaseURL).replace(/\/+$/, "");

const api = axios.create({
  baseURL,
  timeout: 10000,
  // Some CDNs/proxies may respond with 304 (Not Modified). Axios treats 304 as an
  // error by default because it's not in the 2xx range.
  validateStatus: status => (status >= 200 && status < 300) || status === 304,
});

// Prevent conditional caching issues in production by cache-busting GET requests.
api.interceptors.request.use(config => {
  if ((config.method || "").toLowerCase() === "get") {
    config.params = { ...(config.params || {}), _ts: Date.now() };
  }
  return config;
});

export default api;
