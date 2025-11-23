import sys
import os
sys.path.insert(0, 'src')

from setuptools import setup

# Find PySide6 installation to bundle Qt plugins
try:
    import PySide6
    pyside6_path = os.path.dirname(PySide6.__file__)
    qt_plugins_src = os.path.join(pyside6_path, 'Qt', 'plugins')
    
    # Build plugin data files list
    plugin_data = []
    if os.path.exists(qt_plugins_src):
        for plugin_category in os.listdir(qt_plugins_src):
            src_category = os.path.join(qt_plugins_src, plugin_category)
            if os.path.isdir(src_category):
                dest_category = f'qt_plugins/{plugin_category}'
                for plugin_file in os.listdir(src_category):
                    src_file = os.path.join(src_category, plugin_file)
                    if os.path.isfile(src_file):
                        plugin_data.append((dest_category, [src_file]))
except Exception as e:
    print(f"Warning: Could not locate PySide6 plugins: {e}")
    plugin_data = []

APP = ['src/main.py']
DATA_FILES = [
    ('assets', ['src/assets/papyrus.icns']),
] + plugin_data

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'src/assets/papyrus.icns',
    'resources': ['src/assets/papyrus.icns'],
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
