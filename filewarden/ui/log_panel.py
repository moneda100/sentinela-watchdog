"""
Panel para visualizar el log de eventos de FileWarden.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
import datetime
from pathlib import Path

class LogPanel(QWidget):
    """
    Panel de solo lectura para mostrar el log de operaciones y errores.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de texto
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Limpiar log")
        self.btn_export = QPushButton("Exportar log")
        
        self.btn_clear.clicked.connect(self.clear_log)
        self.btn_export.clicked.connect(self.export_log)
        
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def log_action(self, message: str):
        """Añade un mensaje de éxito al log."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f"[{timestamp}] {message}")
        self._scroll_to_bottom()
        
    def log_error(self, message: str):
        """Añade un mensaje de error al log en rojo."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f"<span style='color:red;'>[{timestamp}] ERROR: {message}</span>")
        self._scroll_to_bottom()
        
    def clear_log(self):
        """Limpia todo el texto del log."""
        self.text_edit.clear()
        
    def export_log(self):
        """Abre un diálogo para guardar el log en un archivo de texto."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar log", "", "Archivos de texto (*.txt);;Todos los archivos (*)"
        )
        if file_path:
            try:
                Path(file_path).write_text(self.text_edit.toPlainText(), encoding='utf-8')
            except Exception as e:
                self.log_error(f"No se pudo exportar el log: {e}")
                
    def _scroll_to_bottom(self):
        """Desplaza automáticamente al final del texto."""
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
