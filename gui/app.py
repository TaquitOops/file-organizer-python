"""
gui/app.py  —  Ventana principal del Organizador de Archivos.
Orquesta la lógica (logic.py), el monitor (monitor.py) y los widgets (gui/widgets.py).
"""
import logging
import threading
import time
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from typing import Optional
import os
import config

from watchdog.observers import Observer

from config      import BG, SURFACE, SURFACE2, ACCENT, ACCENT2
from config      import GREEN, RED, YELLOW, TEXT, TEXT_DIM, MONO, SANS
from logic       import ordenar_archivo, corregir_clasificacion
from monitor     import Monitor
from gui.widgets import FlatButton, GUILogHandler


class OrganizadorApp(tk.Tk):
    """Ventana principal del organizador."""

    # ─── Inicialización ─────────────────────────────────────────
    def __init__(self):
        super().__init__()
        self.title("Organizador de Archivos")
        self.geometry("760x580")
        self.minsize(680, 500)
        self.configure(bg=BG)

        # Estado de la aplicación
        self.carpeta_actual = tk.StringVar(value="")
        self.activo = False
        self.observer = None
        self.contadores = {"movidos": 0, "errores": 0, "ignorados": 0}

        self._setup_logger()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Logger ─────────────────────────────────────────────────
    def _setup_logger(self) -> None:
        """Conecta el módulo logging con el área de log de la GUI."""
        self._logger = logging.getLogger("organizador")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []

        handler = GUILogHandler(callback=self._on_log_entry)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

    def _on_log_entry(self, level: str, msg: str) -> None:
        """Recibe un registro de log desde cualquier hilo y lo despacha al hilo principal."""
        self.after(0, self._append_log, level, msg)

    def _append_log(self, level: str, msg: str) -> None:
        """Inserta una línea coloreada en el área de texto."""
        tag = {"INFO": "info", "WARNING": "warn", "ERROR": "err"}.get(level, "dim")
        ts  = datetime.now().strftime("%H:%M:%S")

        self.log_area.configure(state="normal")
        self.log_area.insert("end", f"  {ts}  ", "ts")
        self.log_area.insert("end", f"{msg}\n", tag)
        self.log_area.configure(state="disabled")
        self.log_area.see("end")

    # ─── Construcción de la UI ───────────────────────────────────
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

    def _build_folder_selector(self) -> None:
        frame = tk.Frame(self, bg=SURFACE, padx=16, pady=14)
        frame.pack(fill="x", padx=24, pady=16)

        tk.Label(
            frame, text="Carpeta a organizar",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
        ).pack(anchor="w")

        row = tk.Frame(frame, bg=SURFACE)
        row.pack(fill="x", pady=(6, 0))

        self.carpeta_entry = tk.Entry(
            row,
            textvariable=self.carpeta_actual,
            font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0, insertbackground=ACCENT,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
        )
        self.carpeta_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))

        self.btn_browse = FlatButton(
            row, text="Elegir carpeta",
            command=self._browse, bg=SURFACE2, fg=TEXT, hover=ACCENT2,
        )
        self.btn_browse.pack(side="left", ipadx=12, ipady=6)
    
    def _build_ignored(self) -> None:

        frame = tk.Frame(self, bg=SURFACE, padx=16, pady=12)
        frame.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            frame, text="Carpetas ignoradas",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
        ).pack(anchor="w")

        row = tk.Frame(frame, bg=SURFACE)
        row.pack(fill="x", pady=(6, 0))

        # Listbox con las carpetas ignoradas
        self.ignored_listbox = tk.Listbox(
            row,
            font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0,
            selectbackground=ACCENT2,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
            height=3,
        )
        self.ignored_listbox.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 10))

        # Botones
        btn_frame = tk.Frame(row, bg=SURFACE)
        btn_frame.pack(side="left")

        def agregar():
            base = self.carpeta_actual.get().strip()
            ruta = filedialog.askdirectory(
                title="Carpeta a ignorar",
                initialdir=base if base else "/",
            )
            if not ruta:
                return
            nombre = os.path.basename(ruta)
            if nombre in config.CARPETAS_IGNORADAS:
                self._log("WARNING", f"Ya se está ignorando: {nombre}")
                return
            config.CARPETAS_IGNORADAS.add(nombre)
            self.ignored_listbox.insert("end", nombre)
            self._log("INFO", f"Ignorando carpeta: {nombre}")

        def quitar():
            sel = self.ignored_listbox.curselection()
            if not sel:
                return
            nombre = self.ignored_listbox.get(sel[0])
            config.CARPETAS_IGNORADAS.discard(nombre)
            self.ignored_listbox.delete(sel[0])
            self._log("INFO", f"Ya no se ignora: {nombre}")

        FlatButton(
            btn_frame, text="+ Agregar",
            command=agregar, bg=SURFACE2, fg=TEXT, hover=ACCENT2,
        ).pack(pady=(0, 6), ipadx=10, ipady=5)

        FlatButton(
            btn_frame, text="✕ Quitar",
            command=quitar, bg=SURFACE2, fg=RED, hover=SURFACE2,
        ).pack(ipadx=10, ipady=5)
        
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

    def _build_log(self) -> None:
        outer = tk.Frame(self, bg=SURFACE)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(
            outer, text="ACTIVIDAD",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
            padx=14, pady=8,
        ).pack(anchor="w")

        # Scrollbar + Text juntos
        sb = tk.Scrollbar(outer, bg=SURFACE2)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=(0, 12))

        self.log_area = tk.Text(
            outer,
            bg=SURFACE, fg=TEXT, font=(MONO, 8),
            relief="flat", bd=0,
            state="disabled", wrap="none", cursor="arrow",
            selectbackground=ACCENT2,
            yscrollcommand=sb.set,
            padx=4, pady=4,
        )
        self.log_area.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        sb.configure(command=self.log_area.yview)

        # Colores de las etiquetas
        self.log_area.tag_configure("ts",   foreground=TEXT_DIM)
        self.log_area.tag_configure("info", foreground=TEXT)
        self.log_area.tag_configure("warn", foreground=YELLOW)
        self.log_area.tag_configure("err",  foreground=RED)
        self.log_area.tag_configure("dim",  foreground=TEXT_DIM)

    # ─── Acciones del usuario ────────────────────────────────────
    def _browse(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.carpeta_actual.set(folder)
            self._log("INFO", f"Carpeta seleccionada: {folder}")

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

        # Resetear contadores
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

    # ─── Hilo del organizador ────────────────────────────────────
    def _run_organizer(self) -> None:
        """Se ejecuta en un hilo separado para no bloquear la GUI."""

        carpeta = self.carpeta_actual.get().strip()

        try:
            # 1. Ordenar archivos sueltos existentes
            archivos = [e.path for e in os.scandir(carpeta) if e.is_file()]
            if archivos:
                self._log("INFO", f"Ordenando {len(archivos)} archivo(s) existente(s)…")
                for ruta in archivos:
                    resultado = ordenar_archivo(ruta, carpeta, self._log)
                    self._inc(resultado)
            else:
                self._log("INFO", "No hay archivos sueltos en la raíz.")

            # 2. Corregir clasificaciones previas
            self._log("INFO", "Verificando archivos mal clasificados…")
            corregir_clasificacion(carpeta, log_fn=self._log)
            self._log("INFO", "Verificación completada. Monitoreando cambios…")

        except Exception as e:
            self._log("ERROR", f"Error durante la inicialización: {e}")

        # 3. Iniciar watchdog
        monitor      = Monitor(carpeta_raiz=carpeta, log_fn=self._log)
        self.observer = Observer()
        self.observer.schedule(monitor, carpeta, recursive=True)
        self.observer.start()

        # Mantener vivo el hilo mientras el organizador esté activo
        while self.activo:
            time.sleep(1)

    # ─── Helpers ────────────────────────────────────────────────
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
        """Incrementa el contador correspondiente al resultado de ordenar_archivo."""
        key = {"movido": "movidos", "error": "errores", "ignorado": "ignorados"}.get(resultado)
        if key:
            self.contadores[key] += 1
            val = self.contadores[key]
            self.after(0, self._stat_labels[key].configure, {"text": str(val)})

    def _log(self, level: str, msg: str) -> None:
        self._on_log_entry(level, msg)

    def _clear_log(self) -> None:
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")

    def _on_close(self) -> None:
        if self.activo:
            self._detener()
        self.destroy()