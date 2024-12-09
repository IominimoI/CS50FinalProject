# -*- mode: python ; coding: utf-8 -*-

added_files = [
    ('venv/lib/python3.13/site-packages/customtkinter', 'customtkinter'),
    ('venv/lib/python3.13/site-packages/nltk', 'nltk')
]

a = Analysis(['pmg_gui.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['nltk', 'sqlite3', 'cryptography'],
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
    name='PMG Secure',
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
app = BUNDLE(
    exe,
    name='PMG Secure.app',
    icon=os.path.join(os.getcwd(), 'assets/Pmg.icns'),
    bundle_identifier='com.Iomin.pmgsecure', 
    info_plist={
        'CFBundleShortVersionString': '1.0.0',  # Version
        'CFBundleGetInfoString': 'PMG Secure, Created by Nico Geromin',  # Info
        'NSHumanReadableCopyright': 'Copyright © 2024 Nico Geromin'  # Copyright
    }
)
