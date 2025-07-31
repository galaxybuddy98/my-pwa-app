// src/lib/axios.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 5000, // 5초 후 요청 취소
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;