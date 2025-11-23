import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from app import HTMLConverterApp

def main():
    app = QApplication(sys.argv)
    window = HTMLConverterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
