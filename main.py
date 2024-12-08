import os
from typing import List, Tuple

import duckdb
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
    def __init__(self):
        # Store database in user's home directory
        self.db_path = os.path.join(os.path.dirname(__file__), ".counter.duckdb")
        print(f"Opening database at {self.db_path}")
        self._connect()
        self.init_db()

    def _connect(self):
        """Ensure we have a valid connection"""
        try:
            # Test if connection is still valid
            if hasattr(self, "con"):
                try:
                    self.con.execute("SELECT 1").fetchone()
                    return
                except duckdb.Error:
                    # Connection is dead, close it
                    try:
                        self.con.close()
                    except duckdb.Error:
                        pass

            # Create new connection
            self.con = duckdb.connect(self.db_path, read_only=False)
            print("Created new database connection")
        except duckdb.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def _ensure_connection(self):
        """Decorator to ensure connection is valid before operations"""
        self._connect()

    def init_db(self):
        try:
            # Counters table stores the current state of each counter
            self.con.execute("""
                CREATE SEQUENCE IF NOT EXISTS counter_id_seq;
            """)

            self.con.execute("""
                CREATE TABLE IF NOT EXISTS counters (
                    id INTEGER PRIMARY KEY DEFAULT nextval('counter_id_seq'),
                    name VARCHAR UNIQUE,
                    current_value INTEGER DEFAULT 0,
                    display_format VARCHAR
                );
            """)

            # History table stores all counter changes
            self.con.execute("""
                CREATE SEQUENCE IF NOT EXISTS history_id_seq;
            """)

            self.con.execute("""
                CREATE TABLE IF NOT EXISTS counter_history (
                    id INTEGER PRIMARY KEY DEFAULT nextval('history_id_seq'),
                    counter_id INTEGER,
                    value INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (counter_id) REFERENCES counters (id)
                );
            """)
            print("Database initialized successfully")
        except duckdb.Error as e:
            print(f"Error initializing database: {e}")
            raise

    def get_or_create_counter(self, name: str = "default") -> Tuple[int, int, str]:
        """Returns (counter_id, current_value, display_format)"""
        try:
            self._ensure_connection()
            # Try to get existing counter
            result = self.con.execute(
                """
                SELECT id, current_value, display_format 
                FROM counters 
                WHERE name = ?
            """,
                [name],
            ).fetchone()

            if result:
                print(f"Found existing counter: {result}")
                return result

            print("Creating new counter")
            # Create new counter if it doesn't exist
            self.con.execute(
                """
                INSERT INTO counters (name, current_value, display_format) 
                VALUES (?, ?, ?)
            """,
                [name, 0, "long"],
            )

            result = self.con.execute(
                """
                SELECT id, current_value, display_format 
                FROM counters 
                WHERE name = ?
            """,
                [name],
            ).fetchone()
            print(f"Created new counter: {result}")
            return result
        except duckdb.Error as e:
            print(f"Error in get_or_create_counter: {e}")
            self._connect()  # Try to reconnect for next operation
            raise

    def increment_counter(self, counter_id: int) -> int:
        try:
            self._ensure_connection()
            # Update current value
            self.con.execute(
                """
                UPDATE counters 
                SET current_value = current_value + 1 
                WHERE id = ?
            """,
                [counter_id],
            )

            # Get new value
            new_value = self.con.execute(
                """
                SELECT current_value 
                FROM counters 
                WHERE id = ?
            """,
                [counter_id],
            ).fetchone()[0]

            # Record in history
            self.con.execute(
                """
                INSERT INTO counter_history (counter_id, value, timestamp) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
                [counter_id, new_value],
            )

            # print(f"Incremented counter {counter_id} to {new_value}")
            return new_value
        except duckdb.Error as e:
            print(f"Error incrementing counter: {e}")
            self._connect()  # Try to reconnect for next operation
            raise

    def reset_counter(self, counter_id: int):
        try:
            self._ensure_connection()
            self.con.execute(
                """
                UPDATE counters 
                SET current_value = 0 
                WHERE id = ?
            """,
                [counter_id],
            )

            self.con.execute(
                """
                INSERT INTO counter_history (counter_id, value, timestamp) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
                [counter_id, 0],
            )
            # print(f"Reset counter {counter_id}")
        except duckdb.Error as e:
            print(f"Error resetting counter: {e}")
            self._connect()  # Try to reconnect for next operation
            raise

    def update_display_format(self, counter_id: int, format: str):
        try:
            self._ensure_connection()
            self.con.execute(
                """
                UPDATE counters 
                SET display_format = ? 
                WHERE id = ?
            """,
                [format, counter_id],
            )
            # print(f"Updated display format for counter {counter_id} to {format}")
        except duckdb.Error as e:
            print(f"Error updating display format: {e}")
            self._connect()  # Try to reconnect for next operation
            raise

    def get_daily_stats(self, counter_id: int) -> List[Tuple[str, int]]:
        """Returns list of (date, count) tuples for the past week"""
        try:
            return self.con.execute(
                """
                SELECT date_trunc('day', timestamp)::DATE as day, COUNT(*) as clicks
                FROM counter_history
                WHERE counter_id = ?
                AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY day
                ORDER BY day
            """,
                [counter_id],
            ).fetchall()
        except duckdb.Error as e:
            print(f"Error getting daily stats: {e}")
            self._connect()  # Try to reconnect for next operation
            raise


class CounterApp:
    def __init__(self, initial_value: int = 0):
        self.db = CounterDB()
        self.counter_id, self.count, display_format = self.db.get_or_create_counter()
        self.isLong = display_format == "long"
        self.text = "Count: " if self.isLong else ""

        self.app = NSApplication.sharedApplication()

        # Create the status item in the menu bar with variable width
        self.statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = self.statusbar.statusItemWithLength_(
            -1
        )  # -1 means variable length

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
        title = f"{self.text}{self.count}"
        self.button.setTitle_(title)
        # Force button to update its size
        self.button.sizeToFit()

    def run(self):
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        self.app.activateIgnoringOtherApps_(True)
        AppHelper.runEventLoop()


if __name__ == "__main__":
    app = CounterApp()
    app.run()
