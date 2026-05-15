"""
Motor de temas para FileWarden.
Gestiona 5 paletas de colores completas expresadas como hojas de estilo QSS.
"""
from __future__ import annotations
from PyQt6.QtWidgets import QApplication

# ──────────────────────────────────────────────────────────────────────────────
# Definición de temas
# ──────────────────────────────────────────────────────────────────────────────

THEMES: dict[str, dict] = {
    "Oscuro": {
        "label": "🌑 Oscuro",
        "bg_primary":    "#1a1d23",
        "bg_secondary":  "#22262e",
        "bg_tertiary":   "#2a2f3a",
        "accent":        "#4f8ef7",
        "accent_hover":  "#6ba3ff",
        "accent_pressed":"#3a73d9",
        "text_primary":  "#e8eaf0",
        "text_secondary":"#8b93a7",
        "text_disabled": "#505770",
        "border":        "#353a48",
        "success":       "#2ecc71",
        "error":         "#e74c3c",
        "warning":       "#f39c12",
    },
    "Océano": {
        "label": "🌊 Océano",
        "bg_primary":    "#0d1b2a",
        "bg_secondary":  "#112233",
        "bg_tertiary":   "#1a3044",
        "accent":        "#00c9b1",
        "accent_hover":  "#00e8cc",
        "accent_pressed":"#00a896",
        "text_primary":  "#d6eaf8",
        "text_secondary":"#7fb3d3",
        "text_disabled": "#3a6278",
        "border":        "#1c3f5c",
        "success":       "#00c9b1",
        "error":         "#e74c3c",
        "warning":       "#f0b429",
    },
    "Bosque": {
        "label": "🌿 Bosque",
        "bg_primary":    "#111a13",
        "bg_secondary":  "#192419",
        "bg_tertiary":   "#213023",
        "accent":        "#4caf50",
        "accent_hover":  "#66bb6a",
        "accent_pressed":"#388e3c",
        "text_primary":  "#e8f5e9",
        "text_secondary":"#81c784",
        "text_disabled": "#3b5e3d",
        "border":        "#2e4930",
        "success":       "#4caf50",
        "error":         "#ef5350",
        "warning":       "#ffca28",
    },
    "Crepúsculo": {
        "label": "🌅 Crepúsculo",
        "bg_primary":    "#1c1118",
        "bg_secondary":  "#271520",
        "bg_tertiary":   "#351c2b",
        "accent":        "#ff6b6b",
        "accent_hover":  "#ff8e8e",
        "accent_pressed":"#e05252",
        "text_primary":  "#fce4ec",
        "text_secondary":"#f48fb1",
        "text_disabled": "#7b3f55",
        "border":        "#4a2035",
        "success":       "#a5d6a7",
        "error":         "#ff6b6b",
        "warning":       "#ffcc02",
    },
    "Claro": {
        "label": "☀️ Claro",
        "bg_primary":    "#f5f7fa",
        "bg_secondary":  "#ffffff",
        "bg_tertiary":   "#e8edf4",
        "accent":        "#1976d2",
        "accent_hover":  "#1e88e5",
        "accent_pressed":"#1565c0",
        "text_primary":  "#1a2035",
        "text_secondary":"#546e7a",
        "text_disabled": "#b0bec5",
        "border":        "#d0d8e4",
        "success":       "#2e7d32",
        "error":         "#c62828",
        "warning":       "#e65100",
    },
}


