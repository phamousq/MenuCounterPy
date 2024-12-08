import logging

import gspread
from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSEventTypeLeftMouseDown,
    NSEventTypeRightMouseDown,
    NSMenu,
    NSMenuItem,
    NSStatusBar,
)
from google.oauth2.service_account import Credentials
from PyObjCTools import AppHelper

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "Stoked Capsule JSON - Google Cloud Console.json", scopes=scopes
)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1BOhvQ4tHX6jYTD-L7-vUyUmRA4dTD5xeWONrSoDlcY4"
SHEET_NAME = "Sheet1"
API_KEY = "AIzaSyBqBlePNGkZ4BGRHvjHuMcouPwkUE7qDR0"

sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


class CounterAPI:
    def __init__(self, namespace: str = "test", name: str = "test"):
        pass  # Ignore the parameters as we're using Google Sheets

    def get_count(self) -> int:
        """Return the value in cell C1"""
        try:
            return int(sheet.acell("C1").value)
        except Exception as e:
            logging.error(f"Error getting count: {e}")
            return 0

    def increment(self) -> int:
        """Increment the value in cell C1 by one"""
        try:
            cell = sheet.acell("C1")
            new_value = str(int(cell.value) + 1)
            sheet.update_acell("C1", new_value)
            return int(new_value)
        except Exception as e:
            logging.error(f"Error incrementing count: {e}")
            return self.get_count()

    def reset(self) -> int:
        """Reset the value in cell C1 to 0"""
        try:
            sheet.update_acell("C1", 0)
            return 0
        except Exception as e:
            logging.error(f"Error resetting count: {e}")
            return 0


class CounterApp:
    def __init__(self, initial_value: int = 0):
        self.counter = CounterAPI()
        self.count = self.counter.get_count()
        self.isLong = True
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
        if event.type() == NSEventTypeLeftMouseDown:
            self.count = self.counter.increment()
            self.update_title()
        elif event.type() == NSEventTypeRightMouseDown:
            self.statusitem.popUpStatusItemMenu_(self.menu)

    def resize_(self, sender):
        self.isLong = not self.isLong
        self.text = "Count: " if self.isLong else ""
        self.statusitem.setLength_(-1 if self.text else 40)
        self.update_title()

    def resetCounter_(self, sender):
        self.count = self.counter.reset()
        self.update_title()

    def update_title(self):
        self.button.setTitle_(f"{self.text}{self.count}")

    def run(self):
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        self.app.activateIgnoringOtherApps_(True)
        AppHelper.runEventLoop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    app = CounterApp()
    app.run()
