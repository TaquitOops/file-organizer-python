# ─────────────────────────────────────
# config.py — Constantes globales
# ─────────────────────────────────────

# ── Paleta de colores ────────────────
BG       = "#0f1117"
SURFACE  = "#1a1d27"
SURFACE2 = "#22263a"
ACCENT   = "#5b8dee"
ACCENT2  = "#3f6bcc"
GREEN    = "#3ecf8e"
RED      = "#ff5c6c"
YELLOW   = "#f5a623"
TEXT     = "#e8eaf0"
TEXT_DIM = "#6b7280"

# ── Tipografías ──────────────────────
MONO = "Consolas"
SANS = "Segoe UI"

# ── Sets de control ──────────────────
EXTENSIONES_TEMP: set[str] = {
    ".crdownload", ".part", ".tmp", ".download", ".incomplete"
}

CARPETAS_SISTEMA: set[str] = {
    "Documentos", "Imagenes", "Videos", "Audio",
    "Comprimidos", "Programas", "Codigo", "Fuentes",
}

CARPETAS_IGNORADAS: set[str] = set()