def _build_qss(t: dict) -> str:
    """Genera una hoja de estilo QSS completa a partir de un diccionario de colores."""
    return f"""
/* ═══════════════════════════════════════════════════════════
   FileWarden — Hoja de estilo generada dinámicamente
   ═══════════════════════════════════════════════════════════ */

QMainWindow, QDialog {{
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}

QWidget {{
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
}}

/* ── Menú ─────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border-bottom: 1px solid {t['border']};
    padding: 2px 4px;
    spacing: 2px;
}}
QMenuBar::item {{
    padding: 5px 12px;
    border-radius: 4px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background-color: {t['bg_tertiary']};
    color: {t['accent']};
}}
QMenu {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 4px 0;
}}
QMenu::item {{
    padding: 7px 28px 7px 16px;
    border-radius: 4px;
    margin: 2px 4px;
}}
QMenu::item:selected {{
    background-color: {t['accent']};
    color: {'#ffffff' if t['bg_primary'] != '#f5f7fa' else '#ffffff'};
}}
QMenu::separator {{
    height: 1px;
    background: {t['border']};
    margin: 4px 8px;
}}

/* ── Botones ─────────────────────────────────────────────── */
QPushButton {{
    background-color: {t['bg_tertiary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {t['accent']};
    color: #ffffff;
    border-color: {t['accent']};
}}
QPushButton:pressed {{
    background-color: {t['accent_pressed']};
    border-color: {t['accent_pressed']};
}}
QPushButton:checked {{
    background-color: {t['accent']};
    color: #ffffff;
    border-color: {t['accent_hover']};
}}
QPushButton:disabled {{
    background-color: {t['bg_secondary']};
    color: {t['text_disabled']};
    border-color: {t['border']};
}}

/* ── Inputs ──────────────────────────────────────────────── */
QLineEdit, QSpinBox, QComboBox {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 5px;
    padding: 5px 8px;
    selection-background-color: {t['accent']};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {t['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
    border-radius: 4px;
}}

/* ── Listas ──────────────────────────────────────────────── */
QListWidget, QTableWidget, QTreeWidget {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    outline: none;
    gridline-color: {t['border']};
    alternate-background-color: {t['bg_tertiary']};
}}
QListWidget::item, QTableWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 2px;
}}
QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: {t['accent']};
    color: #ffffff;
}}
QListWidget::item:hover, QTableWidget::item:hover {{
    background-color: {t['bg_tertiary']};
}}
QHeaderView::section {{
    background-color: {t['bg_tertiary']};
    color: {t['text_secondary']};
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid {t['border']};
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}}

/* ── Texto / Log ─────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    selection-background-color: {t['accent']};
}}

/* ── Splitter ────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {t['border']};
    width: 2px;
    height: 2px;
}}
QSplitter::handle:hover {{
    background-color: {t['accent']};
}}

/* ── Scroll bars ─────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {t['bg_primary']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {t['bg_primary']};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t['border']};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t['accent']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Status bar ──────────────────────────────────────────── */
QStatusBar {{
    background-color: {t['bg_secondary']};
    color: {t['text_secondary']};
    border-top: 1px solid {t['border']};
    font-size: 11px;
    padding: 2px 8px;
}}

/* ── CheckBox / Radio ────────────────────────────────────── */
QCheckBox {{
    color: {t['text_primary']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {t['border']};
    border-radius: 3px;
    background: {t['bg_secondary']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
    image: none;
}}
QCheckBox::indicator:hover {{
    border-color: {t['accent']};
}}

/* ── Tooltips ────────────────────────────────────────────── */
QToolTip {{
    background-color: {t['bg_tertiary']};
    color: {t['text_primary']};
    border: 1px solid {t['accent']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── GroupBox ────────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {t['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    color: {t['text_secondary']};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {t['accent']};
}}

/* ── Labels especiales ───────────────────────────────────── */
QLabel[class="status-running"] {{
    color: {t['success']};
    font-weight: bold;
}}
QLabel[class="status-stopped"] {{
    color: {t['error']};
    font-weight: bold;
}}
QLabel[class="stats"] {{
    color: {t['text_secondary']};
}}

/* ── Diálogos ────────────────────────────────────────────── */
QDialog {{
    background-color: {t['bg_primary']};
}}
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
QMessageBox {{
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
}}
"""


class ThemeManager:
    """Gestiona los temas de la aplicación."""

    def __init__(self):
        self._current: str = "Oscuro"

    @property
    def current(self) -> str:
        return self._current

    @property
    def available(self) -> list[str]:
        return list(THEMES.keys())

    def apply(self, theme_name: str, app: QApplication | None = None) -> None:
        """Aplica el tema dado a la aplicación."""
        if theme_name not in THEMES:
            theme_name = "Oscuro"
        self._current = theme_name
        qss = _build_qss(THEMES[theme_name])
        target = app or QApplication.instance()
        if target:
            target.setStyleSheet(qss)

    def get_colors(self, theme_name: str | None = None) -> dict:
        """Retorna el diccionario de colores del tema actual o solicitado."""
        return THEMES.get(theme_name or self._current, THEMES["Oscuro"])

    def label(self, theme_name: str) -> str:
        """Retorna la etiqueta con emoji del tema."""
        return THEMES.get(theme_name, {}).get("label", theme_name)


# Instancia global
theme_manager = ThemeManager()
