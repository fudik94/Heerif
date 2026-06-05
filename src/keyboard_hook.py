"""Global keyboard listener and ring buffer for tracking recent keystrokes."""
from collections import deque
from pynput import keyboard

_MODIFIER_KEYS = {
    keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
}


class KeystrokeBuffer:
    def __init__(self, max_size: int = 200):
        self._buffer: deque[str] = deque(maxlen=max_size)

    def add(self, char: str) -> None:
        self._buffer.append(char)

    def peek(self, n: int) -> str:
        """Return the last n characters without removing them. Returns fewer if buffer has less than n chars."""
        return ''.join(list(self._buffer)[-n:]) if n > 0 else ''

    def pop(self, n: int) -> str:
        """Remove and return the last n characters. If n exceeds buffer size, returns all chars."""
        n = min(n, len(self._buffer))
        chars = list(self._buffer)[-n:]
        for _ in range(n):
            self._buffer.pop()
        return ''.join(chars)

    def clear(self) -> None:
        """Clear all characters from the buffer."""
        self._buffer.clear()


class KeyboardHook:
    def __init__(self, buffer: KeystrokeBuffer):
        self._buffer = buffer
        self._listener: keyboard.Listener | None = None
        self._modifiers_held: set = set()

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key) -> None:
        if key in _MODIFIER_KEYS:
            self._modifiers_held.add(key)
            return

        # Skip any key pressed while a modifier (Ctrl/Alt) is held.
        # This prevents Ctrl+C from get_selection() and the hotkey itself
        # from polluting the buffer.
        if self._modifiers_held:
            return

        try:
            char = key.char
            if char and ord(char) >= 32:
                self._buffer.add(char)
        except AttributeError:
            if key == keyboard.Key.backspace:
                self._buffer.pop(1)
            elif key == keyboard.Key.space:
                self._buffer.add(' ')
            elif key in (keyboard.Key.enter, keyboard.Key.esc, keyboard.Key.tab):
                self._buffer.clear()

    def _on_release(self, key) -> None:
        self._modifiers_held.discard(key)
