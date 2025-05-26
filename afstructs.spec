# -*- mode: python ; coding: utf-8 -*-

import os

production_path = os.path.abspath('production')

a = Analysis(
    [os.path.join('production', 'control.py')],  # Explicit path to control.py
    pathex=[production_path],                    # Include production path for relative imports
    binaries=[],
    datas=[(os.path.join('production', 'icon.ico'), '.')],  
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PySide6'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='afstructs',  # This is the name of your executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

