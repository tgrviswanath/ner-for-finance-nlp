import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL });

export const extractEntities = (text) => api.post("/api/v1/extract", { text });
export const extractBatch    = (texts) => api.post("/api/v1/extract/batch", { texts });
