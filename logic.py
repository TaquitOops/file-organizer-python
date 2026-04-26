"""
logic.py  —  Funciones de organización de archivos.
Sin dependencias de GUI; se pueden testear de forma independiente.
"""
import os
import re
import time
import mimetypes
import logging

from config import EXTENSIONES_TEMP
import config_manager

logger = logging.getLogger(__name__)


# ─────────────────────────────────────
#   RESOLUCIÓN DE DUPLICADOS
# ─────────────────────────────────────
def resolver_duplicado(ruta_destino: str) -> str:
    """
    Si `ruta_destino` ya existe, devuelve una ruta con sufijo (1), (2)…
    Limpia cualquier sufijo previo del nombre base antes de generar uno nuevo.
    """
    if not os.path.exists(ruta_destino):
        return ruta_destino

    base, ext   = os.path.splitext(os.path.basename(ruta_destino))
    carpeta_d   = os.path.dirname(ruta_destino)
    base_real   = re.sub(r'\s*\(\d+\)$', '', base).strip()

    i = 1
    while True:
        nueva = os.path.join(carpeta_d, f"{base_real} ({i}){ext}")
        if not os.path.exists(nueva):
            return nueva
        i += 1


# ─────────────────────────────────────
#   CLASIFICACIÓN
# ─────────────────────────────────────
def carpeta_correcta(archivo: str) -> str:
    import config_manager
    tipos = config_manager.obtener_tipos()
    ext = os.path.splitext(archivo)[1].lower()
    if ext in tipos:
        return tipos[ext]
    tipo, _ = mimetypes.guess_type(archivo)
    if tipo:
        if "image" in tipo: return "Imagenes/Otros"
        if "video" in tipo: return "Videos"
        if "audio" in tipo: return "Audio"
        if "pdf"   in tipo: return "Documentos/PDF"
        if "text"  in tipo: return "Documentos/Texto"
    return "Otros"

# ─────────────────────────────────────
#   VERIFICACIÓN DE ARCHIVO LISTO
# ─────────────────────────────────────
def archivo_listo(ruta: str, max_espera: float = 5.0) -> bool:
    """
    Espera hasta `max_espera` segundos hasta confirmar que el archivo
    no está creciendo (descarga o copia en curso).
    """
    try:
        t0, tam_ant = time.time(), -1

        while time.time() - t0 < max_espera:
            if not os.path.exists(ruta):
                time.sleep(0.1)
                continue
            try:
                tam = os.path.getsize(ruta)
                if tam == tam_ant and tam > 0:
                    time.sleep(0.3)                     # segunda verificación
                    if os.path.getsize(ruta) == tam:
                        return True
                tam_ant = tam
            except (OSError, PermissionError) as e:
                logger.debug("Esperando acceso a %s: %s", ruta, e)
            time.sleep(0.3)

        return False
    except Exception as e:
        logger.warning("archivo_listo falló para %s: %s", ruta, e)
        return False


# ─────────────────────────────────────
#   MOVER ARCHIVO
# ─────────────────────────────────────
def mover_archivo(
    ruta_archivo: str,
    destino_nombre: str,
    carpeta_raiz: str,
    log_fn=None,
) -> bool:
    """
    Mueve `ruta_archivo` a `<carpeta_raiz>/<destino_nombre>/`.
    Retorna True si fue exitoso.
    `log_fn(level, msg)` es opcional para enviar mensajes a la GUI.
    """
    def _log(level, msg):
        if log_fn:
            log_fn(level, msg)
        getattr(logger, level.lower(), logger.info)(msg)

    try:
        archivo  = os.path.basename(ruta_archivo)
        dest_dir = os.path.join(carpeta_raiz, destino_nombre)

        # Ya está en el lugar correcto
        if os.path.normpath(os.path.dirname(ruta_archivo)) == os.path.normpath(dest_dir):
            return True

        os.makedirs(dest_dir, exist_ok=True)
        nueva_ruta = resolver_duplicado(os.path.join(dest_dir, archivo))

        for intento in range(3):
            try:
                os.replace(ruta_archivo, nueva_ruta)
                _log("INFO", f"✓  {archivo}  →  {destino_nombre}/")
                return True

            except PermissionError:
                if intento < 2:
                    _log("WARNING", f"   Archivo en uso, reintentando ({intento+1}/3)…")
                    time.sleep(1.5)
                else:
                    _log("ERROR", f"✗  No se pudo mover (bloqueado): {archivo}")
                    return False

            except FileExistsError:
                nueva_ruta = resolver_duplicado(nueva_ruta)

            except Exception as e:
                _log("ERROR", f"✗  {archivo}: {type(e).__name__}: {e}")
                return False

    except Exception as e:
        logger.error("mover_archivo: error inesperado: %s", e)
        return False

    return False


