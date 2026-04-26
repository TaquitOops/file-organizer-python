"""
main.py  —  Punto de entrada del Organizador de Archivos.

Ejecutar:
    python main.py
"""
import logging

from gui.app import OrganizadorApp


def main() -> None:
    # Logging base (la GUI añade su propio handler en OrganizadorApp._setup_logger)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    app = OrganizadorApp()
    app.mainloop()


if __name__ == "__main__":
    main()