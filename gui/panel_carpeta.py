import tkinter as tk
from tkinter import filedialog
from config import SURFACE, SURFACE2, ACCENT, ACCENT2, TEXT, TEXT_DIM, MONO, SANS
from gui.widgets import FlatButton


class PanelCarpetaMixin:

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

    def _browse(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.carpeta_actual.set(folder)
            self._log("INFO", f"Carpeta seleccionada: {folder}")