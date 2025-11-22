import sys
sys.path.insert(0, 'src')

from setuptools import setup

APP = ['run.py']
DATA_FILES = [
    ('resources', ['resources/papyrus.icns']),
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'resources/papyrus.icns',
    'packages': ['PySide6'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    'excludes': ['tkinter', 'numpy', 'pandas', 'matplotlib', 'scipy', 'IPython', 'jupyter_client', 'ipykernel', 'tornado', 'zmq', 'PIL', 'cv2'],
    'plist': {
        'CFBundleName': 'Papyrus',
        'CFBundleDisplayName': 'Papyrus',
        'CFBundleGetInfoString': "Papyrus HTML Converter",
        'CFBundleIdentifier': "com.RazorBackRoar.papyrus",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024 RazorBackRoar",
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSArchitecturePriority': ['arm64'],
    }
}

setup(
    app=APP,
    name='Papyrus',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)
