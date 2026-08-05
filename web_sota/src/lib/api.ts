// Backend port (10748) — NOT the Vite dev port (10749). The Vite proxy only
// covers /api in dev; prod/Tauri builds must talk to the backend directly.
// The backend serves CORS allow_origins=["*"] so direct browser calls work.
export const API_BASE = "http://127.0.0.1:10748";
