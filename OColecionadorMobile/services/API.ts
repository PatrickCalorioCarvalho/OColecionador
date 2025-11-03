import axios from "axios";

const api = axios.create({
  baseURL: "https://louse-model-lioness.ngrok-free.app/api",
  timeout: 10000,
});

export default api;
