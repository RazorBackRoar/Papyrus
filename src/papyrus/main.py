import sys
import os
import traceback
from PySide6.QtWidgets import QApplication

# Add src directory to Python path to allow 'papyrus' package imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def main():
    try:
        from papyrus.core.app import HTMLConverterApp

        app = QApplication(sys.argv)
        window = HTMLConverterApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        # Crash logging
        log_path = os.path.join(
            os.path.expanduser("~/Desktop"), "papyrus_crash_log.txt"
        )
        with open(log_path, "w") as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
