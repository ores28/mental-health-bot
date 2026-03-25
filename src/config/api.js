// Centralized API and endpoint configuration

export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const ASR_WS_URL = import.meta.env.VITE_ASR_WS_URL || "ws://localhost:9000/ws/asr";

export const ENDPOINTS = {
  CHAT: "/api/chat",
  REGISTER: "/register",
  LOGIN: "/login",
  HISTORY: "/api/conversations",
  SUMMARY: "/api/summary",
  HEALTH: "/health",
  HISTORY_ITEMS: "/history",
  TTS: "/api/tts"
};
