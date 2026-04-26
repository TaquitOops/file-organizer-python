"""
gui/panel_configuracion.py — Editor de perfiles de configuración.
"""
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import config_manager
from config import (
    BG, SURFACE, SURFACE2, ACCENT, ACCENT2,
    GREEN, RED, YELLOW, TEXT, TEXT_DIM, MONO, SANS
)
from gui.widgets import FlatButton


class PanelConfiguracionMixin:

    def _abrir_configuracion(self) -> None:
        win = tk.Toplevel(self)
        win.title("Configuración de perfiles")
        win.geometry("720x540")
        win.minsize(640, 460)
        win.configure(bg=BG)
        win.grab_set()

        # ── Estado local ─────────────────────────────────────
        perfiles     = config_manager.listar_perfiles()
        perfil_sel   = tk.StringVar(value=perfiles[0] if perfiles else "")
        carpeta_sel  = tk.StringVar()
        mapa_local   = {}
        carpeta_mapa = tk.StringVar()

        # ── Header — selector de perfil ──────────────────────
        hdr = tk.Frame(win, bg=SURFACE, padx=16, pady=10)
        hdr.pack(fill="x", padx=16, pady=(16, 0))

        tk.Label(hdr, text="Perfil:", font=(SANS, 9, "bold"),
                 fg=TEXT_DIM, bg=SURFACE).pack(side="left")

        om_perfil = tk.OptionMenu(hdr, perfil_sel, *perfiles if perfiles else [""])
        om_perfil.configure(
            bg=SURFACE2, fg=TEXT, activebackground=ACCENT2,
            relief="flat", font=(MONO, 9), bd=0,
            highlightthickness=0,
        )
        om_perfil["menu"].configure(bg=SURFACE2, fg=TEXT, font=(MONO, 9))
        om_perfil.pack(side="left", padx=(8, 16))

        # ── Helpers de perfil ─────────────────────────────────
        def refrescar_om():
            menu = om_perfil["menu"]
            menu.delete(0, "end")
            for p in config_manager.listar_perfiles():
                menu.add_command(label=p, command=lambda v=p: cargar_perfil(v))

        def cargar_perfil(nombre: str) -> None:
            perfil_sel.set(nombre)
            datos = config_manager.obtener_perfil(nombre)
            carpeta_sel.set(datos.get("carpeta_raiz") or "")
            mapa_local.clear()
            mapa_local.update(datos.get("mapa", {}))
            recargar_carpetas_mapa()
            carpeta_mapa.set("")
            lbl_exts.configure(text="Selecciona una carpeta")

        def nuevo_perfil():
            nombre = simpledialog.askstring("Nuevo perfil", "Nombre:", parent=win)
            if not nombre:
                return
            nombre = nombre.strip()
            if nombre in config_manager.listar_perfiles():
                messagebox.showwarning("Aviso", f"'{nombre}' ya existe.", parent=win)
                return
            config_manager.guardar_perfil(nombre, None, {})
            refrescar_om()
            cargar_perfil(nombre)

        def duplicar_perfil():
            origen = perfil_sel.get()
            if not origen:
                return
            nombre = simpledialog.askstring(
                "Duplicar perfil", "Nombre del nuevo perfil:",
                parent=win, initialvalue=f"{origen} (copia)",
            )
            if not nombre:
                return
            nombre = nombre.strip()
            config_manager.duplicar_perfil(origen, nombre)
            refrescar_om()
            cargar_perfil(nombre)

        def eliminar_perfil():
            nombre = perfil_sel.get()
            if not nombre:
                return
            if not messagebox.askyesno(
                "Confirmar", f"¿Eliminar el perfil '{nombre}'?", parent=win
            ):
                return
            config_manager.eliminar_perfil(nombre)
            refrescar_om()
            perfiles_restantes = config_manager.listar_perfiles()
            if perfiles_restantes:
                cargar_perfil(perfiles_restantes[0])
            else:
                perfil_sel.set("")
                mapa_local.clear()
                recargar_carpetas_mapa()

        FlatButton(hdr, text="+ Nuevo",    command=nuevo_perfil,    bg=SURFACE2, fg=TEXT,   hover=ACCENT2).pack(side="left", ipadx=8,  ipady=4)
        FlatButton(hdr, text="⎘ Duplicar", command=duplicar_perfil, bg=SURFACE2, fg=TEXT,   hover=ACCENT2).pack(side="left", ipadx=8,  ipady=4, padx=(4, 0))
        FlatButton(hdr, text="🗑 Eliminar", command=eliminar_perfil, bg=SURFACE2, fg=RED,    hover=SURFACE2).pack(side="left", ipadx=8, ipady=4, padx=(4, 0))

        # ── Carpeta raíz del perfil ───────────────────────────
        raiz_frame = tk.Frame(win, bg=SURFACE, padx=16, pady=10)
        raiz_frame.pack(fill="x", padx=16, pady=(8, 0))

        tk.Label(raiz_frame, text="Carpeta raíz:", font=(SANS, 8, "bold"),
                 fg=TEXT_DIM, bg=SURFACE).pack(side="left")

        tk.Entry(
            raiz_frame, textvariable=carpeta_sel,
            font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0, insertbackground=ACCENT,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
        ).pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 8))

        def elegir_raiz():
            ruta = filedialog.askdirectory(title="Carpeta raíz del perfil", parent=win)
            if ruta:
                carpeta_sel.set(ruta)

        FlatButton(raiz_frame, text="Elegir", command=elegir_raiz,
                   bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=10, ipady=5)

        # ── Cuerpo principal — dos paneles ────────────────────
        body = tk.Frame(win, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # Panel izquierdo — carpetas del mapa
        left = tk.Frame(body, bg=SURFACE, padx=12, pady=12)
        left.pack(side="left", fill="both", expand=False, padx=(0, 8))
        left.configure(width=200)
        left.pack_propagate(False)

        tk.Label(left, text="CARPETAS", font=(SANS, 8, "bold"),
                 fg=TEXT_DIM, bg=SURFACE).pack(anchor="w", pady=(0, 6))

        lb_carpetas = tk.Listbox(
            left, font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0, selectbackground=ACCENT2,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2, activestyle="none",
        )
        lb_carpetas.pack(fill="both", expand=True)

        # Panel derecho — extensiones
        right = tk.Frame(body, bg=SURFACE, padx=12, pady=12)
        right.pack(side="left", fill="both", expand=True)

        lbl_exts = tk.Label(right, text="Selecciona una carpeta",
                             font=(SANS, 8, "bold"), fg=TEXT_DIM, bg=SURFACE)
        lbl_exts.pack(anchor="w", pady=(0, 6))

        # Catálogo con checkboxes
        cat_frame = tk.Frame(right, bg=SURFACE2)
        cat_frame.pack(fill="both", expand=True)

        cat_canvas = tk.Canvas(cat_frame, bg=SURFACE2, highlightthickness=0)
        cat_scroll = tk.Scrollbar(cat_frame, command=cat_canvas.yview)
        cat_canvas.configure(yscrollcommand=cat_scroll.set)
        cat_scroll.pack(side="right", fill="y")
        cat_canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(cat_canvas, bg=SURFACE2)
        cat_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cat_canvas.configure(
            scrollregion=cat_canvas.bbox("all")
        ))

        checks: dict[str, tk.BooleanVar] = {}

        lb_exts_custom = tk.Listbox(
            right, font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0, selectbackground=ACCENT2,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2, activestyle="none", height=3,
        )

        # ── Helpers de carpetas/extensiones ──────────────────
        def recargar_carpetas_mapa():
            lb_carpetas.delete(0, "end")
            for c in sorted(mapa_local.keys()):
                lb_carpetas.insert("end", c)

        def recargar_panel_exts(carpeta: str) -> None:
            lbl_exts.configure(text=f"Extensiones en: {carpeta}")
            catalogo = config_manager.obtener_catalogo()
            exts_carpeta = set(mapa_local.get(carpeta, []))

            # Limpiar checks anteriores
            for w in inner.winfo_children():
                w.destroy()
            checks.clear()

            # Checkboxes del catálogo
            tk.Label(inner, text="Del catálogo:", font=(SANS, 8, "bold"),
                     fg=TEXT_DIM, bg=SURFACE2).pack(anchor="w", padx=8, pady=(6, 2))

            for grupo, exts in catalogo.items():
                tk.Label(inner, text=grupo, font=(SANS, 8, "bold"),
                         fg=ACCENT, bg=SURFACE2).pack(anchor="w", padx=8, pady=(4, 0))
                for ext in exts:
                    var = tk.BooleanVar(value=ext in exts_carpeta)
                    checks[ext] = var
                    tk.Checkbutton(
                        inner, text=ext, variable=var,
                        font=(MONO, 9), fg=TEXT, bg=SURFACE2,
                        activebackground=SURFACE2, selectcolor=SURFACE,
                        highlightthickness=0,
                        command=lambda e=ext, v=var, c=carpeta: toggle_ext(e, v, c),
                    ).pack(anchor="w", padx=16)

            # Extensiones personalizadas (no están en el catálogo)
            tk.Label(inner, text="Personalizadas:", font=(SANS, 8, "bold"),
                     fg=TEXT_DIM, bg=SURFACE2).pack(anchor="w", padx=8, pady=(8, 2))

            exts_catalogo = {e for exts in catalogo.values() for e in exts}
            personalizadas = [e for e in exts_carpeta if e not in exts_catalogo]

            lb_exts_custom.delete(0, "end")
            for e in sorted(personalizadas):
                lb_exts_custom.insert("end", e)
            lb_exts_custom.pack(fill="x", padx=8, pady=(0, 4))

        def toggle_ext(ext: str, var: tk.BooleanVar, carpeta: str) -> None:
            exts = mapa_local.setdefault(carpeta, [])
            if var.get():
                if ext not in exts:
                    exts.append(ext)
                # Quitarla de otras carpetas
                for c, lista in mapa_local.items():
                    if c != carpeta and ext in lista:
                        lista.remove(ext)
            else:
                if ext in exts:
                    exts.remove(ext)

        def on_carpeta_select(event=None):
            sel = lb_carpetas.curselection()
            if sel:
                c = lb_carpetas.get(sel[0])
                carpeta_mapa.set(c)
                recargar_panel_exts(c)

        lb_carpetas.bind("<<ListboxSelect>>", on_carpeta_select)

        # ── Botones carpetas ──────────────────────────────────
        bc = tk.Frame(left, bg=SURFACE)
        bc.pack(fill="x", pady=(8, 0))

        def nueva_carpeta_mapa():
            nombre = simpledialog.askstring("Nueva carpeta", "Nombre:", parent=win)
            if not nombre:
                return
            nombre = nombre.strip()
            if nombre in mapa_local:
                messagebox.showwarning("Aviso", f"'{nombre}' ya existe.", parent=win)
                return
            mapa_local[nombre] = []
            recargar_carpetas_mapa()

        def renombrar_carpeta_mapa():
            carpeta = carpeta_mapa.get()
            if not carpeta:
                return
            nuevo = simpledialog.askstring(
                "Renombrar", f"Nuevo nombre para '{carpeta}':",
                parent=win, initialvalue=carpeta,
            )
            if not nuevo or nuevo == carpeta:
                return
            nuevo = nuevo.strip()
            mapa_local[nuevo] = mapa_local.pop(carpeta)
            carpeta_mapa.set(nuevo)
            recargar_carpetas_mapa()
            recargar_panel_exts(nuevo)

        def eliminar_carpeta_mapa():
            carpeta = carpeta_mapa.get()
            if not carpeta:
                return
            if not messagebox.askyesno(
                "Confirmar", f"¿Eliminar '{carpeta}'?", parent=win
            ):
                return
            mapa_local.pop(carpeta, None)
            carpeta_mapa.set("")
            lbl_exts.configure(text="Selecciona una carpeta")
            for w in inner.winfo_children():
                w.destroy()
            lb_exts_custom.pack_forget()
            recargar_carpetas_mapa()

        FlatButton(bc, text="+ Nueva",     command=nueva_carpeta_mapa,    bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=6, ipady=4, padx=(0, 4))
        FlatButton(bc, text="✎ Renombrar", command=renombrar_carpeta_mapa, bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=6, ipady=4, padx=(0, 4))
        FlatButton(bc, text="✕ Eliminar",  command=eliminar_carpeta_mapa,  bg=SURFACE2, fg=RED,  hover=SURFACE2).pack(side="left", ipadx=6, ipady=4)

        # ── Botones ext personalizadas ────────────────────────
        be = tk.Frame(right, bg=SURFACE)
        be.pack(fill="x", pady=(4, 0))

        ext_entry = tk.Entry(
            be, font=(MONO, 9), fg=TEXT, bg=SURFACE2,
            relief="flat", bd=0, insertbackground=ACCENT,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SURFACE2,
        )
        ext_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))

        def agregar_ext_custom():
            carpeta = carpeta_mapa.get()
            if not carpeta:
                messagebox.showwarning("Aviso", "Selecciona una carpeta primero.", parent=win)
                return
            ext = ext_entry.get().strip().lower()
            if not ext:
                return
            if not ext.startswith("."):
                ext = "." + ext
            exts = mapa_local.setdefault(carpeta, [])
            if ext not in exts:
                exts.append(ext)
            ext_entry.delete(0, "end")
            recargar_panel_exts(carpeta)

        def quitar_ext_custom():
            carpeta = carpeta_mapa.get()
            if not carpeta:
                return
            sel = lb_exts_custom.curselection()
            if not sel:
                return
            ext = lb_exts_custom.get(sel[0])
            mapa_local.get(carpeta, []).remove(ext)
            recargar_panel_exts(carpeta)

        FlatButton(be, text="+ Agregar", command=agregar_ext_custom, bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=8, ipady=5, padx=(0, 4))
        FlatButton(be, text="✕ Quitar",  command=quitar_ext_custom,  bg=SURFACE2, fg=RED,  hover=SURFACE2).pack(side="left", ipadx=8, ipady=5)

        # ── Barra inferior ────────────────────────────────────
        bot = tk.Frame(win, bg=BG)
        bot.pack(fill="x", padx=16, pady=(0, 16))

        def guardar():
            nombre = perfil_sel.get()
            if not nombre:
                messagebox.showwarning("Aviso", "Crea o selecciona un perfil primero.", parent=win)
                return
            config_manager.guardar_perfil(nombre, carpeta_sel.get() or None, mapa_local)
            config_manager.establecer_perfil_activo(nombre)
            # Cargar carpeta raíz en la app principal
            raiz = carpeta_sel.get().strip()
            if raiz:
                self.carpeta_actual.set(raiz)
            self._log("INFO", f"✓ Perfil '{nombre}' guardado y activado.")
            win.destroy()

        FlatButton(bot, text="⎘ Duplicar perfil", command=duplicar_perfil,
                   bg=SURFACE2, fg=TEXT, hover=ACCENT2).pack(side="left", ipadx=12, ipady=8)
        FlatButton(bot, text="💾 Guardar y activar", command=guardar,
                   bg=GREEN, fg=BG, hover="#2db870").pack(side="right", ipadx=16, ipady=8)

        # Cargar perfil activo al abrir
        activo = config_manager.obtener_perfil_activo()
        if activo and activo in config_manager.listar_perfiles():
            cargar_perfil(activo)
        elif config_manager.listar_perfiles():
            cargar_perfil(config_manager.listar_perfiles()[0])