
import json
import os
from tkinter import messagebox
from src.ui.language_manager import get_translator

_ = get_translator()

class ShortcutManager:
    def __init__(self, resources_path):
        self.shortcuts = {}
        self.config_file = os.path.join(resources_path, 'shortcuts.json')
        self.load_shortcuts()

    def load_shortcuts(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.shortcuts = json.load(f)
            else:
                self.shortcuts = self.get_default_shortcuts()
                self.save_shortcuts()
        except Exception as e:
            messagebox.showerror(_("Error loading shortcuts"), str(e))
            self.shortcuts = self.get_default_shortcuts()

    def get_default_shortcuts(self):
        return {
            "file.open": "<Control-o>",
            "file.save": "<Control-s>",
            "code.run": "<F5>",
            "chat.send": "<Control-Return>"
        }

    def save_shortcuts(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            messagebox.showerror(_("Error saving shortcuts"), str(e))

    def get_shortcut(self, key):
        return self.shortcuts.get(key)

    def set_shortcut(self, key, value):
        self.shortcuts[key] = value
        self.save_shortcuts()

_shortcut_manager = None

def get_shortcut_manager(resources_path=None):
    global _shortcut_manager
    if _shortcut_manager is None and resources_path is not None:
        _shortcut_manager = ShortcutManager(resources_path)
    return _shortcut_manager
