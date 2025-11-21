import sys
import os
sys.path.insert(0, 'src')

from setuptools import setup

APP = ['run.py']
DATA_FILES = [
    ('resources', ['resources/papyrus.icns']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/papyrus.icns',
    'packages': ['PySide6'],
    'includes': [
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'jaraco',
        'pkg_resources',
    ],
    'excludes': [
        'PyInstaller',
        'PyQt6',
        'PyQt5',
        'tkinter',
        'test',
        'unittest',
    ],
    'plist': {
        'CFBundleName': 'Papyrus',
        'CFBundleDisplayName': 'Papyrus',
        'CFBundleGetInfoString': 'Papyrus HTML Converter v1.0.0, Copyright 2025 RazorBackRoar',
        'CFBundleIdentifier': 'com.RazorBackRoar.papyrus',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright 2025 RazorBackRoar. All rights reserved.',
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
