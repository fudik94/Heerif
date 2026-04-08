"""Conversion pipeline — orchestrates text detection, conversion, and paste-back."""
import time
from pynput import keyboard as kb
from src.config import Config
from src.keyboard_hook import KeystrokeBuffer
from src.clipboard_manager import ClipboardManager
from src.converter import auto_convert


def paste_text(clipboard: ClipboardManager, text: str) -> None:
    """Set clipboard to text, simulate Ctrl+V, then restore clipboard.

    Caller is responsible for saving clipboard state before calling this.
    """
    clipboard.set(text)
    ctrl = kb.Controller()
    ctrl.press(kb.Key.ctrl)
    ctrl.press('v')
    ctrl.release('v')
    ctrl.release(kb.Key.ctrl)
    time.sleep(0.05)  # give the target app time to receive the paste before we restore clipboard
    clipboard.restore()


def type_replacing(original: str, replacement: str) -> None:
    """Delete original text with Backspace, then type replacement."""
    ctrl = kb.Controller()
    for _ in range(len(original)):
        ctrl.press(kb.Key.backspace)
        ctrl.release(kb.Key.backspace)
    ctrl.type(replacement)


class ConversionPipeline:
    def __init__(
        self,
        config: Config,
        buffer: KeystrokeBuffer,
        clipboard: ClipboardManager,
        maps: dict[str, dict[str, str]],
    ) -> None:
        self._config = config
        self._buffer = buffer
        self._clipboard = clipboard
        self._maps = maps

    def run(self) -> None:
        """Detect text source, convert layout, and paste result back."""
        text: str | None = None
        source: str | None = None

        # Save clipboard before get_selection() which overwrites it via Ctrl+C.
        self._clipboard.save()

        if self._config.selection_mode:
            selected = self._clipboard.get_selection()
            if selected:
                text = selected
                source = 'selection'

        if text is None and self._config.buffer_mode:
            buffered = self._buffer.peek(self._config.buffer_size)
            if buffered:
                text = buffered
                source = 'buffer'

        if not text:
            return

        converted = auto_convert(text, self._maps['en_ru'], self._maps['ru_en'])

        if source == 'selection':
            paste_text(self._clipboard, converted)
        elif source == 'buffer':
            type_replacing(text, converted)
            self._buffer.clear()
