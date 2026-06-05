"""Clipboard save/restore and selection detection via SendInput."""
import ctypes
import ctypes.wintypes
import time
import pyperclip

user32 = ctypes.windll.user32

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_HOME = 0x24
VK_C = 0x43
VK_V = 0x56


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', ctypes.wintypes.WORD),
        ('wScan', ctypes.wintypes.WORD),
        ('dwFlags', ctypes.wintypes.DWORD),
        ('time', ctypes.wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ('ki', KEYBDINPUT),
        ('padding', ctypes.c_byte * 32),  # MOUSEINPUT is 32 bytes — largest union member
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.wintypes.DWORD),
        ('_input', _INPUT_UNION),
    ]


def _send_ctrl(vk: int) -> None:
    """Inject Ctrl+[vk] via SendInput — works in all apps including modern WinUI."""
    inputs = (INPUT * 4)(
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_CONTROL))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=vk))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=vk, dwFlags=KEYEVENTF_KEYUP))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_CONTROL, dwFlags=KEYEVENTF_KEYUP))),
    )
    user32.SendInput(4, ctypes.byref(inputs), ctypes.sizeof(INPUT))


def _send_shift_home() -> None:
    """Inject Shift+Home to select from cursor to start of line."""
    inputs = (INPUT * 4)(
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_SHIFT))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_HOME, dwFlags=KEYEVENTF_EXTENDEDKEY))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_HOME, dwFlags=KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP))),
        INPUT(type=INPUT_KEYBOARD, _input=_INPUT_UNION(ki=KEYBDINPUT(wVk=VK_SHIFT, dwFlags=KEYEVENTF_KEYUP))),
    )
    user32.SendInput(4, ctypes.byref(inputs), ctypes.sizeof(INPUT))


class ClipboardManager:
    def __init__(self) -> None:
        self._saved: str = ''
        self._hwnd: int = 0

    def set_target_window(self, hwnd: int) -> None:
        self._hwnd = hwnd

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
        """Inject Ctrl+C and return selected text, or None if nothing was selected."""
        before = self.get()
        _send_ctrl(VK_C)
        time.sleep(0.15)
        after = self.get()
        if after and after != before:
            return after
        return None

    def select_to_line_start(self) -> None:
        """Inject Shift+Home to select from cursor to beginning of line."""
        _send_shift_home()

    def paste(self) -> None:
        """Inject Ctrl+V to paste current clipboard into the focused window."""
        _send_ctrl(VK_V)
