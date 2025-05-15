import asyncio

from ui import TranscriptionWindow
from rt_translate import translation_loop

import time

def test_printing(ui):
    i = 0
    while True:
        time.sleep(0.1)
        ui.root.after(0, ui.append, f"Test {i}")
        i += 1

def run_translation(ui: TranscriptionWindow):
    try:
        asyncio.run(translation_loop(ui))

    except KeyboardInterrupt:
        pass

def main():
    ui = TranscriptionWindow(test_printing)
    ui.start()

if __name__ == "__main__":
    main()
