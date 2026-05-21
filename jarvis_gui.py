import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from jarvis import Jarvis, VoiceListener


class JarvisGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Local JARVIS")
        self.root.geometry("960x640")
        self.root.minsize(820, 540)
        self.root.configure(bg="#08111f")

        self.jarvis = Jarvis(voice=False)
        self.is_listening = False
        self.recognition_mode = tk.StringVar(value="offline")
        self.status_text = tk.StringVar(value="Ready")
        self.command_text = tk.StringVar()

        self.configure_styles()
        self.build_layout()
        self.log("JARVIS", "GUI online. Type a command or use Listen Once.")

    def configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#08111f")
        style.configure("Panel.TFrame", background="#101c2f", relief="flat")
        style.configure(
            "Title.TLabel",
            background="#08111f",
            foreground="#e7f1ff",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#08111f",
            foreground="#7fa8d8",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Status.TLabel",
            background="#101c2f",
            foreground="#a9f0c8",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TButton",
            background="#1d3557",
            foreground="#f7fbff",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("TButton", background=[("active", "#2e5c94")])
        style.configure("TEntry", fieldbackground="#edf5ff", padding=8)
        style.configure("TCombobox", fieldbackground="#edf5ff", padding=6)

    def build_layout(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer)
        header.pack(fill=tk.X)

        title_block = ttk.Frame(header)
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(title_block, text="Local JARVIS", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_block,
            text="Laptop assistant for apps, notes, websites, and system commands",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        status = ttk.Frame(header, style="Panel.TFrame", padding=(14, 10))
        status.pack(side=tk.RIGHT)
        ttk.Label(status, textvariable=self.status_text, style="Status.TLabel").pack()

        body = ttk.Frame(outer)
        body.pack(fill=tk.BOTH, expand=True, pady=(18, 0))

        left = ttk.Frame(body, style="Panel.TFrame", padding=14)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.log_box = scrolledtext.ScrolledText(
            left,
            bg="#07101f",
            fg="#dcecff",
            insertbackground="#dcecff",
            relief=tk.FLAT,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=14,
            pady=14,
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)
        self.log_box.configure(state=tk.DISABLED)

        command_row = ttk.Frame(left, style="Panel.TFrame")
        command_row.pack(fill=tk.X, pady=(12, 0))

        entry = ttk.Entry(command_row, textvariable=self.command_text)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", lambda _event: self.send_command())
        entry.focus_set()

        ttk.Button(command_row, text="Send", command=self.send_command).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        right = ttk.Frame(body, style="Panel.TFrame", padding=14)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(16, 0))

        ttk.Label(
            right,
            text="Voice",
            background="#101c2f",
            foreground="#e7f1ff",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")

        ttk.Combobox(
            right,
            textvariable=self.recognition_mode,
            values=("offline", "online", "auto"),
            state="readonly",
            width=18,
        ).pack(fill=tk.X, pady=(8, 8))

        ttk.Button(right, text="Listen Once", command=self.listen_once).pack(fill=tk.X)

        ttk.Label(
            right,
            text="Quick Actions",
            background="#101c2f",
            foreground="#e7f1ff",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(22, 8))

        actions = [
            ("Apps", "apps"),
            ("Time", "time"),
            ("System Info", "system info"),
            ("Open Chrome", "open chrome"),
            ("Open Netflix", "open netflix"),
            ("Visit YouTube", "visit youtube"),
            ("Refresh Apps", "refresh apps"),
        ]
        for label, command in actions:
            ttk.Button(
                right,
                text=label,
                command=lambda value=command: self.run_command(value),
            ).pack(fill=tk.X, pady=3)

        ttk.Label(
            right,
            text="Known Apps",
            background="#101c2f",
            foreground="#e7f1ff",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(22, 8))

        apps = ", ".join(self.jarvis.available_app_names())
        self.apps_label = tk.Message(
            right,
            text=apps,
            bg="#101c2f",
            fg="#aecaef",
            width=220,
            font=("Segoe UI", 9),
        )
        self.apps_label.pack(fill=tk.X)

    def send_command(self) -> None:
        command = self.command_text.get().strip()
        if not command:
            return
        self.command_text.set("")
        self.run_command(command)

    def run_command(self, command: str) -> None:
        self.log("You", command)
        try:
            result = self.jarvis.handle(command)
        except Exception as exc:
            messagebox.showerror("JARVIS error", str(exc))
            self.log("JARVIS", f"Error: {exc}")
            return

        if result == "EXIT":
            self.root.destroy()
            return

        if result:
            self.log("JARVIS", result)
            if command.lower().strip() in {"refresh apps", "rescan apps", "scan apps"}:
                self.apps_label.configure(text=", ".join(self.jarvis.available_app_names()))

    def listen_once(self) -> None:
        if self.is_listening:
            return
        self.is_listening = True
        self.status_text.set("Listening...")
        threading.Thread(target=self.listen_worker, daemon=True).start()

    def listen_worker(self) -> None:
        mode = self.recognition_mode.get()
        listener = VoiceListener(recognition=mode)
        if not listener.available:
            self.root.after(
                0,
                lambda: self.finish_listening(
                    "",
                    f"Voice mode is not ready. {listener.error}",
                ),
            )
            return

        guesses = listener.listen()
        command = self.jarvis.best_voice_command(guesses) if guesses else ""
        if not command:
            self.root.after(
                0,
                lambda: self.finish_listening("", "I did not catch a JARVIS command."),
            )
            return

        self.root.after(0, lambda: self.finish_listening(command, None))

    def finish_listening(self, command: str, error: str | None) -> None:
        self.is_listening = False
        self.status_text.set("Ready")
        if error:
            self.log("JARVIS", error)
            return
        self.run_command(command)

    def log(self, speaker: str, message: str) -> None:
        self.log_box.configure(state=tk.NORMAL)
        self.log_box.insert(tk.END, f"{speaker}: {message}\n\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state=tk.DISABLED)


def main() -> None:
    root = tk.Tk()
    JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
