import sys
from pathlib import Path

sys.path.insert(0, "src")

from setuptools import setup, find_packages

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def get_project_version(default: str = "0.0.0") -> str:
    pyproject = Path(__file__).resolve().parent / "pyproject.toml"
    if not pyproject.exists():
        return default
    try:
        with pyproject.open("rb") as fp:
            data = tomllib.load(fp)
        return data["project"]["version"]
    except Exception:
        return default


APP_VERSION = get_project_version()

APP = ["src/papyrus/main.py"]
DATA_FILES = [
    ("assets/icons", ["assets/icons/Papyrus.icns"]),
]

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "assets/icons/Papyrus.icns",
    "resources": ["assets/icons/Papyrus.icns"],
    "dist_dir": "build/dist",
    "packages": ["PySide6", "bs4", "shiboken6"],
    "includes": [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtPrintSupport",
        "shiboken6",
    ],
    "excludes": [
        "tkinter",
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "IPython",
        "jupyter_client",
        "ipykernel",
        "tornado",
        "zmq",
        "PIL",
        "cv2",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtDesigner",
        "PySide6.QtQuick3D",
        "PySide6.QtDataVisualization",
        "PySide6.QtCharts",
        "PySide6.QtNetworkAuth",
        "PySide6.QtLocation",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtSql",
        "PySide6.QtTest",
        "PySide6.QtTextToSpeech",
        "PySide6.QtXml",
        "PySide6.QtBluetooth",
        "PySide6.QtNfc",
        "PySide6.QtPositioning",
        "PySide6.QtRemoteObjects",
        "PySide6.QtScxml",
        "PySide6.QtStateMachine",
        "PySide6.QtWebChannel",
        "PySide6.QtWebSockets",
    ],
    "plist": {
        "CFBundleName": "Papyrus",
        "CFBundleDisplayName": "Papyrus",
        "CFBundleGetInfoString": f"Papyrus HTML Converter {APP_VERSION}",
        "CFBundleIdentifier": "com.RazorBackRoar.papyrus",
        "CFBundleVersion": APP_VERSION,
        "CFBundleShortVersionString": APP_VERSION,
        "NSHumanReadableCopyright": "Copyright © 2025 RazorBackRoar",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSArchitecturePriority": ["arm64"],
        "PyRuntimeLocations": [
            "@executable_path/../Frameworks/Python.framework/Versions/3.13/Python"
        ],
    },
}

setup(
    app=APP,
    name="Papyrus",
    data_files=DATA_FILES,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    options={"py2app": OPTIONS},
)
