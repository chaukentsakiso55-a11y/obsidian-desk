import os
import tkinter as tk

def render(parent):
    try:
        import psutil
        process = psutil.Process(os.getpid())
        ram = process.memory_info().rss / 1048576
        cpu = psutil.cpu_percent(interval=None)
        info = f"Application RAM: {ram:.1f} MB\nSystem CPU: {cpu:.1f}%\nProcess ID: {os.getpid()}"
    except ImportError:
        info = "Install psutil for live RAM and CPU metrics.\nProcess ID: " + str(os.getpid())
    tk.Label(parent, text=info, bg="#080d17", fg="#d7ecff", justify="left", font=("Segoe UI", 14)).pack(anchor="w", padx=32)
    tk.Label(parent, text="Modules load on demand to reduce idle resource usage.", bg="#080d17", fg="#8b9aaf").pack(anchor="w", padx=32, pady=18)
