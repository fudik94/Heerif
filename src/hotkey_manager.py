"""Global hotkey listener using pynput HotKey for the Heerif layout switcher."""

from typing import Callable
from pynput import keyboard


_MODIFIER_KEYS = {'ctrl', 'alt', 'shift', 'cmd', 'space', 'enter', 'tab', 'esc',
                  'backspace', 'delete', 'home', 'end', 'insert', 'f1', 'f2',
                  'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'}


class HotkeyManager:
    def __init__(self, hotkey_str: str, callback: Callable[[], None]) -> None:
        self._hotkey_str = hotkey_str
        self._callback = callback
        self._listener: keyboard.Listener | None = None
        self._hotkey_obj: keyboard.HotKey | None = None

    def _format_hotkey(self, hotkey_str: str) -> str:
        """Convert 'ctrl+space' format to pynput format '<ctrl>+<space>'."""
        parts = [p.strip().lower() for p in hotkey_str.split('+')]
        formatted = []
        for part in parts:
            if part in _MODIFIER_KEYS or len(part) > 1:
                formatted.append(f'<{part}>')
            else:
                formatted.append(part)
        return '+'.join(formatted)

    def start(self) -> None:
        """Start listening for the configured hotkey. No-op if already running."""
        if self._listener is not None:
            return
        formatted = self._format_hotkey(self._hotkey_str)
        self._hotkey_obj = keyboard.HotKey(
            keyboard.HotKey.parse(formatted),
            self._callback,
        )
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Stop the hotkey listener and reset internal state."""
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._hotkey_obj = None

    def update_hotkey(self, new_hotkey_str: str) -> None:
        """Stop current listener, update hotkey string, and restart listener."""
        self.stop()
        self._hotkey_str = new_hotkey_str
        self.start()

    def _on_press(self, key) -> None:
        if self._hotkey_obj and self._listener:
            self._hotkey_obj.press(self._listener.canonical(key))

    def _on_release(self, key) -> None:
        if self._hotkey_obj and self._listener:
            self._hotkey_obj.release(self._listener.canonical(key))
