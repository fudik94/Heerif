"""Conversion pipeline — orchestrates text detection, conversion, and paste-back."""
import time
from src.config import Config
from src.clipboard_manager import ClipboardManager
from src.converter import auto_convert


class ConversionPipeline:
    def __init__(
        self,
        config: Config,
        clipboard: ClipboardManager,
        maps: dict[str, dict[str, str]],
    ) -> None:
        self._config = config
        self._clipboard = clipboard
        self._maps = maps

    def run(self) -> None:
        time.sleep(0.1)
        self._clipboard.save()
        text: str | None = None

        if self._config.selection_mode:
            text = self._clipboard.get_selection()

        if text is None and self._config.buffer_mode:
            self._clipboard.select_to_line_start()
            time.sleep(0.1)
            text = self._clipboard.get_selection()

        if not text:
            self._clipboard.restore()
            return

        converted = auto_convert(text, self._maps['en_ru'], self._maps['ru_en'])
        self._clipboard.set(converted)
        self._clipboard.paste()
        time.sleep(0.05)
        self._clipboard.restore()
