"""
gui/panel_configuracion.py — Mixin para el editor de mapeo extensión → carpeta.
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import config_manager
from config import (
    BG, SURFACE, SURFACE2, ACCENT, ACCENT2,
    GREEN, RED, YELLOW, TEXT, TEXT_DIM, MONO, SANS
)
from gui.widgets import FlatButton


class PanelConfiguracionMixin:

    def _abrir_configuracion(self) -> None:
        """Abre la ventana secundaria de configuración."""
        win = tk.Toplevel(self)
        win.title("Configuración de carpetas")
        win.geometry("640x480")
        win.minsize(560, 400)
        win.configure(bg=BG)
        win.grab_set()  # modal

        # Estado local de la ventana
        mapa: dict[str, list[str]] = config_manager.cargar()
        carpeta_sel = tk.StringVar()

        # ── Layout principal ─────────────────────────────────
        top = tk.Frame(win, bg=BG)
        top.pack(fill="both", expand=True, padx=16, pady=16)

        # Panel izquierdo — carpetas
        left = tk.Frame(top, bg=SURFACE, padx=12, pady=12)
        left.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left.configure(width=200)
        left.pack_propagate(False)

        tk.Label(
            left, text="CARPETAS",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
        ).pack(anchor="w", pady=(0, 6))

        lb_carpetas = tk.Listbox(
            left,
            font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0,
            selectbackground=ACCENT2,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
            activestyle="none",
        )
        lb_carpetas.pack(fill="both", expand=True)

        # Panel derecho — extensiones
        right = tk.Frame(top, bg=SURFACE, padx=12, pady=12)
        right.pack(side="left", fill="both", expand=True)

        lbl_carpeta_sel = tk.Label(
            right, text="Selecciona una carpeta",
            font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE,
        )
        lbl_carpeta_sel.pack(anchor="w", pady=(0, 6))

        lb_exts = tk.Listbox(
            right,
            font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0,
            selectbackground=ACCENT2,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
            activestyle="none",
        )
        lb_exts.pack(fill="both", expand=True)

        # ── Helpers ──────────────────────────────────────────
        def recargar_carpetas():
            lb_carpetas.delete(0, "end")
            for c in sorted(mapa.keys()):
                lb_carpetas.insert("end", c)

        def recargar_exts(carpeta: str):
            lb_exts.delete(0, "end")
            for ext in sorted(mapa.get(carpeta, [])):
                lb_exts.insert("end", ext)
            lbl_carpeta_sel.configure(text=f"Extensiones en: {carpeta}")

        def on_carpeta_select(event=None):
            sel = lb_carpetas.curselection()
            if sel:
                carpeta_sel.set(lb_carpetas.get(sel[0]))
                recargar_exts(carpeta_sel.get())

        lb_carpetas.bind("<<ListboxSelect>>", on_carpeta_select)

        # ── Botones carpetas ─────────────────────────────────
        btn_row_c = tk.Frame(left, bg=SURFACE)
        btn_row_c.pack(fill="x", pady=(8, 0))

        def nueva_carpeta():
            nombre = simpledialog.askstring(
                "Nueva carpeta", "Nombre de la carpeta destino:",
                parent=win,
            )
            if not nombre:
                return
            nombre = nombre.strip()
            if nombre in mapa:
                messagebox.showwarning("Aviso", f"'{nombre}' ya existe.", parent=win)
                return
            mapa[nombre] = []
            recargar_carpetas()

        def renombrar_carpeta():
            carpeta = carpeta_sel.get()
            if not carpeta:
                return
            nuevo = simpledialog.askstring(
                "Renombrar", f"Nuevo nombre para '{carpeta}':",
                parent=win, initialvalue=carpeta,
            )
            if not nuevo or nuevo == carpeta:
                return
            nuevo = nuevo.strip()
            if nuevo in mapa:
                messagebox.showwarning("Aviso", f"'{nuevo}' ya existe.", parent=win)
                return
            mapa[nuevo] = mapa.pop(carpeta)
            carpeta_sel.set(nuevo)
            recargar_carpetas()
            recargar_exts(nuevo)
            # Seleccionar la carpeta renombrada
            for i, c in enumerate(sorted(mapa.keys())):
                if c == nuevo:
                    lb_carpetas.selection_set(i)
                    break

        def eliminar_carpeta():
            carpeta = carpeta_sel.get()
            if not carpeta:
                return
            if not messagebox.askyesno(
                "Confirmar",
                f"¿Eliminar '{carpeta}' y todas sus extensiones?",
                parent=win,
            ):
                return
            mapa.pop(carpeta, None)
            carpeta_sel.set("")
            lb_exts.delete(0, "end")
            lbl_carpeta_sel.configure(text="Selecciona una carpeta")
            recargar_carpetas()

        FlatButton(btn_row_c, text="+ Nueva",    command=nueva_carpeta,    bg=SURFACE2, fg=TEXT,  hover=ACCENT2).pack(side="left", ipadx=6, ipady=4, padx=(0, 4))
        FlatButton(btn_row_c, text="✎ Renombrar", command=renombrar_carpeta, bg=SURFACE2, fg=TEXT,  hover=ACCENT2).pack(side="left", ipadx=6, ipady=4, padx=(0, 4))
        FlatButton(btn_row_c, text="✕ Eliminar",  command=eliminar_carpeta,  bg=SURFACE2, fg=RED,   hover=SURFACE2).pack(side="left", ipadx=6, ipady=4)

        # ── Botones extensiones ──────────────────────────────
        btn_row_e = tk.Frame(right, bg=SURFACE)
        btn_row_e.pack(fill="x", pady=(8, 0))

        def agregar_ext():
            carpeta = carpeta_sel.get()
            if not carpeta:
                messagebox.showwarning("Aviso", "Selecciona una carpeta primero.", parent=win)
                return
            ext = simpledialog.askstring(
                "Agregar extensión", "Extensión (ej: .pdf):",
                parent=win,
            )
            if not ext:
                return
            ext = ext.strip().lower()
            if not ext.startswith("."):
                ext = "." + ext
            # Verificar si ya existe en otra carpeta
            for c, exts in mapa.items():
                if ext in exts and c != carpeta:
                    if not messagebox.askyesno(
                        "Confirmar",
                        f"'{ext}' ya está en '{c}'.\n¿Moverla a '{carpeta}'?",
                        parent=win,
                    ):
                        return
                    mapa[c].remove(ext)
                    break
            if ext not in mapa[carpeta]:
                mapa[carpeta].append(ext)
            recargar_exts(carpeta)

        def quitar_ext():
            carpeta = carpeta_sel.get()
            if not carpeta:
                return
            sel = lb_exts.curselection()
            if not sel:
                return
            ext = lb_exts.get(sel[0])
            mapa[carpeta].remove(ext)
            recargar_exts(carpeta)

        FlatButton(btn_row_e, text="+ Agregar ext", command=agregar_ext, bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=8, ipady=4, padx=(0, 4))
        FlatButton(btn_row_e, text="✕ Quitar ext",  command=quitar_ext,  bg=SURFACE2, fg=RED,  hover=SURFACE2).pack(side="left", ipadx=8, ipady=4)

        # ── Barra inferior ───────────────────────────────────
        bottom = tk.Frame(win, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(0, 16))

        def guardar():
            config_manager.guardar(mapa)
            self._log("INFO", "✓ Configuración guardada.")
            win.destroy()

        def restaurar():
            if not messagebox.askyesno(
                "Restaurar",
                "¿Restaurar el mapeo original?\nSe perderán todos los cambios.",
                parent=win,
            ):
                return
            mapa.clear()
            mapa.update(config_manager.restaurar())
            recargar_carpetas()
            lb_exts.delete(0, "end")
            lbl_carpeta_sel.configure(text="Selecciona una carpeta")
            self._log("INFO", "↺ Configuración restaurada a valores por defecto.")

        FlatButton(bottom, text="↺ Restaurar defaults", command=restaurar, bg=SURFACE2, fg=YELLOW, hover=SURFACE2).pack(side="left",  ipadx=12, ipady=8)
        FlatButton(bottom, text="💾 Guardar",            command=guardar,   bg=GREEN,    fg=BG,     hover="#2db870").pack(side="right", ipadx=16, ipady=8)

        # Cargar datos iniciales
        recargar_carpetas()