import os
import time
import threading
import tkinter as tk
from watchdog.observers import Observer
from config import BG, SURFACE, SURFACE2, GREEN, RED, YELLOW, TEXT, TEXT_DIM, SANS
from logic import ordenar_archivo, corregir_clasificacion
from monitor import Monitor
from gui.widgets import FlatButton


class PanelControlesMixin:

    def _build_controls(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", padx=24)

        self.btn_toggle = FlatButton(
            frame, text="▶  INICIAR",
            command=self._toggle,
            bg=GREEN, fg="#0f1117", hover="#2db870",
            active_bg=RED, font=(SANS, 10, "bold"),
        )
        self.btn_toggle.pack(side="left", ipadx=20, ipady=10)

        FlatButton(
            frame, text="Limpiar log",
            command=self._clear_log,
            bg=SURFACE, fg=TEXT_DIM, hover=SURFACE2,
        ).pack(side="right", ipadx=12, ipady=8)

    def _build_stats(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", padx=24, pady=14)

        self._stat_labels: dict[str, tk.Label] = {}

        for key, label, color in [
            ("movidos",   "Movidos",   GREEN),
            ("errores",   "Errores",   RED),
            ("ignorados", "Ignorados", YELLOW),
        ]:
            card = tk.Frame(frame, bg=SURFACE, padx=16, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=(0, 8))

            tk.Label(card, text=label, font=(SANS, 8), fg=TEXT_DIM, bg=SURFACE).pack()
            lbl = tk.Label(card, text="0", font=(SANS, 20, "bold"), fg=color, bg=SURFACE)
            lbl.pack()
            self._stat_labels[key] = lbl

    def _toggle(self) -> None:
        if self.activo:
            self._detener()
        else:
            self._iniciar()

    def _iniciar(self) -> None:
        carpeta = self.carpeta_actual.get().strip()
        if not carpeta:
            self._log("ERROR", "Selecciona una carpeta primero.")
            return
        if not os.path.isdir(carpeta):
            self._log("ERROR", f"Carpeta no existe: {carpeta}")
            return

        for key in self.contadores:
            self.contadores[key] = 0
            self._stat_labels[key].configure(text="0")

        self.activo = True
        self._set_activo_ui(True)
        self._log("INFO", f"Iniciando en: {carpeta}")
        threading.Thread(target=self._run_organizer, daemon=True).start()

    def _detener(self) -> None:
        self.activo = False
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
        self._set_activo_ui(False)
        self._log("INFO", "Organizador detenido.")

    def _run_organizer(self) -> None:
        carpeta = self.carpeta_actual.get().strip()
        try:
            archivos = [e.path for e in os.scandir(carpeta) if e.is_file()]
            if archivos:
                self._log("INFO", f"Ordenando {len(archivos)} archivo(s) existente(s)…")
                for ruta in archivos:
                    resultado = ordenar_archivo(ruta, carpeta, self._log)
                    self._inc(resultado)
            else:
                self._log("INFO", "No hay archivos sueltos en la raíz.")

            self._log("INFO", "Verificando archivos mal clasificados…")
            corregir_clasificacion(carpeta, log_fn=self._log)
            self._log("INFO", "Verificación completada. Monitoreando cambios…")

        except Exception as e:
            self._log("ERROR", f"Error durante la inicialización: {e}")

        monitor = Monitor(carpeta_raiz=carpeta, log_fn=self._log)
        self.observer = Observer()
        self.observer.schedule(monitor, carpeta, recursive=True)
        self.observer.start()

        while self.activo:
            time.sleep(1)

    def _set_activo_ui(self, activo: bool) -> None:
        if activo:
            self.btn_toggle.configure(text="■  DETENER", bg=RED, activebackground=RED)
            self.btn_toggle._bg_normal = RED
            self.dot.configure(fg=GREEN)
            self.status_lbl.configure(text="Activo", fg=GREEN)
            self.carpeta_entry.configure(state="disabled")
            self.btn_browse.configure(state="disabled")
        else:
            self.btn_toggle.configure(text="▶  INICIAR", bg=GREEN, activebackground=GREEN)
            self.btn_toggle._bg_normal = GREEN
            self.dot.configure(fg=TEXT_DIM)
            self.status_lbl.configure(text="Inactivo", fg=TEXT_DIM)
            self.carpeta_entry.configure(state="normal")
            self.btn_browse.configure(state="normal")

    def _inc(self, resultado: str) -> None:
        key = {"movido": "movidos", "error": "errores", "ignorado": "ignorados"}.get(resultado)
        if key:
            self.contadores[key] += 1
            val = self.contadores[key]
            self.after(0, self._stat_labels[key].configure, {"text": str(val)})