import sys
import os
import traceback

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from PySide6.QtWidgets import QApplication
        from app import HTMLConverterApp

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
