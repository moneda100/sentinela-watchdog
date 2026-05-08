"""
Ventana principal de FileWarden.
"""
import json
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QSplitter, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

from core.rules import Sentinel, Rule
from core.watcher import FileWatcherThread
from ui.sentinel_panel import SentinelPanel
from ui.rules_table import RulesTable
from ui.log_panel import LogPanel

CONFIG_FILE = Path.home() / ".filewarden" / "config.json"


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileWarden")
        self.resize(960, 640)

        self.sentinels = []
        self.watcher_thread = None
        self.is_running = False

        # Estadísticas de sesión
        self._moved_count = 0
        self._error_count = 0

        # Historial para deshacer (lista de tuples: (ubicación_actual, ubicación_original))
        self._undo_history: list[tuple[Path, Path]] = []

        self._setup_ui()
        self.load_config()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(6)

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = QHBoxLayout()

        self.lbl_status = QLabel("⏹ Detenido")
        self.lbl_status.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 13px;")

        # Estadísticas
        self.lbl_stats = QLabel("📁 0 movidos  |  ⚠️ 0 errores")
        self.lbl_stats.setStyleSheet("color: #95a5a6; font-size: 12px;")

        self.btn_undo = QPushButton("⏪ Deshacer")
        self.btn_undo.setEnabled(False)
        self.btn_undo.setToolTip("Revertir la última operación de archivo")
        self.btn_undo.clicked.connect(self._undo_last)

        self.btn_play_stop = QPushButton("▶ Iniciar Observador")
        self.btn_play_stop.setCheckable(True)
        self.btn_play_stop.clicked.connect(self.toggle_watcher)

        top_bar.addWidget(self.lbl_status)
        top_bar.addSpacing(16)
        top_bar.addWidget(self.lbl_stats)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_undo)
        top_bar.addWidget(self.btn_play_stop)
        main_layout.addLayout(top_bar)

        # ── Splitter principal ────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo: Centinelas
        self.sentinel_panel = SentinelPanel()
        self.sentinel_panel.sentinel_selected.connect(self.on_sentinel_selected)
        self.sentinel_panel.sentinels_changed.connect(self.save_config)
        self.sentinel_panel.action_logged.connect(self._on_file_moved)
        self.sentinel_panel.error_logged.connect(self._on_error_occurred)
        self.sentinel_panel.organized.connect(self._on_organized)
        splitter.addWidget(self.sentinel_panel)

        # Panel derecho: Reglas + Log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.rules_table = RulesTable()
        self.rules_table.rules_changed.connect(self.save_config)

        self.log_panel = LogPanel()

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(self.rules_table)
        right_splitter.addWidget(self.log_panel)
        right_splitter.setSizes([280, 200])

        right_layout.addWidget(right_splitter)
        splitter.addWidget(right_panel)

        splitter.setSizes([270, 690])
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Listo")

    # ── Sentinel selection ────────────────────────────────────────────────────

    def on_sentinel_selected(self, sentinel):
        self.rules_table.load_sentinel(sentinel)

    # ── Watcher control ───────────────────────────────────────────────────────

    def toggle_watcher(self, checked):
        if checked:
            self._start_watcher()
        else:
            self._stop_watcher()

    def _start_watcher(self):
        active_sentinels = [s for s in self.sentinels if s.active]
        if not active_sentinels:
            QMessageBox.warning(self, "Atención", "No hay centinelas activos para monitorear.")
            self.btn_play_stop.setChecked(False)
            return

        self.watcher_thread = FileWatcherThread(self.sentinels)
        self.watcher_thread.file_moved.connect(self._on_file_moved)
        self.watcher_thread.error_occurred.connect(self._on_error_occurred)
        self.watcher_thread.start()

        self.is_running = True
        self.lbl_status.setText("▶ En ejecución")
        self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 13px;")
        self.btn_play_stop.setText("⏹ Detener Observador")
        self.sentinel_panel.setEnabled(False)

    def _stop_watcher(self):
        if self.watcher_thread and self.watcher_thread.isRunning():
            self.watcher_thread.stop()

        self.is_running = False
        self.lbl_status.setText("⏹ Detenido")
        self.lbl_status.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 13px;")
        self.btn_play_stop.setText("▶ Iniciar Observador")
        self.btn_play_stop.setChecked(False)
        self.sentinel_panel.setEnabled(True)

    # ── Logging + Stats ───────────────────────────────────────────────────────

    def _on_file_moved(self, msg: str):
        self.log_panel.log_action(msg)
        self.statusBar().showMessage(msg, 5000)
        self._moved_count += 1
        self._update_stats()

    def _on_error_occurred(self, msg: str):
        self.log_panel.log_error(msg)
        self.statusBar().showMessage(f"Error: {msg}", 5000)
        self._error_count += 1
        self._update_stats()

    def _update_stats(self):
        self.lbl_stats.setText(
            f"📁 {self._moved_count} movido(s)  |  ⚠️ {self._error_count} error(es)"
        )

    # ── Organized (auto-organize batch) ──────────────────────────────────────

    def _on_organized(self, history: list):
        """
        Recibe el historial de movimientos de auto_organize y lo agrega al
        historial de deshacer. El historial es lista de (dest_actual, origen_original).
        """
        self._undo_history.extend(history)
        self.btn_undo.setEnabled(bool(self._undo_history))
        # Las estadísticas ya se actualizaron vía action_logged señal

    # ── Undo ─────────────────────────────────────────────────────────────────

    def _undo_last(self):
        """Deshace el último movimiento de archivo registrado."""
        if not self._undo_history:
            return

        current_path, original_path = self._undo_history.pop()

        if not current_path.exists():
            self.log_panel.log_error(f"No se puede deshacer: '{current_path.name}' ya no existe.")
            self.btn_undo.setEnabled(bool(self._undo_history))
            return

        try:
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), str(original_path))
            msg = f"⏪ Deshecho: '{current_path.name}' regresó a '{original_path.parent.name}'"
            self.log_panel.log_action(msg)
            self.statusBar().showMessage(msg, 5000)
        except Exception as e:
            self.log_panel.log_error(f"Error al deshacer: {e}")

        self.btn_undo.setEnabled(bool(self._undo_history))

    # ── Config persistence ────────────────────────────────────────────────────

    def load_config(self):
        if not CONFIG_FILE.exists():
            return

        try:
            with CONFIG_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)

            self.sentinels = []
            for s_data in data.get('sentinels', []):
                rules = []
                for r_data in s_data.get('rules', []):
                    rules.append(Rule(
                        extension=r_data['extension'],
                        destination=Path(r_data['destination']),
                        action=r_data['action'],
                        rename_pattern=r_data.get('rename_pattern', '')
                    ))
                self.sentinels.append(Sentinel(
                    watch_path=Path(s_data['watch_path']),
                    active=s_data['active'],
                    auto_organize=s_data.get('auto_organize', False),
                    rules=rules
                ))
            self.sentinel_panel.load_sentinels(self.sentinels)
        except Exception as e:
            self.log_panel.log_error(f"Error al cargar configuración: {e}")

    def save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {'sentinels': []}
        for s in self.sentinels:
            s_data = {
                'watch_path': str(s.watch_path),
                'active': s.active,
                'auto_organize': s.auto_organize,
                'rules': [
                    {
                        'extension': r.extension,
                        'destination': str(r.destination),
                        'action': r.action,
                        'rename_pattern': r.rename_pattern
                    } for r in s.rules
                ]
            }
            data['sentinels'].append(s_data)

        try:
            with CONFIG_FILE.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log_panel.log_error(f"Error al guardar configuración: {e}")

    def closeEvent(self, event):
        self._stop_watcher()
        self.save_config()
        event.accept()
