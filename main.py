import sys
import os

# Add src to path to ensure we can import the package
# This is primarily for dev mode; PyInstaller handles this via analysis
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from papyrus.main import main

if __name__ == '__main__':
    main()
