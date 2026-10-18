import os
import platform
import shutil
import subprocess
import tkinter as tk
from datetime import datetime

try:
    import psutil
except Exception:
    psutil = None

BG = "#05070d"
PANEL = "#0d1524"
CARD = "#111d31"
CYAN = "#55e7ff"
VIOLET = "#9b7bff"
TEXT = "#d7ecff"
MUTED = "#8295ad"

class MarkLIV(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MARK LIV — Legacy Linux Port")
        self.geometry("1050x680")
        self.minsize(760, 500)
        self.configure(bg=BG)

        left = tk.Frame(self, bg=PANEL, width=210)
        left.pack(side="left", fill="y")
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(side="right", fill="both", expand=True)

        tk.Label(left, text="MARK LIV", bg=PANEL, fg=CYAN, font=("Sans", 20, "bold")).pack(pady=(28, 2))
        tk.Label(left, text="LEGACY LINUX PORT", bg=PANEL, fg=MUTED, font=("Sans", 9)).pack(pady=(0, 24))

        for name, fn in [
            ("Dashboard", self.dashboard),
            ("Assistant", self.assistant),
            ("Files", self.open_files),
            ("Terminal", self.open_terminal),
        ]:
            tk.Button(
                left,
                text=name,
                command=fn,
                bg=CARD,
                fg=TEXT,
                activebackground="#18304d",
                activeforeground="white",
                relief="flat",
                anchor="w",
                padx=16,
                pady=12,
            ).pack(fill="x", padx=12, pady=4)

        tk.Label(
            left,
            text="Obsidian Desk\ncompatibility edition",
            bg=PANEL,
            fg=MUTED,
            justify="left",
        ).pack(side="bottom", anchor="w", padx=18, pady=20)

        self.dashboard()

    def clear(self):
        for child in self.body.winfo_children():
            child.destroy()

    def title_block(self, title, subtitle):
        tk.Label(self.body, text=title, bg=BG, fg=CYAN, font=("Sans", 24, "bold")).pack(anchor="w", padx=32, pady=(28, 4))
        tk.Label(self.body, text=subtitle, bg=BG, fg=MUTED, font=("Sans", 10)).pack(anchor="w", padx=32, pady=(0, 18))

    def dashboard(self):
        self.clear()
        self.title_block("MARK LIV", "Legacy companion running inside Obsidian Desk")
        info = tk.Frame(self.body, bg=CARD)
        info.pack(fill="x", padx=32, pady=8)
        cpu = "Unavailable"
        ram = "Unavailable"
        if psutil:
            cpu = f"{psutil.cpu_percent(interval=0.15):.1f}%"
            vm = psutil.virtual_memory()
            ram = f"{vm.percent:.1f}%"
        details = [
            ("System", platform.system() + " " + platform.release()),
            ("Architecture", platform.machine()),
            ("CPU", cpu),
            ("RAM", ram),
            ("Python", platform.python_version()),
            ("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        for key, value in details:
            row = tk.Frame(info, bg=CARD)
            row.pack(fill="x", padx=18, pady=7)
            tk.Label(row, text=key, width=16, anchor="w", bg=CARD, fg=VIOLET, font=("Sans", 11, "bold")).pack(side="left")
            tk.Label(row, text=value, anchor="w", bg=CARD, fg=TEXT, font=("Sans", 11)).pack(side="left")

    def assistant(self):
        self.clear()
        self.title_block("Assistant", "Local legacy command console")
        output = tk.Text(self.body, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", height=18)
        output.pack(fill="both", expand=True, padx=32, pady=8)
        output.insert("end", "MARK LIV ready. Try: time, system, files, terminal\n")
        entry = tk.Entry(self.body, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat")
        entry.pack(fill="x", padx=32, pady=(6, 28), ipady=10)

        def run(_=None):
            query = entry.get().strip().lower()
            entry.delete(0, "end")
            output.insert("end", f"> {query}\n")
            if query in {"time", "date"}:
                answer = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
            elif query in {"system", "status"}:
                answer = f"{platform.system()} {platform.release()} · {platform.machine()}"
            elif query in {"files", "open files"}:
                self.open_files()
                answer = "Opening file manager."
            elif query in {"terminal", "open terminal"}:
                self.open_terminal()
                answer = "Opening terminal."
            elif not query:
                return
            else:
                answer = "Legacy offline mode only. AI provider integration is not bundled."
            output.insert("end", answer + "\n")
            output.see("end")

        entry.bind("<Return>", run)
        entry.focus_set()

    def launch_first(self, names):
        for name in names:
            path = shutil.which(name)
            if path:
                subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
        return False

    def open_files(self):
        if not self.launch_first(["thunar", "caja", "pcmanfm-qt", "dolphin"]):
            self._notice("No supported file manager is installed.")

    def open_terminal(self):
        if not self.launch_first(["xfce4-terminal", "mate-terminal", "qterminal", "konsole"]):
            self._notice("No supported terminal is installed.")

    def _notice(self, message):
        win = tk.Toplevel(self)
        win.configure(bg=PANEL)
        win.title("MARK LIV")
        tk.Label(win, text=message, bg=PANEL, fg=TEXT, padx=24, pady=20).pack()
        tk.Button(win, text="OK", command=win.destroy, bg=CARD, fg=TEXT, relief="flat", padx=18, pady=8).pack(pady=(0, 18))

if __name__ == "__main__":
    MarkLIV().mainloop()
