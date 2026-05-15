"""
Punto de entrada de FileWarden.
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from ui.themes import theme_manager


def setup_logging():
    """Configura el logging básico del sistema."""
    log_dir = Path.home() / ".filewarden" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "filewarden.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Función principal."""
    setup_logging()

    # Necesario para que el ícono de la bandeja funcione correctamente
    # y la app no cierre cuando se oculta la ventana principal
    QApplication.setQuitOnLastWindowClosed(False)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("FileWarden")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("FileWarden")

    # Aplicar tema oscuro por defecto antes de crear la ventana
    theme_manager.apply("Oscuro", app)

    window = MainWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
