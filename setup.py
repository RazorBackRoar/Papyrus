import sys
sys.path.insert(0, 'src')

from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('assets', ['src/assets/papyrus.icns']),
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'src/assets/papyrus.icns',
    'packages': ['PySide6', 'bs4'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtPrintSupport'],
    'excludes': [
        'tkinter', 'numpy', 'pandas', 'matplotlib', 'scipy', 'IPython', 'jupyter_client', 'ipykernel', 'tornado', 'zmq', 'PIL', 'cv2',
        'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineQuick',
        'PySide6.QtDesigner', 'PySide6.QtQuick3D', 'PySide6.QtDataVisualization', 'PySide6.QtCharts',
        'PySide6.QtNetworkAuth', 'PySide6.QtLocation', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
        'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtTextToSpeech',
        'PySide6.QtXml', 'PySide6.QtBluetooth', 'PySide6.QtNfc', 'PySide6.QtPositioning', 'PySide6.QtRemoteObjects',
        'PySide6.QtScxml', 'PySide6.QtStateMachine', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets'
    ],
    'plist': {
        'CFBundleName': 'Papyrus',
        'CFBundleDisplayName': 'Papyrus',
        'CFBundleGetInfoString': "Papyrus HTML Converter",
        'CFBundleIdentifier': "com.RazorBackRoar.papyrus",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2025 RazorBackRoar",
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
