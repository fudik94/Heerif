"""Global hotkey listener using the keyboard library for the Heerif layout switcher."""

from typing import Callable
import keyboard


class HotkeyManager:
    def __init__(self, hotkey_str: str, callback: Callable[[], None]) -> None:
        self._hotkey_str = hotkey_str
        self._callback = callback
        self._hotkey_ref = None  # handle returned by keyboard.add_hotkey

    def start(self) -> None:
        """Register the global hotkey. No-op if already running.

        Raises ValueError if the hotkey string is invalid.
        """
        if self._hotkey_ref is not None:
            return
        try:
            self._hotkey_ref = keyboard.add_hotkey(self._hotkey_str, self._callback)
        except ValueError as exc:
            raise ValueError(
                f"Invalid hotkey {self._hotkey_str!r}: {exc}"
            ) from exc

    def stop(self) -> None:
        """Unregister the global hotkey and reset internal state."""
        if self._hotkey_ref is not None:
            keyboard.remove_hotkey(self._hotkey_ref)
            self._hotkey_ref = None

    def update_hotkey(self, new_hotkey_str: str) -> None:
        """Stop current hotkey, update hotkey string, and restart."""
        self.stop()
        self._hotkey_str = new_hotkey_str
        self.start()
