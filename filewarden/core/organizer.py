"""
Módulo para la organización automática de archivos por categoría.
"""
import shutil
from pathlib import Path
from typing import Callable, Optional

# Mapa de extensión → nombre de carpeta de categoría
CATEGORY_MAP: dict[str, str] = {
    # Imágenes
    ".jpg": "📷 Imágenes", ".jpeg": "📷 Imágenes", ".png": "📷 Imágenes",
    ".gif": "📷 Imágenes", ".bmp": "📷 Imágenes", ".svg": "📷 Imágenes",
    ".webp": "📷 Imágenes", ".ico": "📷 Imágenes", ".tiff": "📷 Imágenes",
    ".tif": "📷 Imágenes", ".raw": "📷 Imágenes", ".heic": "📷 Imágenes",
    ".psd": "📷 Imágenes", ".ai": "📷 Imágenes",
    # Videos
    ".mp4": "🎬 Videos", ".mkv": "🎬 Videos", ".avi": "🎬 Videos",
    ".mov": "🎬 Videos", ".wmv": "🎬 Videos", ".flv": "🎬 Videos",
    ".webm": "🎬 Videos", ".m4v": "🎬 Videos", ".mpg": "🎬 Videos",
    ".mpeg": "🎬 Videos", ".ts": "🎬 Videos", ".vob": "🎬 Videos",
    # Música
    ".mp3": "🎵 Música", ".wav": "🎵 Música", ".flac": "🎵 Música",
    ".aac": "🎵 Música", ".ogg": "🎵 Música", ".wma": "🎵 Música",
    ".m4a": "🎵 Música", ".opus": "🎵 Música", ".aiff": "🎵 Música",
    # Documentos
    ".pdf": "📄 Documentos", ".docx": "📄 Documentos", ".doc": "📄 Documentos",
    ".xlsx": "📄 Documentos", ".xls": "📄 Documentos", ".pptx": "📄 Documentos",
    ".ppt": "📄 Documentos", ".odt": "📄 Documentos", ".ods": "📄 Documentos",
    ".odp": "📄 Documentos", ".rtf": "📄 Documentos", ".epub": "📄 Documentos",
    # Texto plano
    ".txt": "📝 Texto", ".md": "📝 Texto", ".rst": "📝 Texto",
    ".log": "📝 Texto", ".csv": "📝 Texto", ".ini": "📝 Texto",
    ".cfg": "📝 Texto", ".toml": "📝 Texto", ".yaml": "📝 Texto", ".yml": "📝 Texto",
    # Programas e instaladores
    ".exe": "💾 Programas", ".msi": "💾 Programas", ".apk": "💾 Programas",
    ".deb": "💾 Programas", ".appimage": "💾 Programas", ".bat": "💾 Programas",
    ".sh": "💾 Programas", ".cmd": "💾 Programas",
    # Archivos comprimidos
    ".zip": "🗜️ Archivos", ".rar": "🗜️ Archivos", ".7z": "🗜️ Archivos",
    ".tar": "🗜️ Archivos", ".gz": "🗜️ Archivos", ".bz2": "🗜️ Archivos",
    ".xz": "🗜️ Archivos", ".iso": "🗜️ Archivos",
    # Código
    ".py": "💻 Código", ".js": "💻 Código", ".ts": "💻 Código",
    ".html": "💻 Código", ".css": "💻 Código", ".java": "💻 Código",
    ".cpp": "💻 Código", ".c": "💻 Código", ".cs": "💻 Código",
    ".json": "💻 Código", ".xml": "💻 Código", ".php": "💻 Código",
    ".rb": "💻 Código", ".go": "💻 Código", ".rs": "💻 Código",
    ".kt": "💻 Código", ".swift": "💻 Código",
}

OTHER_CATEGORY = "📂 Otros"


def get_category(extension: str) -> str:
    """Devuelve el nombre de la carpeta de categoría para la extensión dada."""
    return CATEGORY_MAP.get(extension.lower(), OTHER_CATEGORY)


def get_folder_size(path: Path) -> int:
    """
    Calcula el tamaño total de una carpeta en bytes, sumando todos sus archivos recursivamente.
    """
    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """
    Convierte bytes a formato legible por humanos.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"


def _get_unique_dest(destination_dir: Path, filename: str) -> Path:
    """Genera una ruta de destino única para evitar sobrescribir archivos."""
    dest_path = destination_dir / filename
    if not dest_path.exists():
        return dest_path
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        new_dest = destination_dir / f"{stem}_{counter}{suffix}"
        if not new_dest.exists():
            return new_dest
        counter += 1


def auto_organize(
    watch_path: Path,
    log_callback: Callable[[str], None],
    error_callback: Callable[[str], None],
) -> list[tuple[Path, Path]]:
    """
    Organiza automáticamente todos los archivos de `watch_path` moviéndolos
    a subcarpetas por categoría.

    Devuelve una lista de tuplas (origen_original, destino_nuevo) para el historial de deshacer.
    """
    history: list[tuple[Path, Path]] = []

    if not watch_path.exists() or not watch_path.is_dir():
        error_callback(f"La ruta no existe o no es una carpeta: {watch_path}")
        return history

    # Solo archivos directamente en la carpeta (no recursivo para no tocar subcarpetas)
    files = [item for item in watch_path.iterdir() if item.is_file()]

    if not files:
        log_callback(f"Auto-organizar: No hay archivos en '{watch_path.name}'.")
        return history

    moved_count = 0
    for file_path in files:
        category = get_category(file_path.suffix)
        dest_dir = watch_path / category
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = _get_unique_dest(dest_dir, file_path.name)
            shutil.move(str(file_path), str(dest_path))
            history.append((dest_path, file_path))  # (nuevo_lugar, lugar_original)
            log_callback(f"Organizar: {file_path.name} → {category}")
            moved_count += 1
        except Exception as e:
            error_callback(f"Error al organizar {file_path.name}: {e}")

    log_callback(f"✅ Auto-organización completada: {moved_count} archivo(s) procesados en '{watch_path.name}'.")
    return history
