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
  - pyinstaller main.py --add-data="counter.db:."  -n MenuBarCounter -F -w -y --clean   
  - .counter.db file will be located in ~/
  - file will be in dist folder