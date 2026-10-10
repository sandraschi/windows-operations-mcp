// Backend port (10748) — NOT the Vite dev port (10749). The Vite proxy only
// covers /api in dev; prod/Tauri builds must talk to the backend directly.
// The backend allows the Tauri origins plus Tailscale/LAN via an explicit
// allowlist + origin regex (see src/windows_operations_mcp/server.py).
export const API_BASE = "http://127.0.0.1:10748";
