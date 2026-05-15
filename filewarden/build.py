"""
Script de empaquetado de FileWarden con PyInstaller.
Genera un unico ejecutable .exe en la carpeta dist/.

Uso:
    python build.py
"""
import subprocess
import sys
import shutil
from pathlib import Path

# ── Configuracion ──────────────────────────────────────────────────────────────
APP_NAME    = "FileWarden"
APP_VERSION = "2.0.0"
MAIN_SCRIPT = "main.py"
ICON_PATH   = Path("assets") / "icon.ico"
DIST_DIR    = Path("dist")
BUILD_DIR   = Path("build")

# Datos extra a incluir: (origen, destino_dentro_del_exe)
DATAS = [
    ("assets", "assets"),
]

# Modulos ocultos que PyInstaller a veces no detecta automaticamente
HIDDEN_IMPORTS = [
    "PyQt6.QtSvg",
    "PyQt6.QtXml",
    "watchdog.observers",
    "watchdog.observers.polling",
    "watchdog.events",
]


# ── Funciones helper ───────────────────────────────────────────────────────────

def clean_previous():
    """Elimina artifacts de builds anteriores."""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Limpiado: {d}/")

    spec_file = Path(f"{APP_NAME}.spec")
    if spec_file.exists():
        spec_file.unlink()
        print(f"  Limpiado: {spec_file}")


def build():
    """Construye el ejecutable con PyInstaller."""
    print(f"\n{'='*60}")
    print(f"  FileWarden v{APP_VERSION} -- Build con PyInstaller")
    print(f"{'='*60}\n")

    print("Limpiando builds anteriores...")
    clean_previous()

    # ── Construir argumentos de PyInstaller ────────────────────────────────────
    args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        "--clean",
        "--noconfirm",
    ]

    # Icono
    if ICON_PATH.exists():
        args += [f"--icon={ICON_PATH}"]
        print(f"  Icono: {ICON_PATH}")
    else:
        print("  AVISO: Icono no encontrado, usando el predeterminado.")

    # Datos adicionales
    for src, dst in DATAS:
        if Path(src).exists():
            args += [f"--add-data={src};{dst}"]
            print(f"  Incluyendo: {src} -> {dst}")

    # Importaciones ocultas
    for imp in HIDDEN_IMPORTS:
        args += [f"--hidden-import={imp}"]

    args.append(MAIN_SCRIPT)

    print(f"\nEjecutando PyInstaller...\n")
    result = subprocess.run(args, check=False)

    if result.returncode == 0:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        size_mb = exe_path.stat().st_size / 1_048_576 if exe_path.exists() else 0
        print(f"\n{'='*60}")
        print(f"  Build exitoso!")
        print(f"  Ejecutable: {exe_path.resolve()}")
        print(f"  Tamano: {size_mb:.1f} MB")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"  ERROR en el build (codigo: {result.returncode})")
        print(f"  Revisa los mensajes anteriores para mas detalles.")
        print(f"{'='*60}\n")
        sys.exit(result.returncode)


if __name__ == "__main__":
    # Asegurar que corremos desde el directorio correcto
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)

    build()
