import os
import sqlite3
from datetime import datetime
from typing import List, Tuple

from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSEventTypeLeftMouseDown,
    NSEventTypeRightMouseDown,
    NSMenu,
    NSMenuItem,
    NSStatusBar,
)
from PyObjCTools import AppHelper


class CounterDB:
    def __init__(self, db_path: str = "counter.db"):
        # Store database in user's home directory
        self.db_path = os.path.expanduser(os.path.join("~", ".counter.db"))
        self.init_db()

    def _adapt_datetime(self, dt: datetime) -> str:
        """Convert datetime to string format for SQLite"""
        return dt.isoformat()

    def _convert_datetime(self, value: str) -> datetime:
        """Convert string from SQLite back to datetime"""
        return datetime.fromisoformat(value)

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Register datetime adapter and converter
            sqlite3.register_adapter(datetime, self._adapt_datetime)
            sqlite3.register_converter("datetime", self._convert_datetime)

            cursor = conn.cursor()
            # Counters table stores the current state of each counter
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS counters (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    current_value INTEGER,
                    display_format TEXT
                )
            """)
            # History table stores all counter changes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS counter_history (
                    id INTEGER PRIMARY KEY,
                    counter_id INTEGER,
                    value INTEGER,
                    timestamp datetime,  -- Note: lowercase datetime for type
                    FOREIGN KEY (counter_id) REFERENCES counters (id)
                )
            """)
            conn.commit()

    def get_or_create_counter(self, name: str = "default") -> Tuple[int, int, str]:
        """Returns (counter_id, current_value, display_format)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, current_value, display_format FROM counters WHERE name = ?",
                (name,),
            )
            result = cursor.fetchone()
            if result:
                return result

            # Create new counter if it doesn't exist
            cursor.execute(
                "INSERT INTO counters (name, current_value, display_format) VALUES (?, ?, ?)",
                (name, 0, "long"),
            )
            return (cursor.lastrowid, 0, "long")

    def increment_counter(self, counter_id: int) -> int:
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            # Update current value
            cursor.execute(
                "UPDATE counters SET current_value = current_value + 1 WHERE id = ?",
                (counter_id,),
            )
            # Get new value
            cursor.execute(
                "SELECT current_value FROM counters WHERE id = ?", (counter_id,)
            )
            new_value = cursor.fetchone()[0]
            # Record in history
            cursor.execute(
                "INSERT INTO counter_history (counter_id, value, timestamp) VALUES (?, ?, ?)",
                (counter_id, new_value, datetime.now()),
            )
            return new_value

    def reset_counter(self, counter_id: int):
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE counters SET current_value = 0 WHERE id = ?", (counter_id,)
            )
            cursor.execute(
                "INSERT INTO counter_history (counter_id, value, timestamp) VALUES (?, ?, ?)",
                (counter_id, 0, datetime.now()),
            )

    def update_display_format(self, counter_id: int, format: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE counters SET display_format = ? WHERE id = ?",
                (format, counter_id),
            )

    def get_daily_stats(self, counter_id: int) -> List[Tuple[str, int]]:
        """Returns list of (date, count) tuples for the past week"""
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT date(timestamp), COUNT(*)
                FROM counter_history
                WHERE counter_id = ?
                AND timestamp >= date('now', '-7 days')
                GROUP BY date(timestamp)
                ORDER BY date(timestamp)
            """,
                (counter_id,),
            )
            return cursor.fetchall()


class CounterApp:
    def __init__(self, initial_value: int = 0):
        self.db = CounterDB()
        self.counter_id, self.count, display_format = self.db.get_or_create_counter()
        self.isLong = display_format == "long"
        self.text = "Count: " if self.isLong else ""

        self.app = NSApplication.sharedApplication()

        # Create the status item in the menu bar with variable width
        self.statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = self.statusbar.statusItemWithLength_(-1 if self.text else 40)

        # Create the menu
        self.menu = NSMenu.alloc().init()

        # Buttons!
        toggle_size = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Toggle Size", "resize:", ""
        )
        toggle_size.setTarget_(self)
        self.menu.addItem_(toggle_size)

        reset_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Reset Counter", "resetCounter:", "r"
        )
        reset_item.setTarget_(self)
        self.menu.addItem_(reset_item)

        stats_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Show Stats", "showStats:", "s"
        )
        stats_item.setTarget_(self)
        self.menu.addItem_(stats_item)

        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", "q"
        )
        self.menu.addItem_(quit_item)

        # Set up the button
        self.button = self.statusitem.button()
        self.update_title()

        # Set up click handling
        self.button.setTarget_(self)
        self.button.setAction_("buttonClicked:")

        # Enable both left and right clicks
        self.button.sendActionOn_(1 << 1 | 1 << 3)

    def buttonClicked_(self, sender):
        event = NSApplication.sharedApplication().currentEvent()
        event_type = event.type()
        if event_type == NSEventTypeRightMouseDown:
            self.statusitem.popUpStatusItemMenu_(self.menu)
            NSApplication.sharedApplication().runModalForWindow_(None)
            NSApplication.sharedApplication().stopModal()
        elif event_type == NSEventTypeLeftMouseDown:
            self.increment_(sender)

    def resize_(self, sender):
        self.isLong = not self.isLong
        self.text = "Count: " if self.isLong else ""
        self.db.update_display_format(
            self.counter_id, "long" if self.isLong else "short"
        )
        self.update_title()

    def resetCounter_(self, sender):
        self.db.reset_counter(self.counter_id)
        self.count = 0
        self.update_title()

    def increment_(self, sender):
        self.count = self.db.increment_counter(self.counter_id)
        self.update_title()

    def showStats_(self, sender):
        stats = self.db.get_daily_stats(self.counter_id)
        if not stats:
            title = "No data available"
            message = ["No clicks recorded in the past week"]
        else:
            title = "Daily counts for the past week:"
            message = [f"{date}: {count} clicks" for date, count in stats]

        # Limit notification length and join with newlines for better readability
        message_text = "\\n".join(message[:7])  # Limit to 7 days
        command = f"""
        osascript -e 'display notification "{message_text}" with title "{title}"'
        """
        os.system(command)

    def update_title(self):
        self.button.setTitle_(f"{self.text}{self.count}")

    def run(self):
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        self.app.activateIgnoringOtherApps_(True)
        AppHelper.runEventLoop()


if __name__ == "__main__":
    app = CounterApp()
    app.run()
