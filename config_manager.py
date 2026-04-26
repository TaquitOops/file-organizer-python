"""
config_manager.py — Maneja perfiles de configuración con persistencia en JSON.
"""
import json
import os

PERFILES_PATH = os.path.join(os.path.dirname(__file__), "perfiles.json")


def _cargar_json() -> dict:
    with open(PERFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_json(data: dict) -> None:
    with open(PERFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Perfiles ─────────────────────────────────────────────────

def listar_perfiles() -> list[str]:
    return list(_cargar_json()["perfiles"].keys())


def obtener_perfil(nombre: str) -> dict:
    return _cargar_json()["perfiles"].get(nombre, {})


def guardar_perfil(nombre: str, carpeta_raiz: str | None, mapa: dict[str, list[str]]) -> None:
    data = _cargar_json()
    data["perfiles"][nombre] = {
        "carpeta_raiz": carpeta_raiz,
        "mapa": mapa,
    }
    _guardar_json(data)


def eliminar_perfil(nombre: str) -> None:
    data = _cargar_json()
    data["perfiles"].pop(nombre, None)
    if data["perfil_activo"] == nombre:
        data["perfil_activo"] = None
    _guardar_json(data)


def duplicar_perfil(origen: str, destino: str) -> None:
    data = _cargar_json()
    if origen in data["perfiles"]:
        data["perfiles"][destino] = json.loads(
            json.dumps(data["perfiles"][origen])
        )
    _guardar_json(data)


# ── Perfil activo ─────────────────────────────────────────────

def obtener_perfil_activo() -> str | None:
    return _cargar_json().get("perfil_activo")


def establecer_perfil_activo(nombre: str | None) -> None:
    data = _cargar_json()
    data["perfil_activo"] = nombre
    _guardar_json(data)


# ── Mapa plano para logic.py ──────────────────────────────────

def obtener_tipos() -> dict[str, str]:
    """Devuelve {ext: carpeta} del perfil activo. Vacío si no hay perfil."""
    data = _cargar_json()
    activo = data.get("perfil_activo")
    if not activo:
        return {}
    mapa = data["perfiles"].get(activo, {}).get("mapa", {})
    return {ext: carpeta for carpeta, exts in mapa.items() for ext in exts}


def obtener_carpeta_raiz() -> str | None:
    """Devuelve la carpeta raíz del perfil activo."""
    data = _cargar_json()
    activo = data.get("perfil_activo")
    if not activo:
        return None
    return data["perfiles"].get(activo, {}).get("carpeta_raiz")


# ── Catálogo ──────────────────────────────────────────────────

def obtener_catalogo() -> dict[str, list[str]]:
    return _cargar_json().get("catalogo", {})