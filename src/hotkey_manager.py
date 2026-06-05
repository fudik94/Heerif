"""System-wide hotkey via Windows RegisterHotKey — OS suppresses the key, no event-hook interference."""
import ctypes
import ctypes.wintypes
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

_VK: dict[str, int] = {
    **{f'f{n}': 0x6F + n for n in range(1, 13)},  # F1-F12
    **{chr(c).lower(): c for c in range(0x41, 0x5B)},  # a-z
    **{str(n): 0x30 + n for n in range(10)},
    'space': 0x20, 'tab': 0x09, 'enter': 0x0D, 'esc': 0x1B,
}

_MOD: dict[str, int] = {
    'ctrl': MOD_CONTROL, 'shift': MOD_SHIFT, 'alt': MOD_ALT, 'win': MOD_WIN,
}

_next_id = 1


def _parse(hotkey_str: str) -> tuple[int, int]:
    mods, vk = 0, 0
    for part in hotkey_str.lower().split('+'):
        part = part.strip()
        if part in _MOD:
            mods |= _MOD[part]
        elif part in _VK:
            vk = _VK[part]
        else:
            raise ValueError(f'Unknown key {part!r} in hotkey {hotkey_str!r}')
    if not vk:
        raise ValueError(f'No non-modifier key in hotkey {hotkey_str!r}')
    return mods, vk


class HotkeyManager:
    def __init__(self, hotkey_str: str, callback) -> None:
        global _next_id
        self._hotkey_str = hotkey_str
        self._callback = callback
        self._thread: threading.Thread | None = None
        self._thread_id: int = 0
        self._hk_id = _next_id
        _next_id += 1

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        mods, vk = _parse(self._hotkey_str)
        self._thread = threading.Thread(target=self._run, args=(mods, vk), daemon=True)
        self._thread.start()

    def _run(self, mods: int, vk: int) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        if not user32.RegisterHotKey(None, self._hk_id, mods, vk):
            raise RuntimeError(f'RegisterHotKey failed — hotkey {self._hotkey_str!r} may already be in use')
        msg = ctypes.wintypes.MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam == self._hk_id:
                    self._callback()
        finally:
            user32.UnregisterHotKey(None, self._hk_id)
            self._thread_id = 0

    def stop(self) -> None:
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(timeout=2.0)
        self._thread = None

    def update_hotkey(self, new_str: str) -> None:
        global _next_id
        self.stop()
        self._hotkey_str = new_str
        self._hk_id = _next_id
        _next_id += 1
        self.start()
