# pizdos :-0
import tkinter as tk
from collections import deque
import asyncio
import threading
import signal
import sys
import base64
import json
import subprocess
import requests
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedOK
from typing import TypedDict, Literal

from ui import TranscriptionWindow
from rt_translate import translation_loop

def run_translation(ui: TranscriptionWindow):
    try:
        asyncio.run(translation_loop(ui))
    except KeyboardInterrupt:
        pass

def main():
    ui = TranscriptionWindow()

    thread = threading.Thread(target=run_translation, args=(ui,), daemon=True)
    thread.start()
    ui.start()

if __name__ == "__main__":
    main()
