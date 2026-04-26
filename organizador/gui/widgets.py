"""
gui/widgets.py  —  Componentes tkinter reutilizables.
"""
import logging
import tkinter as tk

from config import SANS


# ─────────────────────────────────────
#   BOTÓN PLANO CON HOVER
# ─────────────────────────────────────
class FlatButton(tk.Button):
    """
    Botón sin relieve con efecto hover de color.

    Parámetros extra respecto a tk.Button
    ──────────────────────────────────────
    hover     : color de fondo al pasar el cursor
    active_bg : color de activebackground (por defecto = hover)
    font      : tupla de fuente (por defecto Segoe UI 9)
    """

    def __init__(
        self,
        parent,
        text: str,
        command,
        bg: str,
        fg: str,
        hover: str,
        active_bg: str = None,
        font=None,
        **kwargs,
    ):
        _font = font or (SANS, 9)
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg or hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=_font,
            cursor="hand2",
            **kwargs,
        )
        self._bg_normal = bg
        self._bg_hover  = hover

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        if str(self["state"]) != "disabled":
            self.configure(bg=self._bg_hover)

    def _on_leave(self, _event):
        self.configure(bg=self._bg_normal)

    def set_colors(self, bg: str, hover: str = None):
        """Actualiza el color base (y opcionalmente el hover) en caliente."""
        self._bg_normal = bg
        if hover:
            self._bg_hover = hover
        self.configure(bg=bg, activebackground=self._bg_hover)


# ─────────────────────────────────────
#   LOGGING HANDLER → GUI
# ─────────────────────────────────────
class GUILogHandler(logging.Handler):
    """
    Redirige los registros de logging a un callback `fn(level, msg)`.
    Útil para mostrar logs en un widget de texto de tkinter.

    Uso
    ───
    handler = GUILogHandler(callback=mi_funcion)
    logging.getLogger("mi_modulo").addHandler(handler)
    """

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._callback(record.levelname, msg)
        except Exception:
            self.handleError(record)