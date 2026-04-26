import os
import tkinter as tk
from tkinter import filedialog
import config
from config import SURFACE, SURFACE2, ACCENT, ACCENT2, TEXT, TEXT_DIM, RED, MONO, SANS
from gui.widgets import FlatButton


class PanelIgnoradasMixin:

    def _build_ignored(self) -> None:
        frame = tk.Frame(self, bg=SURFACE, padx=16, pady=12)
        frame.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            frame, text="Carpetas ignoradas",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
        ).pack(anchor="w")

        row = tk.Frame(frame, bg=SURFACE)
        row.pack(fill="x", pady=(6, 0))

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