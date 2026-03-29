# -*- mode: python ; coding: utf-8 -*-
import os


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('modules', 'modules'),
        ('interfaces', 'interfaces'),
        ('icon.png', '.')
    ],
    hiddenimports=['modules', 'interfaces', 'interfaces.arduino_obi', 'modules.makita_lxt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenBatteryInformation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns' if os.path.exists('icon.icns') else 'icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='OpenBatteryInformation',
)

app = BUNDLE(
    coll,
    name='OpenBatteryInformation.app',
    icon='icon.icns' if os.path.exists('icon.icns') else 'icon.png',
    bundle_identifier='com.obi.openbatteryinformation',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '0.1.0',
    },
)
