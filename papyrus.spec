# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import PySide6

# --- Project-Specific Configuration ---
project_root = os.path.abspath(os.getcwd())
app_name = 'Papyrus'
main_script = os.path.join(project_root, 'src', 'main.py')
icon_file = os.path.join(project_root, 'src', 'assets', 'papyrus.icns')

# --- Analysis: Finding Dependencies ---
a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/assets', 'assets'),
        (os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins'), 'PySide6/Qt/plugins')
    ],
    hiddenimports=['PySide6'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)

# --- PYZ, EXE, COLLECT sections ---
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name
)

# --- BUNDLE (The macOS .app structure) ---
app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon=icon_file,
    bundle_identifier='com.RazorBackRoar.papyrus',
    info_plist={
        'CFBundleName': app_name,
        'CFBundleDisplayName': app_name,
        'CFBundleGetInfoString': 'Papyrus HTML Converter, Copyright 2025 RazorBackRoar',
        'CFBundleIdentifier': 'com.RazorBackRoar.papyrus',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'LSMinimumSystemVersion': '12.0',
        'NSHumanReadableCopyright': 'Copyright 2025 RazorBackRoar. All rights reserved.',
        'NSHighResolutionCapable': 'True',
    }
)
