import tkinter as tk
from datetime import datetime
from config import SURFACE, SURFACE2, ACCENT, ACCENT2, YELLOW, RED, TEXT, TEXT_DIM, MONO, SANS
from gui.widgets import GUILogHandler


class PanelLogMixin:

    def _build_log(self) -> None:
        outer = tk.Frame(self, bg=SURFACE)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(
            outer, text="ACTIVIDAD",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
            padx=14, pady=8,
        ).pack(anchor="w")

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

        self.log_area.tag_configure("ts",   foreground=TEXT_DIM)
        self.log_area.tag_configure("info", foreground=TEXT)
        self.log_area.tag_configure("warn", foreground=YELLOW)
        self.log_area.tag_configure("err",  foreground=RED)
        self.log_area.tag_configure("dim",  foreground=TEXT_DIM)

    def _on_log_entry(self, level: str, msg: str) -> None:
        self.after(0, self._append_log, level, msg)

    def _append_log(self, level: str, msg: str) -> None:
        tag = {"INFO": "info", "WARNING": "warn", "ERROR": "err"}.get(level, "dim")
        ts  = datetime.now().strftime("%H:%M:%S")

        self.log_area.configure(state="normal")
        self.log_area.insert("end", f"  {ts}  ", "ts")
        self.log_area.insert("end", f"{msg}\n", tag)
        self.log_area.configure(state="disabled")
        self.log_area.see("end")

    def _log(self, level: str, msg: str) -> None:
        self._on_log_entry(level, msg)

    def _clear_log(self) -> None:
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")