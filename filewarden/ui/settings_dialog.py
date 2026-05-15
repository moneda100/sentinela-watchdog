"""
Diálogo de Configuración de FileWarden.
Gestiona: tema visual, inicio automático con Windows, e inicio minimizado.
"""
import winreg
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QCheckBox, QPushButton, QDialogButtonBox,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.themes import theme_manager, THEMES

APP_NAME = "FileWarden"
_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_EXE_PATH = str(Path(__file__).parent.parent.resolve() / "FileWarden.exe")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers para registro de Windows
# ──────────────────────────────────────────────────────────────────────────────

def is_autostart_enabled() -> bool:
    """Comprueba si FileWarden está en el inicio automático de Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                            winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except (FileNotFoundError, OSError):
        return False


def set_autostart(enabled: bool, exe_path: str | None = None) -> bool:
    """
    Activa o desactiva el inicio automático con Windows.
    Retorna True si la operación fue exitosa.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                            winreg.KEY_SET_VALUE) as key:
            if enabled:
                path = exe_path or _EXE_PATH
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{path}"')
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass  # Ya no existía, no es error
        return True
    except OSError:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Diálogo
# ──────────────────────────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    """
    Diálogo modal de configuración de FileWarden.
    """

    def __init__(self, parent=None, current_theme: str = "Oscuro",
                 start_minimized: bool = False):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración — FileWarden")
        self.setMinimumWidth(440)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self._selected_theme = current_theme
        self._start_minimized = start_minimized

        self._setup_ui()
        self._load_current_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Título ─────────────────────────────────────────────────────────────
        title_label = QLabel("Configuración")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        subtitle = QLabel("Personaliza el comportamiento y apariencia de FileWarden")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Policy.Minimum,
                                         QSizePolicy.Policy.Fixed))

        # ── Grupo: Apariencia ─────────────────────────────────────────────────
        grp_appearance = QGroupBox("Apariencia")
        app_layout = QVBoxLayout(grp_appearance)
        app_layout.setSpacing(10)

        theme_row = QHBoxLayout()
        lbl_theme = QLabel("Tema de color:")
        lbl_theme.setMinimumWidth(130)

        self.cmb_theme = QComboBox()
        for key, data in THEMES.items():
            self.cmb_theme.addItem(data["label"], key)
        self.cmb_theme.currentIndexChanged.connect(self._on_theme_preview)

        theme_row.addWidget(lbl_theme)
        theme_row.addWidget(self.cmb_theme, 1)
        app_layout.addLayout(theme_row)

        # Preview strip
        self.lbl_preview = QLabel("Vista previa aplicada en tiempo real")
        self.lbl_preview.setObjectName("preview-hint")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(self.lbl_preview)

        layout.addWidget(grp_appearance)

        # ── Grupo: Sistema ────────────────────────────────────────────────────
        grp_system = QGroupBox("Sistema")
        sys_layout = QVBoxLayout(grp_system)
        sys_layout.setSpacing(10)

        self.chk_autostart = QCheckBox(
            "🚀  Iniciar automáticamente con Windows"
        )
        self.chk_autostart.setToolTip(
            "Agrega FileWarden al registro de inicio de Windows.\n"
            "Requiere que exista el ejecutable FileWarden.exe."
        )
        sys_layout.addWidget(self.chk_autostart)

        self.chk_minimized = QCheckBox(
            "🔔  Iniciar minimizado en la bandeja del sistema"
        )
        self.chk_minimized.setToolTip(
            "Al abrir FileWarden, la ventana permanecerá oculta.\n"
            "Haz doble clic en el ícono de la bandeja para mostrarla."
        )
        sys_layout.addWidget(self.chk_minimized)

        layout.addWidget(grp_system)

        # ── Grupo: Comportamiento ─────────────────────────────────────────────
        grp_behavior = QGroupBox("Notificaciones")
        beh_layout = QVBoxLayout(grp_behavior)

        self.chk_tray_notify = QCheckBox(
            "🔔  Mostrar notificaciones en la bandeja al mover archivos"
        )
        self.chk_tray_notify.setChecked(True)
        beh_layout.addWidget(self.chk_tray_notify)

        layout.addWidget(grp_behavior)

        layout.addStretch()

        # ── Botones ───────────────────────────────────────────────────────────
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _load_current_values(self):
        """Carga los valores actuales en los controles."""
        # Tema
        idx = self.cmb_theme.findData(self._selected_theme)
        if idx >= 0:
            self.cmb_theme.setCurrentIndex(idx)

        # Inicio automático
        self.chk_autostart.setChecked(is_autostart_enabled())

        # Inicio minimizado
        self.chk_minimized.setChecked(self._start_minimized)

    def _on_theme_preview(self, _index: int):
        """Aplica el tema seleccionado en tiempo real como vista previa."""
        key = self.cmb_theme.currentData()
        if key:
            theme_manager.apply(key)
            self._selected_theme = key

    def _on_accept(self):
        """Guarda los cambios y cierra el diálogo."""
        # Aplicar inicio automático
        autostart_ok = set_autostart(self.chk_autostart.isChecked())
        if not autostart_ok and self.chk_autostart.isChecked():
            # Informar al usuario si falló pero no bloquear
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Inicio Automático",
                "No se pudo modificar el registro de Windows.\n"
                "Intenta ejecutar FileWarden como administrador."
            )

        self.accept()

    # ── Propiedades de resultado ──────────────────────────────────────────────

    @property
    def selected_theme(self) -> str:
        return self._selected_theme

    @property
    def start_minimized(self) -> bool:
        return self.chk_minimized.isChecked()

    @property
    def tray_notifications(self) -> bool:
        return self.chk_tray_notify.isChecked()
