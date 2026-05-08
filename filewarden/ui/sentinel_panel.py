"""
Panel para gestionar la lista de centinelas.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QColor
from pathlib import Path

from core.rules import Sentinel
from core.organizer import get_folder_size, format_size, auto_organize

class SizeWorker(QThread):
    """Hilo para calcular tamaños de carpeta sin bloquear la UI."""
    finished = pyqtSignal(dict)

    def __init__(self, sentinels):
        super().__init__()
        self.sentinels = sentinels

    def run(self):
        results = {}
        for s in self.sentinels:
            try:
                size = get_folder_size(s.watch_path)
                results[str(s.watch_path)] = format_size(size)
            except:
                results[str(s.watch_path)] = "error"
        self.finished.emit(results)

class SentinelPanel(QWidget):
    """
    Panel lateral con la lista de centinelas configurados.
    """
    sentinel_selected = pyqtSignal(object)
    sentinels_changed = pyqtSignal()
    action_logged = pyqtSignal(str)
    error_logged = pyqtSignal(str)
    organized = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sentinels = []
        self.cached_sizes = {}
        self._setup_ui()

        # Timer para iniciar el trabajador de peso cada 10 segundos (menos frecuente para evitar carga)
        self._size_timer = QTimer(self)
        self._size_timer.setInterval(10000)
        self._size_timer.timeout.connect(self._start_size_worker)
        self._size_timer.start()
        
        self.size_worker = None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Añadir")
        self.btn_toggle = QPushButton("⏯ Activar")
        self.btn_del = QPushButton("🗑 Borrar")
        
        for b in [self.btn_add, self.btn_toggle, self.btn_del]:
            b.setMinimumHeight(30)

        self.btn_add.clicked.connect(self.add_sentinel)
        self.btn_toggle.clicked.connect(self.toggle_sentinel)
        self.btn_del.clicked.connect(self.delete_sentinel)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_toggle)
        btn_layout.addWidget(self.btn_del)
        layout.addLayout(btn_layout)

        # Botones de organización
        org_layout = QVBoxLayout()
        
        self.btn_auto_active = QPushButton("🔄 Auto-Organización: OFF")
        self.btn_auto_active.setCheckable(True)
        self.btn_auto_active.clicked.connect(self.toggle_auto_organize)
        self.btn_auto_active.setToolTip("Si está ON, los archivos sin reglas se moverán a subcarpetas por tipo automáticamente.")
        
        self.btn_organize_now = QPushButton("🗂 Organizar Ahora (Manual)")
        self.btn_organize_now.clicked.connect(self.auto_organize_selected)
        
        org_layout.addWidget(self.btn_auto_active)
        org_layout.addWidget(self.btn_organize_now)
        layout.addLayout(org_layout)

    def load_sentinels(self, sentinels):
        """Carga la lista inicial de centinelas."""
        self.sentinels = sentinels
        self.refresh_list()
        self._start_size_worker()

    def _start_size_worker(self):
        """Inicia el hilo de cálculo de tamaño."""
        if self.size_worker and self.size_worker.isRunning():
            return
        
        self.size_worker = SizeWorker(self.sentinels)
        self.size_worker.finished.connect(self._on_sizes_calculated)
        self.size_worker.start()

    def _on_sizes_calculated(self, results):
        """Recibe los tamaños calculados y actualiza la lista."""
        self.cached_sizes = results
        self.refresh_list()

    def _compute_label(self, sentinel: Sentinel) -> str:
        """Genera el texto del item."""
        emoji = "🟢" if sentinel.active else "🔴"
        size_str = self.cached_sizes.get(str(sentinel.watch_path), "calculando...")
        auto_str = "[AUTO]" if sentinel.auto_organize else ""
        return f"{emoji} {sentinel.watch_path.name} {auto_str} ({size_str})"

    def refresh_list(self):
        """Actualiza la vista de la lista."""
        current_path = None
        current_item = self.list_widget.currentItem()
        if current_item:
            s = current_item.data(Qt.ItemDataRole.UserRole)
            if s:
                current_path = s.watch_path

        self.list_widget.clear()
        for sentinel in self.sentinels:
            label = self._compute_label(sentinel)
            item = QListWidgetItem(label)
            item.setToolTip(str(sentinel.watch_path))
            item.setData(Qt.ItemDataRole.UserRole, sentinel)

            if sentinel.active:
                item.setForeground(QColor("#2ecc71"))
            else:
                item.setForeground(QColor("#e74c3c"))

            self.list_widget.addItem(item)
            if current_path and sentinel.watch_path == current_path:
                self.list_widget.setCurrentItem(item)
                self._update_auto_btn_state(sentinel)

    def _update_auto_btn_state(self, sentinel):
        if sentinel.auto_organize:
            self.btn_auto_active.setText("🔄 Auto-Organización: ON")
            self.btn_auto_active.setChecked(True)
            self.btn_auto_active.setStyleSheet("background-color: #2ecc71; color: white;")
        else:
            self.btn_auto_active.setText("🔄 Auto-Organización: OFF")
            self.btn_auto_active.setChecked(False)
            self.btn_auto_active.setStyleSheet("")

    def add_sentinel(self):
        """Abre diálogo para seleccionar nueva carpeta centinela."""
        dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta a monitorear")
        if dir_path:
            path = Path(dir_path)
            if any(s.watch_path == path for s in self.sentinels):
                return
            new_sentinel = Sentinel(watch_path=path, active=True)
            self.sentinels.append(new_sentinel)
            self.refresh_list()
            self.sentinels_changed.emit()
            self._start_size_worker()

    def toggle_sentinel(self):
        """Alterna el estado activo del centinela seleccionado."""
        current_item = self.list_widget.currentItem()
        if current_item:
            sentinel = current_item.data(Qt.ItemDataRole.UserRole)
            sentinel.active = not sentinel.active
            self.refresh_list()
            self.sentinels_changed.emit()

    def toggle_auto_organize(self):
        """Alterna el modo auto-organización continua para el centinela."""
        current_item = self.list_widget.currentItem()
        if current_item:
            sentinel = current_item.data(Qt.ItemDataRole.UserRole)
            sentinel.auto_organize = self.btn_auto_active.isChecked()
            self.refresh_list()
            self.sentinels_changed.emit()
            self._update_auto_btn_state(sentinel)

    def delete_sentinel(self):
        """Elimina el centinela seleccionado."""
        current_item = self.list_widget.currentItem()
        if current_item:
            sentinel = current_item.data(Qt.ItemDataRole.UserRole)
            self.sentinels.remove(sentinel)
            self.refresh_list()
            self.sentinels_changed.emit()

    def auto_organize_selected(self):
        """Auto-organiza los archivos del centinela seleccionado (manualmente)."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        sentinel = current_item.data(Qt.ItemDataRole.UserRole)
        history = auto_organize(
            sentinel.watch_path,
            log_callback=self.action_logged.emit,
            error_callback=self.error_logged.emit,
        )
        if history:
            self.organized.emit(history)
        self._start_size_worker()

    def _on_item_changed(self, current, previous):
        """Emite señal cuando se selecciona un centinela diferente."""
        if current:
            sentinel = current.data(Qt.ItemDataRole.UserRole)
            self.sentinel_selected.emit(sentinel)
            self._update_auto_btn_state(sentinel)
        else:
            self.sentinel_selected.emit(None)
