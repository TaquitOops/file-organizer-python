# Organizador de Archivos

## Descripción
Aplicación desarrollada en Python que organiza automáticamente archivos en carpetas según su tipo (documentos, imágenes, videos, etc.). Incluye monitoreo en tiempo real y una interfaz gráfica modular.

## Características
- Organización automática por extensión de archivo (+70 extensiones soportadas)
- Monitoreo en tiempo real de carpetas con Watchdog
- Selección de carpetas a ignorar desde la interfaz
- Manejo de descargas en curso (`.crdownload`, `.part`, etc.)
- Resolución automática de archivos duplicados
- Interfaz gráfica modular con tema oscuro
- Registro de actividad en tiempo real

## Tecnologías
- Python 3.13
- Watchdog
- Tkinter

## Instalación

Clonar el repositorio:
```bash
git clone https://github.com/TaquitOops/file-organizer-python.git
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar el programa:
```bash
python main.py
```

1. Selecciona la carpeta que deseas organizar
2. (Opcional) Agrega carpetas a ignorar dentro de ella
3. Presiona **INICIAR** — el programa organizará los archivos existentes y monitoreará cambios en tiempo real

## Estructura del proyecto

```
file-organizer-python/
├── main.py               # Punto de entrada
├── config.py             # Constantes, colores y mapa de extensiones
├── logic.py              # Lógica de organización (independiente de GUI)
├── monitor.py            # Observador de carpetas con Watchdog
├── requirements.txt
└── gui/
    ├── __init__.py
    ├── app.py            # Ventana principal
    ├── widgets.py        # Componentes reutilizables
    ├── panel_carpeta.py  # Selector de carpeta raíz
    ├── panel_ignoradas.py# Panel de carpetas ignoradas
    ├── panel_controles.py# Botones y estadísticas
    └── panel_log.py      # Área de actividad
```

## Autor
Angel Marmolejo