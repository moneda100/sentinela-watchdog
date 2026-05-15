"""
Ícono en la bandeja del sistema (system tray) para FileWarden.
"""
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QRect


def _create_fallback_icon() -> QIcon:
    """Crea un ícono vectorial de respaldo si no existe el archivo .ico."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Fondo del escudo
    shield_color = QColor("#1a1d23")
    accent_color = QColor("#4f8ef7")

    painter.setBrush(QBrush(shield_color))
    painter.setPen(QPen(accent_color, 3))

    # Dibujar escudo (polígono simplificado)
    from PyQt6.QtGui import QPolygon
    from PyQt6.QtCore import QPoint
    shield_pts = QPolygon([
        QPoint(32, 4),
        QPoint(58, 14),
        QPoint(58, 36),
        QPoint(32, 60),
        QPoint(6, 36),
        QPoint(6, 14),
    ])
    painter.drawPolygon(shield_pts)

    # Ojo en el centro
    painter.setBrush(QBrush(accent_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRect(20, 24, 24, 16))

    painter.setBrush(QBrush(shield_color))
    painter.drawEllipse(QRect(26, 28, 8, 8))

    painter.end()
    return QIcon(pixmap)


def _load_icon() -> QIcon:
    """Carga el ícono desde assets/ o genera uno de respaldo."""
    assets_dir = Path(__file__).parent.parent / "assets"
    ico_path = assets_dir / "icon.ico"
    png_path = assets_dir / "icon.png"

    if ico_path.exists():
        return QIcon(str(ico_path))
    if png_path.exists():
        return QIcon(str(png_path))
    return _create_fallback_icon()


class TrayIcon(QSystemTrayIcon):
    """
    Ícono en la bandeja del sistema con menú contextual.
    """

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._is_watcher_running = False

        icon = _load_icon()
        self.setIcon(icon)
        self.setToolTip("FileWarden — Observador de Archivos")

        self._build_menu()

        self.activated.connect(self._on_activated)

    # ── Menú contextual ───────────────────────────────────────────────────────

    def _build_menu(self):
        menu = QMenu()

        self.action_show = menu.addAction("📂 Mostrar FileWarden")
        self.action_show.triggered.connect(self._show_window)

        menu.addSeparator()

        self.action_status = menu.addAction("⏹ Observador: Detenido")
        self.action_status.setEnabled(False)

        self.action_toggle = menu.addAction("▶ Iniciar Observador")
        self.action_toggle.triggered.connect(self._toggle_watcher)

        menu.addSeparator()

        action_quit = menu.addAction("❌ Salir de FileWarden")
        action_quit.triggered.connect(self._quit_app)

        self.setContextMenu(menu)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self.main_window.showNormal()
        self.main_window.activateWindow()
        self.main_window.raise_()

    def _toggle_watcher(self):
        """Alterna el observador desde la bandeja."""
        btn = self.main_window.btn_play_stop
        btn.setChecked(not btn.isChecked())
        self.main_window.toggle_watcher(btn.isChecked())

    def _quit_app(self):
        """Sale completamente de la aplicación."""
        self.main_window._force_quit = True
        self.main_window.close()
        QApplication.quit()

    # ── Actualización de estado ───────────────────────────────────────────────

    def update_watcher_status(self, running: bool):
        """Actualiza el texto del menú según el estado del observador."""
        self._is_watcher_running = running
        if running:
            self.action_status.setText("▶ Observador: En ejecución")
            self.action_toggle.setText("⏹ Detener Observador")
            self.setToolTip("FileWarden — Observador Activo 🟢")
        else:
            self.action_status.setText("⏹ Observador: Detenido")
            self.action_toggle.setText("▶ Iniciar Observador")
            self.setToolTip("FileWarden — Observador Inactivo 🔴")

    def notify(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Muestra una notificación de la bandeja."""
        if self.supportsMessages():
            self.showMessage(title, message, icon, 4000)
