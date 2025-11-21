import sys
import os
from PySide6.QtWidgets import QApplication
from .app import HTMLConverterApp

__version__ = "1.0.0"

# Silence noisy Qt font alias warnings in terminal (e.g., missing "JetBrains Mono")
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts=false")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = HTMLConverterApp()
    screen = app.primaryScreen().geometry()
    x = (screen.width() - 1200) // 2
    y = (screen.height() - 800) // 2
    window.move(x, y)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
