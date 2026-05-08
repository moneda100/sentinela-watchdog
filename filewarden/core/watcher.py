"""
Módulo para monitorear el sistema de archivos usando watchdog.
"""
from pathlib import Path
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from core.rules import Sentinel
from core.file_ops import TEMP_EXTENSIONS, TEMP_PREFIXES, is_file_ready, safe_file_operation
from core.organizer import get_category

class WardenEventHandler(FileSystemEventHandler):
    """
    Manejador de eventos para watchdog. Evalúa las reglas y procesa los archivos.
    """
    def __init__(self, sentinel: Sentinel, log_signal: pyqtSignal, error_signal: pyqtSignal):
        super().__init__()
        self.sentinel = sentinel
        self.log_signal = log_signal
        self.error_signal = error_signal
        
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._process_path(event.src_path)
        
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._process_path(event.src_path)
            
    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            self._process_path(event.dest_path)
        
    def _process_path(self, path_str: str):
        file_path = Path(path_str)
        
        if not file_path.exists():
            return
            
        # Ignorar archivos temporales
        if file_path.suffix.lower() in TEMP_EXTENSIONS:
            return
        if file_path.name.startswith(TEMP_PREFIXES):
            return
            
        # Evaluar reglas
        matched_rule = None
        for rule in self.sentinel.rules:
            if rule.matches(file_path.suffix):
                matched_rule = rule
                break
                
        # Si no hay regla pero la auto-organización está activa, determinar categoría
        destination_dir = None
        action = "move"
        rename_pattern = ""
        
        if matched_rule:
            destination_dir = matched_rule.destination
            action = matched_rule.action
            rename_pattern = matched_rule.rename_pattern
        elif self.sentinel.auto_organize:
            category = get_category(file_path.suffix)
            destination_dir = self.sentinel.watch_path / category
        else:
            return
            
        # Esperar a que el archivo esté listo
        if not is_file_ready(file_path):
            self.error_signal.emit(f"Tiempo de espera agotado para acceder a: {file_path.name}")
            return
            
        try:
            # Asegurar que el directorio destino existe
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Ejecutar operación
            log_msg = safe_file_operation(
                source=file_path,
                destination_dir=destination_dir,
                action=action,
                rename_pattern=rename_pattern
            )
            self.log_signal.emit(log_msg)
        except Exception as e:
            self.error_signal.emit(str(e))

class FileWatcherThread(QThread):
    """
    Hilo de PyQt que administra el observador de watchdog.
    """
    file_moved = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, sentinels: List[Sentinel]):
        super().__init__()
        self.sentinels = sentinels
        self.observer = None
        
    def run(self):
        self.observer = Observer()
        handlers = []
        
        for sentinel in self.sentinels:
            if sentinel.active and sentinel.watch_path.exists() and sentinel.watch_path.is_dir():
                handler = WardenEventHandler(sentinel, self.file_moved, self.error_occurred)
                self.observer.schedule(handler, str(sentinel.watch_path), recursive=False)
                handlers.append(handler)
                
        self.observer.start()
        
        # Escaneo inicial de archivos existentes
        for handler in handlers:
            try:
                for item in handler.sentinel.watch_path.iterdir():
                    if item.is_file():
                        handler._process_path(str(item))
            except Exception as e:
                self.error_occurred.emit(f"Error en escaneo inicial de {handler.sentinel.watch_path.name}: {e}")
                
        try:
            while not self.isInterruptionRequested():
                QThread.msleep(500)
        finally:
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            
    def stop(self):
        """Detiene el hilo y el observador."""
        self.requestInterruption()
        self.wait()
