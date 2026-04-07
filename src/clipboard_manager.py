"""Clipboard save/restore and selection detection for the conversion pipeline."""
import time
import pyperclip
from pynput import keyboard


class ClipboardManager:
    def __init__(self) -> None:
        self._saved: str = ''

    def save(self) -> None:
        try:
            self._saved = pyperclip.paste()
        except Exception:
            self._saved = ''

    def restore(self) -> None:
        try:
            pyperclip.copy(self._saved)
        except Exception:
            pass

    def get(self) -> str:
        try:
            return pyperclip.paste()
        except Exception:
            return ''

    def set(self, text: str) -> None:
        try:
            pyperclip.copy(text)
        except Exception:
            pass

    def get_selection(self) -> str | None:
        """Simulate Ctrl+C and return selected text, or None if nothing changed."""
        before = self.get()
        ctrl = keyboard.Controller()
        ctrl.press(keyboard.Key.ctrl)
        ctrl.press('c')
        ctrl.release('c')
        ctrl.release(keyboard.Key.ctrl)
        time.sleep(0.1)
        after = self.get()
        # Return None if clipboard is empty or unchanged — neither represents a real selection
        if after and after != before:
            return after
        return None
