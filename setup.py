from setuptools import setup

APP = ["src/time_announcer/app.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "packages": ["time_announcer"],
    "includes": ["PySide6", "pyttsx3.drivers", "pyttsx3.drivers.nsss"],
    "iconfile": "icons/app_icon.icns",
    "plist": {
        "CFBundleName": "Time Announcer",
        "CFBundleDisplayName": "Time Announcer",
        "CFBundleIdentifier": "com.mohamednadirsaidi.timeannouncer",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "LSUIElement": True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
)