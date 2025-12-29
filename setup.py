"""
Setup script for creating a macOS .app bundle using py2app
"""
from setuptools import setup

APP = ['menubar_app.py']
DATA_FILES = [
    # Include config JSON file if it exists
    ('.', ['.proxi_lock_config.json']) if __import__('os').path.exists('.proxi_lock_config.json') else None
]
OPTIONS = {
    'argv_emulation': False,  # Don't use argv emulation for menu bar apps
    'plist': {
        'CFBundleName': 'Proxi-Lock',
        'CFBundleDisplayName': 'Proxi-Lock',
        'CFBundleGetInfoString': 'Proximity-based Mac screen lock/unlock',
        'CFBundleIdentifier': 'com.proxi-lock.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024',
        'LSBackgroundOnly': False,  
        'LSUIElement': True,  
        'NSHighResolutionCapable': True,
        'NSBluetoothAlwaysUsageDescription': 'Proxi-Lock needs Bluetooth access to detect your device proximity.',
        'NSBluetoothPeripheralUsageDescription': 'Proxi-Lock needs Bluetooth access to detect your device proximity.',
    },
    'packages': [
        'rumps',
        'bleak',
        'asyncio',
        'threading',
        'config',
        'scanner',
        'controller',
        'lock_manager',
        'lock_security',
        'main',
        'native_dialogs',
        'sleep_watcher',
    ],
    'includes': [
        'rumps',
        'bleak',
        'asyncio',
        'threading',
        'time',
        'json',
        'subprocess',
        'getpass',
        'enum',
        'AppKit',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
    ],
    'iconfile': 'icon.icns',  # App icon file
}

# Filter out None values from DATA_FILES
DATA_FILES = [f for f in DATA_FILES if f is not None]

setup(
    app=APP,
    name='Proxi-Lock',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

