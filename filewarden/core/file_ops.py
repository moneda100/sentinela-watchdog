"""
Módulo para realizar operaciones de archivo (mover, copiar, renombrar) de manera segura.
"""
import shutil
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

TEMP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download", 
                   ".partial", ".opdownload"}
TEMP_PREFIXES = ("~$", ".~")

def is_file_ready(path: Path, timeout: float = 5.0) -> bool:
    """
    Verifica si un archivo está listo para ser procesado.
    Intenta abrir el archivo en modo lectura exclusiva.
    Si falla, espera y reintenta hasta que se agote el timeout.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Intenta abrir el archivo. En Windows, esto puede fallar si está en uso exclusivo por otro proceso.
            with path.open("rb"):
                pass
            # Comprobación de tamaño estable como heurística adicional
            initial_size = path.stat().st_size
            time.sleep(0.1)
            if path.stat().st_size == initial_size:
                return True
        except (PermissionError, OSError):
            time.sleep(0.5)
    return False

def get_unique_destination(destination_dir: Path, filename: str) -> Path:
    """
    Genera una ruta de destino única para evitar sobrescribir archivos.
    Añade un sufijo numérico si el archivo ya existe.
    """
    dest_path = destination_dir / filename
    if not dest_path.exists():
        return dest_path
        
    stem = dest_path.stem
    suffix = dest_path.suffix
    counter = 1
    
    while True:
        new_dest = destination_dir / f"{stem}_{counter}{suffix}"
        if not new_dest.exists():
            return new_dest
        counter += 1

def safe_file_operation(source: Path, destination_dir: Path, action: str, rename_pattern: str = "") -> str:
    """
    Ejecuta una operación de archivo (mover, copiar, renombrar) con manejo de errores.
    Devuelve un mensaje de log sobre la operación, o lanza una excepción.
    """
    if not source.exists():
        raise FileNotFoundError(f"El archivo origen no existe: {source}")
        
    if action == "rename" and rename_pattern:
        import datetime
        now = datetime.datetime.now()
        new_name = rename_pattern.replace("{stem}", source.stem) \
                                 .replace("{suffix}", source.suffix) \
                                 .replace("{date}", now.strftime("%Y%m%d"))
        if not new_name.endswith(source.suffix):
            new_name += source.suffix
        dest_path = get_unique_destination(destination_dir, new_name)
    else:
        dest_path = get_unique_destination(destination_dir, source.name)
        
    try:
        if action == "move":
            shutil.move(str(source), str(dest_path))
            return f"Mover: {source.name} -> {dest_path.parent}"
        elif action == "copy":
            shutil.copy2(str(source), str(dest_path))
            return f"Copiar: {source.name} -> {dest_path.parent}"
        elif action == "rename":
            shutil.move(str(source), str(dest_path))
            return f"Renombrar: {source.name} -> {dest_path.name}"
        else:
            raise ValueError(f"Acción desconocida: {action}")
    except PermissionError as e:
        raise PermissionError(f"Error de permisos al operar {source.name}: {e}")
    except shutil.Error as e:
        raise shutil.Error(f"Error de shutil al operar {source.name}: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado al operar {source.name}: {e}")
