"""
Punto de entrada de FileWarden.
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def setup_logging():
    """Configura el logging básico del sistema."""
    log_dir = Path.home() / ".filewarden" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "filewarden.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Función principal."""
    setup_logging()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