# ─────────────────────────────────────
#   ORDENAR UN ARCHIVO INDIVIDUAL
# ─────────────────────────────────────
def ordenar_archivo(
    ruta_archivo: str,
    carpeta_raiz: str,
    log_fn=None,
) -> str:
    """
    Clasifica y mueve `ruta_archivo` a la carpeta que le corresponde.
    Devuelve: 'movido' | 'ignorado' | 'error'
    """
    try:
        if not os.path.isfile(ruta_archivo):
            return "ignorado"

        archivo = os.path.basename(ruta_archivo)

        if archivo.startswith(("~$", ".")):
            return "ignorado"

        if os.path.splitext(archivo)[1].lower() in EXTENSIONES_TEMP:
            return "ignorado"

        if not archivo_listo(ruta_archivo):
            return "ignorado"

        destino = carpeta_correcta(archivo)
        ok      = mover_archivo(ruta_archivo, destino, carpeta_raiz, log_fn)
        return "movido" if ok else "error"

    except Exception as e:
        logger.error("ordenar_archivo: %s → %s", ruta_archivo, e)
        return "error"


# ─────────────────────────────────────
#   CORREGIR CLASIFICACIÓN EXISTENTE
# ─────────────────────────────────────
def corregir_clasificacion(
    carpeta_raiz: str,
    dir_actual: str = None,
    nivel: int = 0,
    log_fn=None,
    carpetas_sistema: set = None,
) -> None:
    """
    Recorre `dir_actual` recursivamente y mueve los archivos que estén
    en una subcarpeta incorrecta.
    """
    from config import CARPETAS_SISTEMA as _CS
    carpetas_sistema = carpetas_sistema or _CS

    def _log(level, msg):
        if log_fn:
            log_fn(level, msg)
        getattr(logger, level.lower(), logger.info)(msg)

    if nivel > 3:
        return

    dir_actual = dir_actual or carpeta_raiz

    try:
        for entrada in os.scandir(dir_actual):
            ruta   = entrada.path
            nombre = entrada.name

            if os.path.isfile(ruta):
                # Ignorar archivos en la raíz
                if os.path.dirname(ruta) == carpeta_raiz:
                    continue
                if os.path.splitext(nombre)[1].lower() in EXTENSIONES_TEMP:
                    continue

                destino_c = os.path.normpath(carpeta_correcta(nombre))
                ubicacion = os.path.normpath(
                    os.path.relpath(os.path.dirname(ruta), carpeta_raiz)
                )

                if destino_c != ubicacion:
                    _log("INFO", f"⟳  '{nombre}'  {ubicacion}/  →  {destino_c}/")
                    mover_archivo(ruta, destino_c, carpeta_raiz, log_fn)

            elif os.path.isdir(ruta):
                if nombre not in carpetas_sistema:
                    corregir_clasificacion(
                        carpeta_raiz, ruta, nivel + 1, log_fn, carpetas_sistema
                    )

    except Exception as e:
        _log("ERROR", f"corregir_clasificacion: {e}")