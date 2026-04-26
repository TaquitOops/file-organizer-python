"""
monitor.py  —  Watchdog FileSystemEventHandler.
Detecta archivos creados y renombres de descargas (e.g. .crdownload → .pdf).
"""
import os
import time
import logging

from watchdog.events import FileSystemEventHandler

from config import EXTENSIONES_TEMP, CARPETAS_SISTEMA
from logic  import ordenar_archivo

logger = logging.getLogger(__name__)


class Monitor(FileSystemEventHandler):
    """
    Observa una carpeta y ordena los archivos entrantes.

    Parámetros
    ----------
    carpeta_raiz : str
        Carpeta que se está monitoreando.
    log_fn : callable(level: str, msg: str) | None
        Callback para enviar mensajes a la GUI.
    """

    def __init__(self, carpeta_raiz: str, log_fn=None):
        super().__init__()
        self._carpeta = carpeta_raiz
        self._log_fn  = log_fn

    # ─── Eventos ────────────────────────────────────────────────
    def on_created(self, event):
        """Archivo nuevo detectado (no en proceso de descarga)."""
        if event.is_directory:
            return

        ext = os.path.splitext(event.src_path)[1].lower()

        # Las extensiones temporales se capturan con on_moved
        if ext in EXTENSIONES_TEMP:
            return

        time.sleep(0.2)
        self._procesar(event.src_path)

    def on_moved(self, event):
        """
        Captura el rename de archivo temporal → definitivo.
        Caso típico: Chrome  archivo.pdf.crdownload → archivo.pdf
        """
        if event.is_directory:
            return

        src_ext = os.path.splitext(event.src_path)[1].lower()

        # Solo nos interesan los renombres desde una extensión temporal
        if src_ext not in EXTENSIONES_TEMP:
            return

        time.sleep(1)   # Esperar a que el SO libere el handle

        ruta = event.dest_path
        if not os.path.exists(ruta):
            logger.debug("Archivo renombrado ya no existe: %s", ruta)
            return

        self._procesar(ruta)

    # ─── Lógica interna ─────────────────────────────────────────
    def _procesar(self, ruta: str) -> None:
        """
        Comprueba que el archivo no esté dentro de una carpeta del sistema
        y lo envía a ordenar_archivo.
        """
        try:
            ruta_rel = os.path.relpath(ruta, self._carpeta)
            partes   = ruta_rel.split(os.sep)

            # Si ya está en una carpeta del sistema, ignorar
            if len(partes) > 1 and partes[0] in CARPETAS_SISTEMA:
                return

            ordenar_archivo(ruta, self._carpeta, self._log_fn)

        except Exception as e:
            logger.error("Monitor._procesar: %s → %s", ruta, e)