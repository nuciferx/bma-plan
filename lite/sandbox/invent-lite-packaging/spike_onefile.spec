# -*- mode: python ; coding: utf-8 -*-
# Spike: one-file PyInstaller build of BMA-Plan Lite (Artifact A).
# Based on the working precedent proto/BMA-Plan.spec (collect_all pattern) +
# proto/build.bat (uvicorn/multipart hidden imports), extended for lite:
#   - server_lite.py bundled as DATA (uvicorn imports it via import string
#     from sys._MEIPASS/lite — see launch_wrapper_a.py)
#   - ui-lite.html, lite-report.html, static/** bundled under lite/
#   - openpyxl (lazy import in /export-xlsx) + aiofiles collected explicitly
import os
from PyInstaller.utils.hooks import collect_all

LITE_DIR = os.path.abspath(os.path.join(SPECPATH, "..", ".."))  # -> <repo>/lite

datas = [
    (os.path.join(LITE_DIR, "server_lite.py"), "lite"),
    (os.path.join(LITE_DIR, "ui-lite.html"), "lite"),
    (os.path.join(LITE_DIR, "lite-report.html"), "lite"),
]
binaries = []
hiddenimports = ["fitz", "multipart", "python_multipart", "email.mime.multipart"]
for pkg in ("pymupdf", "uvicorn", "fastapi", "starlette", "openpyxl", "aiofiles", "anyio"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# static tree -> lite/static/**
static_tree = Tree(os.path.join(LITE_DIR, "static"), prefix=os.path.join("lite", "static"))

a = Analysis(
    [os.path.join(SPECPATH, "launch_wrapper_a.py")],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    static_tree,
    [],
    name="BMA-Plan-Lite-A",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
