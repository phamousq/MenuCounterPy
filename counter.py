from AppKit import (NSApplication, NSStatusBar, 
                      NSMenu, NSMenuItem,
                      NSEventTypeRightMouseDown, NSEventTypeLeftMouseDown)
from PyObjCTools import AppHelper

class CounterApp:
    def __init__(self):
        self.counter = 0
        self.app = NSApplication.sharedApplication()
        
        # Create the status item in the menu bar with fixed width
        self.statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = self.statusbar.statusItemWithLength_(40)
        
        # Create the menu
        self.menu = NSMenu.alloc().init()
        reset_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Reset Counter", "resetCounter:", "")
        reset_item.setTarget_(self)
        self.menu.addItem_(reset_item)
        
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", "")
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
    
    def resetCounter_(self, sender):
        self.counter = 0
        self.update_title()
    
    def increment_(self, sender):
        self.counter += 1
        self.update_title()
    
    def update_title(self):
        self.button.setTitle_(f"{self.counter}")
    
    def run(self):
        self.app.activateIgnoringOtherApps_(True)
        AppHelper.runEventLoop()

if __name__ == "__main__":
    app = CounterApp()
    app.run()