import tkinter as tk
from collections import deque
import asyncio
import threading
import random

class TranscriptionWindow:
    def __init__(self, max_lines=50):
        self.root = tk.Tk()
        self.root.title("Live Transcription")
        self.root.geometry("900x300")
        self.texts = deque(maxlen=max_lines)

        tk.Frame(self.root, height=100).pack()

        self.text_widget = tk.Text(
            self.root,
            height=max_lines,
            width=100,
            font=("Courier", 13),
            wrap=tk.WORD
        )
        self.text_widget.pack(pady=10)
        self.text_widget.config(state=tk.DISABLED)

    def append(self, line: str):
        self.texts.append(line)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "\n".join(self.texts))
        self.text_widget.config(state=tk.DISABLED)

    def start(self):
        self.root.mainloop()
