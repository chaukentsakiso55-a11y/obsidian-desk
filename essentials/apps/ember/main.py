import tkinter as tk
from tkinter import ttk
import importlib
import os
import time

MODULES = {
    "AI Chat": "modules.chat",
    "Obsidian Security": "modules.security",
    "Evolution Learning": "modules.evolution",
    "Pulsa AI": "modules.pulsa",
    "System Intel": "modules.system_intel",
}

class EmberV11(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMBER V11 — Powered by OBSIDIAN")
        self.geometry("1100x700")
        self.minsize(780, 500)
        self.configure(bg="#080d17")
        self.modules = {}
        self.nav = tk.Frame(self, bg="#0d1728", width=210)
        self.nav.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg="#080d17")
        self.content.pack(side="right", fill="both", expand=True)
        tk.Label(self.nav, text="EMBER V11", bg="#0d1728", fg="#6ddcff", font=("Segoe UI", 19, "bold")).pack(pady=(28, 4))
        tk.Label(self.nav, text="POWERED BY OBSIDIAN", bg="#0d1728", fg="#8b9aaf", font=("Segoe UI", 9)).pack(pady=(0, 24))
        for name in MODULES:
            tk.Button(self.nav, text=name, command=lambda n=name: self.open_module(n), bg="#12233a", fg="#d7ecff", activebackground="#173a58", activeforeground="white", relief="flat", anchor="w", padx=14, pady=12).pack(fill="x", padx=12, pady=4)
        self.open_module("System Intel")

    def open_module(self, name):
        for child in self.content.winfo_children():
            child.destroy()
        tk.Label(self.content, text=name, bg="#080d17", fg="#6ddcff", font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=32, pady=(28, 16))
        try:
            if name not in self.modules:
                self.modules[name] = importlib.import_module(MODULES[name])
            self.modules[name].render(self.content)
        except Exception as exc:
            tk.Label(self.content, text=f"Module unavailable: {exc}", bg="#080d17", fg="#ff8e8e", wraplength=600).pack(anchor="w", padx=32)

if __name__ == "__main__":
    EmberV11().mainloop()
