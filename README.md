# 🛡️ FileWarden — Organizador Automático de Archivos

**FileWarden** es una aplicación de escritorio para Windows que monitorea carpetas en tiempo real y organiza automáticamente los archivos según reglas definidas por el usuario o por categorías inteligentes predefinidas. Construido con Python 3, PyQt6 y Watchdog.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
  - [Inicio Rápido](#inicio-rápido)
  - [Panel de Centinelas](#panel-de-centinelas-izquierdo)
  - [Tabla de Reglas](#tabla-de-reglas-derecho-superior)
  - [Panel de Registro](#panel-de-registro-derecho-inferior)
  - [Barra Superior](#barra-superior)
  - [Barra de Estado](#barra-de-estado-inferior)
- [Auto-Organización Inteligente](#-auto-organización-inteligente)
- [Categorías de Archivos](#-categorías-de-archivos)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Configuración Persistente](#-configuración-persistente)
- [Resolución de Problemas](#-resolución-de-problemas)

---

## ✨ Características

### Monitoreo en Tiempo Real
- Vigilancia continua de carpetas usando la librería **Watchdog**.
- Detecta archivos creados, modificados y movidos (arrastrar y soltar desde el explorador).
- Escaneo inicial automático al activar el observador para procesar archivos ya existentes.

### Reglas Personalizadas
- Crea reglas por extensión de archivo con destino y acción configurables.
- Soporta **múltiples extensiones** en una sola regla separadas por comas (ej: `jpg, png, gif`).
- Acciones disponibles: **mover**, **copiar** y **renombrar**.
- Soporte para patrones de renombrado con variables (`{stem}`, `{suffix}`, `{date}`).

### Auto-Organización Inteligente
- **Modo continuo (toggle ON/OFF):** Los archivos nuevos que no coincidan con ninguna regla se clasifican automáticamente en subcarpetas por tipo.
- **Modo manual (botón):** Organiza de una sola vez todos los archivos sueltos en la carpeta vigilada.
- 9 categorías predefinidas con más de 90 extensiones reconocidas.

### Interfaz Profesional
- Peso de cada carpeta vigilada en tiempo real (calculado en hilo secundario para no bloquear la UI).
- Indicador `[AUTO]` junto a carpetas con auto-organización activa.
- Contadores de estadísticas de sesión: archivos movidos y errores.
- Botón **Deshacer** para revertir la última operación de archivo.
- Panel de registro (log) con marcas de tiempo, exportable a `.txt`.
- Barra de estado inferior con notificaciones temporales de 5 segundos.

### Seguridad y Robustez
- Verificación de que el archivo está listo antes de procesarlo (no está siendo escrito por otro programa).
- Ignora automáticamente archivos temporales (`.crdownload`, `.part`, `.tmp`, etc.).
- Generación de nombres únicos para evitar sobrescribir archivos existentes.
- Toda la configuración se guarda automáticamente y persiste entre sesiones.

---

## 📦 Requisitos

| Componente | Versión         |
|------------|-----------------|
| Python     | 3.11 o superior |
| PyQt6      | ≥ 6.6.0        |
| watchdog   | ≥ 4.0.0        |
| SO         | Windows 10/11   |

---

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <repositorio>
cd "sentinela watchdog"
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat
```

### 4. Instalar dependencias

```bash
pip install -r filewarden/requirements.txt
```

### 5. Ejecutar la aplicación

```bash
cd filewarden
python main.py
```

> **Nota:** Asegúrate de ejecutar `python main.py` desde dentro de la carpeta `filewarden/`, ya que los imports relativos dependen de esa ubicación como directorio de trabajo.

---

## 🖥️ Uso

### Inicio Rápido

1. Abre FileWarden ejecutando `python main.py`.
2. Haz clic en **➕ Añadir** para seleccionar una carpeta a vigilar.
3. **(Opción A)** Activa la **Auto-Organización** para clasificación automática por tipo.
4. **(Opción B)** Añade reglas personalizadas en la tabla de la derecha.
5. Presiona **▶ Iniciar Observador** para activar el monitoreo en tiempo real.

---

### Panel de Centinelas (Izquierdo)

El panel izquierdo muestra las carpetas que están siendo vigiladas. Cada entrada muestra:

```
🟢 Downloads [AUTO] (1.5 GB)
🔴 Desktop (342.7 MB)
```

- 🟢 / 🔴 — Estado activo o inactivo del centinela.
- `[AUTO]` — Indica que la auto-organización continua está habilitada.
- `(1.5 GB)` — Peso actual de la carpeta (se actualiza cada 10 segundos en segundo plano).

**Botones del panel:**

| Botón | Función |
|-------|---------|
| ➕ Añadir | Selecciona una nueva carpeta para vigilar |
| ⏯ Activar | Alterna el estado activo/inactivo del centinela seleccionado |
| 🗑 Borrar | Elimina el centinela de la lista |
| 🔄 Auto-Organización: ON/OFF | Activa o desactiva la clasificación automática continua |
| 🗂 Organizar Ahora (Manual) | Organiza todos los archivos sueltos de la carpeta inmediatamente |

---

### Tabla de Reglas (Derecho Superior)

Al seleccionar un centinela, la tabla muestra las reglas configuradas:

| Extensión | Carpeta Destino | Acción |
|-----------|-----------------|--------|
| `.pdf, .docx` | `C:\Users\...\Documentos` | move |
| `.jpg, .png, .gif` | `C:\Users\...\Fotos` | copy |

- **Extensión:** Puede contener una o varias extensiones separadas por comas.
- **Carpeta Destino:** Haz doble clic en la celda para abrir un selector de carpeta.
- **Acción:** `move` (mover), `copy` (copiar) o `rename` (renombrar).

**Botones:**

| Botón | Función |
|-------|---------|
| Añadir fila | Agrega una regla nueva en blanco |
| Eliminar fila seleccionada | Borra la regla seleccionada |
| Guardar reglas | Aplica los cambios de la tabla al centinela |

> **Prioridad:** Las reglas personalizadas siempre tienen prioridad sobre la auto-organización. Si un archivo `.pdf` coincide con una regla manual, se usará esa regla. Si no coincide con ninguna y la auto-organización está activa, se clasificará en `📄 Documentos`.

---

### Panel de Registro (Derecho Inferior)

Muestra un historial de todas las operaciones realizadas durante la sesión con marcas de tiempo:

```
[14:05:32] Mover: informe.pdf → C:\Users\...\Documentos
[14:05:33] Organizar: cancion.mp3 → 🎵 Música
[14:05:34] ERROR: Error de permisos al operar video.mp4
```

| Botón | Función |
|-------|---------|
| Limpiar log | Borra todo el contenido del registro |
| Exportar log | Guarda el registro en un archivo `.txt` |

---

### Barra Superior

```
⏹ Detenido  |  📁 12 movido(s)  |  ⚠️ 1 error(es)     [⏪ Deshacer]  [▶ Iniciar Observador]
```

- **Estado:** Muestra si el observador está detenido o en ejecución.
- **Estadísticas:** Conteo acumulado de archivos movidos y errores en la sesión actual.
- **⏪ Deshacer:** Revierte la última operación de archivo (devuelve el archivo a su ubicación original).
- **▶ / ⏹:** Inicia o detiene el monitoreo en tiempo real.

---

### Barra de Estado (Inferior)

Muestra notificaciones temporales (5 segundos) cada vez que se realiza una operación:

```
Mover: foto_vacaciones.jpg → C:\Users\...\📷 Imágenes
```

---

## 🗂️ Auto-Organización Inteligente

FileWarden clasifica automáticamente los archivos en subcarpetas dentro de la misma carpeta vigilada según su tipo.

### Modo Continuo (Auto-Organización ON)

1. Selecciona un centinela en el panel izquierdo.
2. Presiona **🔄 Auto-Organización: OFF** para cambiarlo a **ON**.
3. Inicia el observador con **▶ Iniciar Observador**.
4. A partir de ahora, cualquier archivo nuevo que llegue a la carpeta y no tenga una regla específica será movido automáticamente a su subcarpeta por tipo.

### Modo Manual (Organizar Ahora)

1. Selecciona un centinela.
2. Presiona **🗂 Organizar Ahora (Manual)**.
3. Todos los archivos sueltos (no en subcarpetas) serán clasificados inmediatamente.

---

## 📁 Categorías de Archivos

| Categoría | Extensiones soportadas |
|-----------|----------------------|
| 📷 Imágenes | jpg, jpeg, png, gif, bmp, svg, webp, ico, tiff, tif, raw, heic, psd, ai |
| 🎬 Videos | mp4, mkv, avi, mov, wmv, flv, webm, m4v, mpg, mpeg, ts, vob |
| 🎵 Música | mp3, wav, flac, aac, ogg, wma, m4a, opus, aiff |
| 📄 Documentos | pdf, docx, doc, xlsx, xls, pptx, ppt, odt, ods, odp, rtf, epub |
| 📝 Texto | txt, md, rst, log, csv, ini, cfg, toml, yaml, yml |
| 💾 Programas | exe, msi, apk, deb, appimage, bat, sh, cmd |
| 🗜️ Archivos | zip, rar, 7z, tar, gz, bz2, xz, iso |
| 💻 Código | py, js, ts, html, css, java, cpp, c, cs, json, xml, php, rb, go, rs, kt, swift |
| 📂 Otros | Cualquier extensión no reconocida |

---

## 🏗️ Arquitectura del Proyecto

```
filewarden/
├── main.py                  # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Este archivo
│
├── core/                    # Lógica de negocio
│   ├── rules.py             # Modelos de datos (Sentinel, Rule)
│   ├── watcher.py           # Hilo de monitoreo con Watchdog
│   ├── file_ops.py          # Operaciones seguras de archivos
│   └── organizer.py         # Motor de auto-organización por categoría
│
└── ui/                      # Interfaz gráfica (PyQt6)
    ├── main_window.py       # Ventana principal y orquestación
    ├── sentinel_panel.py    # Panel de gestión de centinelas
    ├── rules_table.py       # Tabla editable de reglas
    └── log_panel.py         # Panel de registro de eventos
```

### Flujo de Datos

```
┌─────────────────┐        ┌──────────────────┐
│  Watchdog        │        │  Auto-Organizer  │
│  Observer        │        │                  │
│  (hilo externo)  │        │  organizer.py    │
└────────┬─────────┘        └────────┬─────────┘
         │ eventos                    │ batch
         ▼                            ▼
┌─────────────────────────────────────────────────┐
│           FileWatcherThread (QThread)            │
│   - Evalúa reglas del usuario primero            │
│   - Si auto_organize=True y no hay regla →       │
│     determina categoría automáticamente          │
│   - Escanea archivos existentes al iniciar       │
└────────────────────┬────────────────────────────┘
                     │ señales Qt
                     ▼
┌─────────────────────────────────────────────────┐
│               MainWindow (UI)                    │
│   - Actualiza log, estadísticas, barra de estado │
│   - Gestiona historial de Deshacer               │
│   - Persiste configuración en JSON               │
└──────────────────────────────────────────────────┘
```

---

## 💾 Configuración Persistente

La configuración se almacena automáticamente en:

```
%USERPROFILE%\.filewarden\config.json
```

Los logs del sistema se guardan en:

```
%USERPROFILE%\.filewarden\logs\filewarden.log
```

### Estructura del `config.json`

```json
{
    "sentinels": [
        {
            "watch_path": "C:\\Users\\usuario\\Downloads",
            "active": true,
            "auto_organize": true,
            "rules": [
                {
                    "extension": ".pdf, .docx",
                    "destination": "C:\\Users\\usuario\\Documentos",
                    "action": "move",
                    "rename_pattern": ""
                }
            ]
        }
    ]
}
```

---

## 🔧 Resolución de Problemas

### La aplicación no inicia

- Asegúrate de estar dentro de la carpeta `filewarden/` al ejecutar `python main.py`.
- Verifica que `PyQt6` y `watchdog` estén instalados en el mismo intérprete de Python que usas para ejecutar.

```bash
pip install PyQt6 watchdog
```

### Los archivos no se mueven

- Verifica que el centinela esté **activo** (🟢) y que hayas presionado **▶ Iniciar Observador**.
- Si usas reglas personalizadas, asegúrate de haber presionado **"Guardar reglas"** después de editar la tabla.
- Si usas auto-organización, verifica que el botón diga **Auto-Organización: ON**.

### La interfaz se congela

- El cálculo de peso de carpetas se realiza en un hilo secundario y no debería bloquear la interfaz. Si vigilas una carpeta con cientos de miles de archivos, el cálculo puede tardar pero la UI seguirá respondiendo.

### Errores de permisos

- Algunos archivos del sistema o de programas en ejecución no pueden ser movidos. FileWarden registrará estos errores en el panel de log sin interrumpir el monitoreo de los demás archivos.

---

## 📄 Licencia

Este proyecto es de uso personal y educativo.

---

*FileWarden — Mantén tus archivos en orden, automáticamente.* 🛡️
