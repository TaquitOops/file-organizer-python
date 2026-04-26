# ─────────────────────────────────────
#   config.py  —  Constantes globales
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

# ── Mapeo extensión → carpeta ────────
TIPOS_ARCHIVOS: dict[str, str] = {
    # Documentos
    ".pdf":  "Documentos/PDF",
    ".docx": "Documentos/Word",  ".doc":  "Documentos/Word",
    ".odt":  "Documentos/Word",  ".rtf":  "Documentos/Word",
    ".txt":  "Documentos/Texto", ".md":   "Documentos/Texto",
    ".xlsx": "Documentos/Excel", ".xls":  "Documentos/Excel",
    ".csv":  "Documentos/Excel", ".ods":  "Documentos/Excel",
    ".pptx": "Documentos/PowerPoint", ".ppt": "Documentos/PowerPoint",
    ".odp":  "Documentos/PowerPoint",
    ".xml":  "Documentos/Texto", ".json": "Documentos/Texto",
    # Imágenes
    ".jpg":  "Imagenes/Fotos",   ".jpeg": "Imagenes/Fotos",
    ".png":  "Imagenes/Fotos",   ".webp": "Imagenes/Fotos",
    ".bmp":  "Imagenes/Fotos",   ".tiff": "Imagenes/Fotos",
    ".tif":  "Imagenes/Fotos",   ".heic": "Imagenes/Fotos",
    ".raw":  "Imagenes/Fotos",   ".gif":  "Imagenes/GIFs",
    ".svg":  "Imagenes/Vectores",".ico":  "Imagenes/Vectores",
    ".ai":   "Imagenes/Edicion", ".psd":  "Imagenes/Edicion",
    # Videos
    ".mp4":  "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov":  "Videos", ".webm":"Videos", ".flv": "Videos",
    ".wmv":  "Videos", ".3gp": "Videos",
    # Audio
    ".mp3":  "Audio", ".wav":  "Audio", ".flac": "Audio",
    ".ogg":  "Audio", ".m4a":  "Audio", ".aac":  "Audio",
    ".wma":  "Audio", ".opus": "Audio", ".mid":  "Audio",
    # Programas
    ".exe":  "Programas/Windows", ".msi": "Programas/Windows",
    ".bat":  "Programas/Windows",
    ".dmg":  "Programas/Mac",     ".pkg": "Programas/Mac",
    ".deb":  "Programas/Linux",   ".rpm": "Programas/Linux",
    # Comprimidos
    ".zip":  "Comprimidos", ".rar": "Comprimidos", ".7z":  "Comprimidos",
    ".tar":  "Comprimidos", ".gz":  "Comprimidos", ".iso": "Comprimidos",
    # Código
    ".py":   "Codigo/Python",
    ".js":   "Codigo/JavaScript", ".ts":  "Codigo/JavaScript",
    ".html": "Codigo/Web",        ".css": "Codigo/Web",
    ".java": "Codigo/Java",
    ".cpp":  "Codigo/C",          ".c":   "Codigo/C",
    ".cs":   "Codigo/CSharp",
    ".php":  "Codigo/PHP",        ".sql": "Codigo/SQL",
    # Fuentes
    ".ttf":  "Fuentes", ".otf":   "Fuentes",
    ".woff": "Fuentes", ".woff2": "Fuentes",
}

# ── Sets de control ──────────────────
EXTENSIONES_TEMP: set[str] = {
    ".crdownload", ".part", ".tmp", ".download", ".incomplete"
}

CARPETAS_SISTEMA: set[str] = {
    "Documentos", "Imagenes", "Videos", "Audio",
    "Comprimidos", "Programas", "Codigo", "Fuentes",
}

CARPETAS_IGNORADAS: set[str] = set()

# ── Config dinámica ──────────────────
CARPETAS_IGNORADAS: set[str] = set()