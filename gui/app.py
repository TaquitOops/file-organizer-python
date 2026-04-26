"""
gui/app.py  —  Ventana principal del Organizador de Archivos.
"""
import logging
import tkinter as tk

from config import BG, SURFACE, ACCENT, TEXT_DIM, SANS
from gui.widgets         import GUILogHandler
from gui.panel_carpeta   import PanelCarpetaMixin
from gui.panel_ignoradas import PanelIgnoradasMixin
from gui.panel_controles import PanelControlesMixin
from gui.panel_log       import PanelLogMixin


class OrganizadorApp(
    PanelCarpetaMixin,
    PanelIgnoradasMixin,
    PanelControlesMixin,
    PanelLogMixin,
    tk.Tk,
):
    def __init__(self):
        super().__init__()
        self.title("Organizador de Archivos")
        self.geometry("760x580")
        self.minsize(680, 500)
        self.configure(bg=BG)

        self.carpeta_actual = tk.StringVar(value="")
        self.activo = False
        self.observer = None
        self.contadores = {"movidos": 0, "errores": 0, "ignorados": 0}

        self._setup_logger()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_logger(self) -> None:
        self._logger = logging.getLogger("organizador")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []

        handler = GUILogHandler(callback=self._on_log_entry)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

    def _build_ui(self) -> None:
        self._build_header()
        self._build_folder_selector()
        self._build_ignored()
        self._build_controls()
        self._build_stats()
        self._build_log()
        self._log("INFO", "Listo. Elige una carpeta y presiona INICIAR.")

    def _build_header(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(
            frame, text="ORGANIZADOR",
            font=(SANS, 9, "bold"), fg=ACCENT, bg=BG,
        ).pack(side="left")

        self.dot = tk.Label(frame, text="●", font=(SANS, 10), fg=TEXT_DIM, bg=BG)
        self.dot.pack(side="right")

        self.status_lbl = tk.Label(
            frame, text="Inactivo", font=(SANS, 9), fg=TEXT_DIM, bg=BG,
        )
        self.status_lbl.pack(side="right", padx=(0, 6))

    def _on_close(self) -> None:
        if self.activo:
            self._detener()
        self.destroy()