# -*- mode: python ; coding: utf-8 -*-

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--cheap", action="store_true")
options = parser.parse_args()


icon_stem = "img/app"
icon_png = icon_stem + ".png"

if sys.platform == "win32":
    icon = icon_stem + ".ico"
elif sys.platform == "linux":
    icon = icon_png
elif sys.platform == "darwin":
    icon = icon_stem + ".icns"
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

if options.cheap:
    name = 'LazyAccCannonCalcCheap'
    src = 'src_cheap' 
else:
    name = 'LazyAccCannonCalc'
    src = 'src' 


a = Analysis(
    ['app/gui.py'],
    pathex=[],
    binaries=[],
    datas=[(src, 'src'), (icon, 'img'), (icon_png, 'img')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name=name,
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
    icon=icon,
)
