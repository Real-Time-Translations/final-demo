import tkinter as tk
from tkinter import ttk

from collections import deque
import asyncio
import threading
import random

class TranscriptionWindow:
    def __init__(self, printing_function, max_lines=10):
        self.printing_thread = threading.Thread(target=printing_function, args=(self,), daemon=True)

        self.root = tk.Tk()
        self.root.title("Live Transcription")
        self.texts = deque(maxlen=max_lines)
        self.started = False

        self.langs = ["Russian",  "Romanian", "English"]
        self.selected_lang = tk.StringVar(value=self.langs[0])

        self.root.geometry("900x300")
        self.top_padding = tk.Frame(self.root, height=200)
        self.top_padding.pack()

        self.text_widget = tk.Text(
            self.root,
            height=max_lines,
            width=100,
            font=("Courier", 20),
            wrap=tk.WORD
        )

        self.text_widget.pack(pady=10)
        self.text_widget.config(state=tk.DISABLED)

        self.dropdown = ttk.Combobox(
            self.root,
            font=("Courier", 20),
            textvariable=self.selected_lang,
            values=self.langs,
            state="readonly"
        )

        self.dropdown.pack(pady=5)
        self.button = tk.Button(
            self.root,
            text="Start",
            command=self.on_click,
            font=("Courier", 20),
        )

        self.button.pack(pady=5)

    def on_click(self):
        if not self.started:
            self.printing_thread.start()

        self.started = True
        self.button.config(text="Start" if not self.started else "Running")

    def append(self, line: str):
        self.texts.append(line)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)

        padding = max(0, self.text_widget.cget("height") - len(self.texts))
        if padding > 0:
            self.text_widget.insert(tk.END, "\n" * padding)

        self.text_widget.insert(tk.END, "\n".join(self.texts))
        self.text_widget.config(state=tk.DISABLED)


    def start(self):
        self.root.mainloop()
