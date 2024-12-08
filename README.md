# MenuCounterPy

A simple yet powerful menu bar counter application for macOS.

## Features
- Persistent counter that saves state between app restarts
- Toggle between compact and full display modes
- View weekly statistics via system notifications
- SQLite database for reliable data storage
- Historical tracking of all counter changes

## Data Storage
- Counter data is stored in `~/.counter.db`
- Tracks counter values, display preferences, and click history
- Maintains a 7-day history of counter usage

## Usage
- Left-click to increment counter
- Right-click to access menu:
  - Toggle Size: Switch between "Count: X" and "X" display
  - Reset Counter: Set counter back to 0
  - Show Stats: View past week's click counts
  - Quit: Exit application

## Development
- using uv to manage dependencies
  - uv init 
  - uv venv
  - source .venv/bin/activate
  - uv sync


## Building
- Using PyInstaller:
  - pyinstaller main.py -n MenuBarCounter -F -w -y --clean   
  - .counter.db file will be located in ~/
  - file will be in dist folder

## Next Steps
- error: 
  - Traceback (most recent call last):
  File "main.py", line 18, in <module>
  File "google/oauth2/service_account.py", line 260, in from_service_account_file
  File "google/auth/_service_account_info.py", line 78, in from_filename
FileNotFoundError: [Errno 2] No such file or directory: 'Stoked Capsule JSON - Google Cloud Console.json'
[PYI-30829:ERROR] Failed to execute script 'main' due to unhandled exception: [Errno 2] No such file or directory: 'Stoked Capsule JSON - Google Cloud Console.json'
[PYI-30829:ERROR] Traceback:
Traceback (most recent call last):
  File "main.py", line 18, in <module>
  File "google/oauth2/service_account.py", line 260, in from_service_account_file
  File "google/auth/_service_account_info.py", line 78, in from_filename
FileNotFoundError: [Errno 2] No such file or directory: 'Stoked Capsule JSON - Google Cloud Console.json'


Saving session...
...copying shared history...
...saving history...truncating history files...
...completed.

[Process completed]
- don't know how else auth would be done.
- this should only work from the commandline...