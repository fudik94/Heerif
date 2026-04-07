from collections import deque
from pynput import keyboard


class KeystrokeBuffer:
    def __init__(self, max_size: int = 200):
        self._buffer: deque[str] = deque(maxlen=max_size)

    def add(self, char: str) -> None:
        self._buffer.append(char)

    def peek(self, n: int) -> str:
        return ''.join(list(self._buffer)[-n:]) if n > 0 else ''

    def pop(self, n: int) -> str:
        n = min(n, len(self._buffer))
        chars = list(self._buffer)[-n:]
        for _ in range(n):
            self._buffer.pop()
        return ''.join(chars)

    def clear(self) -> None:
        self._buffer.clear()


class KeyboardHook:
    def __init__(self, buffer: KeystrokeBuffer):
        self._buffer = buffer
        self._listener: keyboard.Listener | None = None

    def start(self) -> None:
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()

    def _on_press(self, key) -> None:
        try:
            char = key.char
            if char:
                self._buffer.add(char)
        except AttributeError:
            if key == keyboard.Key.backspace:
                self._buffer.pop(1)
            elif key in (keyboard.Key.enter, keyboard.Key.esc, keyboard.Key.tab):
                self._buffer.clear()
