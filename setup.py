from setuptools import setup

APP = ['counter.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Changed to False to avoid launch issues
    'plist': {
        'LSUIElement': True,  # Makes it a "background" app without a dock icon
        'CFBundleName': 'MenuCounter',
        'CFBundleDisplayName': 'MenuCounter',
        'CFBundleIdentifier': 'com.menubar.counter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
    'packages': ['Foundation', 'AppKit', 'objc', 'pyobjc'],
    'frameworks': ['Cocoa'],
    'includes': ['Foundation', 'AppKit', 'objc', 'pyobjc'],
    'resources': [],
    'excludes': ['tkinter', 'matplotlib', 'numpy'],  # Exclude unnecessary packages
}

setup(
    app=APP,
    name='MenuCounter',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pyobjc-core>=10.1',
        'pyobjc-framework-Cocoa>=10.1',
    ],
)
