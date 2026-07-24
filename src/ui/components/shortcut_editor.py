
import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.language_manager import get_translator

_ = get_translator()

class ShortcutEditor(tk.Toplevel):
    def __init__(self, parent, shortcut_manager):
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.title(_("Customize Shortcuts"))
        self.geometry("400x300")

        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(main_frame, columns=("shortcut",), show="headings")
        self.tree.heading("shortcut", text=_("Shortcut"))
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_tree()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text=_("Edit"), command=self.edit_shortcut).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=_("Reset to Default"), command=self.reset_shortcut).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=_("Close"), command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for key, value in self.shortcut_manager.shortcuts.items():
            self.tree.insert("", "end", values=(key, value), iid=key)

    def edit_shortcut(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning(_("No selection"), _("Please select a shortcut to edit."))
            return

        key = selected_item
        old_shortcut = self.shortcut_manager.get_shortcut(key)

        new_shortcut = tk.simpledialog.askstring(_("Edit Shortcut"), _("Enter new shortcut for {key}:").format(key=key), initialvalue=old_shortcut)

        if new_shortcut and new_shortcut != old_shortcut:
            self.shortcut_manager.set_shortcut(key, new_shortcut)
            self.populate_tree()
            messagebox.showinfo(_("Shortcut updated"), _("The new shortcut will be applied after restarting the application."))

    def reset_shortcut(self):
        if messagebox.askyesno(_("Reset Shortcuts"), _("Are you sure you want to reset all shortcuts to their default values?")):
            self.shortcut_manager.shortcuts = self.shortcut_manager.get_default_shortcuts()
            self.shortcut_manager.save_shortcuts()
            self.populate_tree()
            messagebox.showinfo(_("Shortcuts reset"), _("Default shortcuts will be applied after restarting the application."))

