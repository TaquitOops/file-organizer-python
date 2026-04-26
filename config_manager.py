"""
config_manager.py — Maneja la persistencia del mapeo extensión → carpeta.
Lee config_usuario.json si existe, si no usa los defaults de config.py.
"""
import json
import os
from config import TIPOS_ARCHIVOS as _DEFAULTS

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_usuario.json")


def _invertir(tipos: dict[str, str]) -> dict[str, list[str]]:
    """Convierte {'.pdf': 'Documentos/PDF'} → {'Documentos/PDF': ['.pdf']}"""
    resultado: dict[str, list[str]] = {}
    for ext, carpeta in tipos.items():
        resultado.setdefault(carpeta, []).append(ext)
    return resultado


def _aplanar(mapa: dict[str, list[str]]) -> dict[str, str]:
    """Convierte {'Documentos/PDF': ['.pdf']} → {'.pdf': 'Documentos/PDF'}"""
    return {ext: carpeta for carpeta, exts in mapa.items() for ext in exts}


def cargar() -> dict[str, list[str]]:
    """Devuelve el mapa carpeta → [extensiones] desde JSON o desde defaults."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return _invertir(_DEFAULTS)


def guardar(mapa: dict[str, list[str]]) -> None:
    """Guarda el mapa en config_usuario.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(mapa, f, indent=2, ensure_ascii=False)


def restaurar() -> dict[str, list[str]]:
    """Borra el JSON y devuelve los defaults."""
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
    return _invertir(_DEFAULTS)


def obtener_tipos() -> dict[str, str]:
    """Devuelve el mapa plano {ext: carpeta} listo para usar en logic.py."""
    return _aplanar(cargar())