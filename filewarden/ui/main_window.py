"""
Ventana principal de FileWarden — con temas, bandeja del sistema y menú completo.
"""
import json
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QLabel, QMessageBox,
    QMenuBar, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

from core.rules import Sentinel, Rule
from core.watcher import FileWatcherThread
from ui.sentinel_panel import SentinelPanel
from ui.rules_table import RulesTable
from ui.log_panel import LogPanel
from ui.themes import theme_manager
from ui.tray_icon import TrayIcon
from ui.settings_dialog import SettingsDialog

CONFIG_FILE = Path.home() / ".filewarden" / "config.json"
ASSETS_DIR = Path(__file__).parent.parent / "assets"


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación FileWarden.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileWarden")
        self.resize(1060, 680)
        self.setMinimumSize(800, 520)

        # Icono de la ventana
        icon_path = ASSETS_DIR / "icon.ico"
        if not icon_path.exists():
            icon_path = ASSETS_DIR / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.sentinels: list[Sentinel] = []
        self.watcher_thread: FileWatcherThread | None = None
        self.is_running = False
        self._force_quit = False

        # Preferencias
        self._start_minimized = False
        self._tray_notifications = True

        # Estadísticas de sesión
        self._moved_count = 0
        self._error_count = 0

        # Historial para deshacer
        self._undo_history: list[tuple[Path, Path]] = []

        self._setup_menu()
        self._setup_ui()
        self.load_config()

        # Bandeja del sistema
        self._tray = TrayIcon(self)
        self._tray.show()

        # Iniciar minimizado si está configurado
        if self._start_minimized:
            self.hide()
        else:
            self.show()

    # ══════════════════════════════════════════════════════════════════════════
    # Menú principal
    # ══════════════════════════════════════════════════════════════════════════

    def _setup_menu(self):
        menubar: QMenuBar = self.menuBar()

        # ── Archivo ───────────────────────────────────────────────────────────
        menu_file: QMenu = menubar.addMenu("&Archivo")

        act_config = QAction("⚙️ Configuración…", self)
        act_config.setShortcut("Ctrl+,")
        act_config.triggered.connect(self.open_settings)
        menu_file.addAction(act_config)

        menu_file.addSeparator()

        act_minimize = QAction("🔔 Minimizar a bandeja", self)
        act_minimize.setShortcut("Ctrl+M")
        act_minimize.triggered.connect(self.hide)
        menu_file.addAction(act_minimize)

        menu_file.addSeparator()

        act_quit = QAction("❌ Salir", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self._quit_completely)
        menu_file.addAction(act_quit)

        # ── Vista / Temas ─────────────────────────────────────────────────────
        menu_view: QMenu = menubar.addMenu("&Vista")
        menu_themes: QMenu = menu_view.addMenu("🎨 Temas")

        for key in theme_manager.available:
            label = theme_manager.label(key)
            act = QAction(label, self)
            act.setData(key)
            act.setCheckable(True)
            act.setChecked(key == theme_manager.current)
            act.triggered.connect(lambda checked, k=key: self._apply_theme(k))
            menu_themes.addAction(act)

        self._menu_themes = menu_themes  # guardar ref para actualizar checks

        # ── Herramientas ──────────────────────────────────────────────────────
        menu_tools: QMenu = menubar.addMenu("&Herramientas")

        act_undo = QAction("⏪ Deshacer último movimiento", self)
        act_undo.setShortcut("Ctrl+Z")
        act_undo.triggered.connect(self._undo_last)
        menu_tools.addAction(act_undo)

        menu_tools.addSeparator()

        act_clear_log = QAction("🗑 Limpiar log", self)
        act_clear_log.triggered.connect(lambda: self.log_panel.clear_log())
        menu_tools.addAction(act_clear_log)

        act_export_log = QAction("💾 Exportar log…", self)
        act_export_log.triggered.connect(lambda: self.log_panel.export_log())
        menu_tools.addAction(act_export_log)

        # ── Ayuda ─────────────────────────────────────────────────────────────
        menu_help: QMenu = menubar.addMenu("&Ayuda")

        act_about = QAction("ℹ️ Acerca de FileWarden", self)
        act_about.triggered.connect(self._show_about)
        menu_help.addAction(act_about)

    # ══════════════════════════════════════════════════════════════════════════
    # UI principal
    # ══════════════════════════════════════════════════════════════════════════

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 6, 8, 4)

        # ── Top bar ───────────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.lbl_status = QLabel("⏹ Detenido")
        self.lbl_status.setObjectName("status-label")
        self._apply_status_style(running=False)

        self.lbl_stats = QLabel("📁 0 movidos  |  ⚠️ 0 errores")
        self.lbl_stats.setObjectName("stats-label")

        self.btn_undo = QPushButton("⏪ Deshacer")
        self.btn_undo.setEnabled(False)
        self.btn_undo.setToolTip("Revertir la última operación de archivo  (Ctrl+Z)")
        self.btn_undo.clicked.connect(self._undo_last)
        self.btn_undo.setFixedHeight(34)

        self.btn_play_stop = QPushButton("▶  Iniciar Observador")
        self.btn_play_stop.setCheckable(True)
        self.btn_play_stop.clicked.connect(self.toggle_watcher)
        self.btn_play_stop.setFixedHeight(34)
        self.btn_play_stop.setMinimumWidth(160)

        top_bar.addWidget(self.lbl_status)
        top_bar.addSpacing(12)
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
        right_splitter.setSizes([300, 220])

        right_layout.addWidget(right_splitter)
        splitter.addWidget(right_panel)

        splitter.setSizes([280, 780])
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("FileWarden listo ✔")

    # ══════════════════════════════════════════════════════════════════════════
    # Temas
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_theme(self, key: str):
        """Aplica un tema y actualiza los checks del menú."""
        theme_manager.apply(key)
        self._refresh_theme_checks(key)
        self._apply_status_style(self.is_running)
        self.save_config()

    def _refresh_theme_checks(self, active_key: str):
        for act in self._menu_themes.actions():
            act.setChecked(act.data() == active_key)

    def _apply_status_style(self, running: bool):
        colors = theme_manager.get_colors()
        if running:
            self.lbl_status.setText("▶ En ejecución")
            self.lbl_status.setStyleSheet(
                f"color: {colors['success']}; font-weight: bold; font-size: 13px;"
            )
        else:
            self.lbl_status.setText("⏹ Detenido")
            self.lbl_status.setStyleSheet(
                f"color: {colors['error']}; font-weight: bold; font-size: 13px;"
            )

    # ══════════════════════════════════════════════════════════════════════════
    # Configuración
    # ══════════════════════════════════════════════════════════════════════════

    def open_settings(self):
        dlg = SettingsDialog(
            parent=self,
            current_theme=theme_manager.current,
            start_minimized=self._start_minimized
        )
        if dlg.exec():
            self._start_minimized = dlg.start_minimized
            self._tray_notifications = dlg.tray_notifications
            # El tema ya se aplicó en tiempo real dentro del diálogo
            self._refresh_theme_checks(theme_manager.current)
            self._apply_status_style(self.is_running)
            self.save_config()

    def _show_about(self):
        colors = theme_manager.get_colors()
        QMessageBox.about(
            self,
            "Acerca de FileWarden",
            "<h2>🛡️ FileWarden</h2>"
            "<p>Observador y organizador automático de archivos.</p>"
            "<p><b>Versión:</b> 2.0.0<br>"
            "<b>Motor:</b> Python + PyQt6 + Watchdog</p>"
            "<p>Monitorea carpetas en tiempo real y organiza archivos<br>"
            "según reglas definidas por el usuario.</p>"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Sentinel selection
    # ══════════════════════════════════════════════════════════════════════════

    def on_sentinel_selected(self, sentinel):
        self.rules_table.load_sentinel(sentinel)

    # ══════════════════════════════════════════════════════════════════════════
    # Watcher control
    # ══════════════════════════════════════════════════════════════════════════

    def toggle_watcher(self, checked: bool):
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
        self._apply_status_style(running=True)
        self.btn_play_stop.setText("⏹  Detener Observador")
        self.sentinel_panel.setEnabled(False)
        self._tray.update_watcher_status(True)
        if self._tray_notifications:
            self._tray.notify("FileWarden", "Observador iniciado 🟢")

    def _stop_watcher(self):
        if self.watcher_thread and self.watcher_thread.isRunning():
            self.watcher_thread.stop()

        self.is_running = False
        self._apply_status_style(running=False)
        self.btn_play_stop.setText("▶  Iniciar Observador")
        self.btn_play_stop.setChecked(False)
        self.sentinel_panel.setEnabled(True)
        self._tray.update_watcher_status(False)

    # ══════════════════════════════════════════════════════════════════════════
    # Logging + Stats
    # ══════════════════════════════════════════════════════════════════════════

    def _on_file_moved(self, msg: str):
        self.log_panel.log_action(msg)
        self.statusBar().showMessage(msg, 5000)
        self._moved_count += 1
        self._update_stats()
        if self._tray_notifications and not self.isVisible():
            self._tray.notify("Archivo movido", msg)

    def _on_error_occurred(self, msg: str):
        self.log_panel.log_error(msg)
        self.statusBar().showMessage(f"Error: {msg}", 5000)
        self._error_count += 1
        self._update_stats()

    def _update_stats(self):
        self.lbl_stats.setText(
            f"📁 {self._moved_count} movido(s)  |  ⚠️ {self._error_count} error(es)"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Organized (auto-organize batch)
    # ══════════════════════════════════════════════════════════════════════════

    def _on_organized(self, history: list):
        self._undo_history.extend(history)
        self.btn_undo.setEnabled(bool(self._undo_history))

    # ══════════════════════════════════════════════════════════════════════════
    # Undo
    # ══════════════════════════════════════════════════════════════════════════

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

    # ══════════════════════════════════════════════════════════════════════════
    # Config persistence
    # ══════════════════════════════════════════════════════════════════════════

    def load_config(self):
        if not CONFIG_FILE.exists():
            return

        try:
            with CONFIG_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)

            # Preferencias de app
            prefs = data.get('preferences', {})
            saved_theme = prefs.get('theme', 'Oscuro')
            self._start_minimized = prefs.get('start_minimized', False)
            self._tray_notifications = prefs.get('tray_notifications', True)
            theme_manager.apply(saved_theme)
            self._refresh_theme_checks(saved_theme)

            # Centinelas
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

        data = {
            'preferences': {
                'theme': theme_manager.current,
                'start_minimized': self._start_minimized,
                'tray_notifications': self._tray_notifications,
            },
            'sentinels': []
        }

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
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log_panel.log_error(f"Error al guardar configuración: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # Cierre
    # ══════════════════════════════════════════════════════════════════════════

    def _quit_completely(self):
        """Sale completamente de la aplicación."""
        self._force_quit = True
        self.close()

    def closeEvent(self, event):
        if not self._force_quit:
            # Minimizar a bandeja en lugar de cerrar
            event.ignore()
            self.hide()
            if self._tray_notifications:
                self._tray.notify(
                    "FileWarden",
                    "Minimizado a la bandeja. Doble clic para mostrar."
                )
        else:
            # Cerrar de verdad
            self._stop_watcher()
            self.save_config()
            self._tray.hide()
            event.accept()
