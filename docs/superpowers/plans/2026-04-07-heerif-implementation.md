# Heerif — Layout Switcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows background utility that converts text between keyboard layouts (EN↔RU) on hotkey press.

**Architecture:** Python app with a global keyboard hook that maintains a keystroke buffer. On `Ctrl+Space`, it checks for selected text (Ctrl+C) or falls back to the buffer, auto-detects the layout direction, converts using a character map, and pastes the result back. A pystray tray icon hosts a compact tkinter settings popup.

**Tech Stack:** Python 3.10+, pynput, pyperclip, pystray, Pillow, tkinter (stdlib), pytest

---

## File Structure

```
heerif/
  src/
    __init__.py
    layout_maps.py       # EN↔RU character mapping tables
    config.py            # Config dataclass + JSON load/save
    converter.py         # Layout detection + character conversion
    keyboard_hook.py     # Global keyboard listener + ring buffer
    clipboard_manager.py # Clipboard save/restore/get-selection
    hotkey_manager.py    # Hotkey listener (pynput HotKey)
    pipeline.py          # Orchestrates conversion on hotkey trigger
    startup.py           # Windows registry autostart
    tray_app.py          # System tray icon + settings popup
  main.py                # Entry point
  tests/
    __init__.py
    test_layout_maps.py
    test_converter.py
    test_config.py
    test_keyboard_hook.py
    test_clipboard_manager.py
    test_hotkey_manager.py
    test_pipeline.py
    test_startup.py
  requirements.txt
  .gitignore
```

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `.gitignore`

- [ ] **Step 1: Create requirements.txt**

```
pynput==1.7.6
pyperclip==1.8.2
pystray==0.19.5
Pillow==10.3.0
pytest==8.1.1
pytest-mock==3.14.0
```

- [ ] **Step 2: Create src/__init__.py and tests/__init__.py**

Both files are empty — just `touch` them:
```bash
# Windows Git Bash
touch src/__init__.py tests/__init__.py
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
dist/
build/
*.egg-info/
.heerif/
.superpowers/
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected output ends with: `Successfully installed ...`

- [ ] **Step 5: Verify pytest works**

```bash
pytest --collect-only
```

Expected: `no tests ran` (zero errors)

- [ ] **Step 6: Commit**

```bash
git add requirements.txt src/__init__.py tests/__init__.py .gitignore
git commit -m "chore: project setup"
```

---

## Task 2: layout_maps.py — Character Mapping Tables

**Files:**
- Create: `src/layout_maps.py`
- Create: `tests/test_layout_maps.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_layout_maps.py
from src.layout_maps import EN_RU, RU_EN, get_maps

def test_en_ru_sample():
    assert EN_RU['q'] == 'й'
    assert EN_RU['a'] == 'ф'
    assert EN_RU['g'] == 'п'
    assert EN_RU['h'] == 'р'
    assert EN_RU['b'] == 'и'

def test_uppercase_preserved():
    assert EN_RU['Q'] == 'Й'
    assert EN_RU['G'] == 'П'

def test_ru_en_is_reverse_of_en_ru():
    for en_char, ru_char in EN_RU.items():
        assert RU_EN[ru_char] == en_char

def test_get_maps_en_ru():
    maps = get_maps('en_ru')
    assert maps['en_ru'] is EN_RU
    assert maps['ru_en'] is RU_EN

def test_known_word_welcome():
    # 'цудсщьу' typed on RU layout when intending 'welcome'
    word = 'цудсщьу'
    result = ''.join(RU_EN.get(c, c) for c in word)
    assert result == 'welcome'

def test_known_word_privet():
    # 'ghbdtn' typed on EN layout when intending 'привет'
    word = 'ghbdtn'
    result = ''.join(EN_RU.get(c, c) for c in word)
    assert result == 'привет'
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_layout_maps.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.layout_maps'`

- [ ] **Step 3: Implement layout_maps.py**

```python
# src/layout_maps.py

EN_RU: dict[str, str] = {
    # Lowercase
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
    'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п',
    'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д',
    'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и',
    'n': 'т', 'm': 'ь',
    # Uppercase
    'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е',
    'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
    'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П',
    'H': 'Р', 'J': 'О', 'K': 'Л', 'L': 'Д',
    'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И',
    'N': 'Т', 'M': 'Ь',
    # Punctuation
    ';': 'ж', "'": 'э', '[': 'х', ']': 'ъ', ',': 'б', '.': 'ю',
    ':': 'Ж', '"': 'Э', '{': 'Х', '}': 'Ъ', '<': 'Б', '>': 'Ю',
    '`': 'ё', '~': 'Ё',
}

RU_EN: dict[str, str] = {v: k for k, v in EN_RU.items()}


def get_maps(language_pair: str) -> dict[str, dict[str, str]]:
    """Return forward and reverse maps for the given language pair."""
    if language_pair == 'en_ru':
        return {'en_ru': EN_RU, 'ru_en': RU_EN}
    # Default fallback — future pairs can be added here
    return {'en_ru': EN_RU, 'ru_en': RU_EN}
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_layout_maps.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add src/layout_maps.py tests/test_layout_maps.py
git commit -m "feat: add EN<->RU keyboard layout maps"
```

---

## Task 3: converter.py — Layout Detection and Conversion

**Files:**
- Create: `src/converter.py`
- Create: `tests/test_converter.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_converter.py
from src.converter import detect_layout, convert, auto_convert
from src.layout_maps import EN_RU, RU_EN

def test_detect_cyrillic():
    assert detect_layout('привет') == 'ru'

def test_detect_latin():
    assert detect_layout('hello') == 'en'

def test_detect_mixed_majority_cyrillic():
    assert detect_layout('приветhello') == 'ru'

def test_detect_empty_defaults_to_en():
    assert detect_layout('') == 'en'

def test_convert_with_map():
    result = convert('ghbdtn', EN_RU)
    assert result == 'привет'

def test_convert_unmapped_chars_preserved():
    result = convert('hello 123!', EN_RU)
    assert '1' in result
    assert '2' in result
    assert '3' in result
    assert '!' in result
    assert ' ' in result

def test_auto_convert_latin_to_cyrillic():
    # 'ghbdtn' typed on EN layout → should become 'привет'
    result = auto_convert('ghbdtn', EN_RU, RU_EN)
    assert result == 'привет'

def test_auto_convert_cyrillic_to_latin():
    # 'цудсщьу' typed on RU layout → should become 'welcome'
    result = auto_convert('цудсщьу', EN_RU, RU_EN)
    assert result == 'welcome'

def test_auto_convert_preserves_spaces():
    result = auto_convert('ghbdtn ьшк', EN_RU, RU_EN)
    assert result == 'привет mir'
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_converter.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.converter'`

- [ ] **Step 3: Implement converter.py**

```python
# src/converter.py


def detect_layout(text: str) -> str:
    """Return 'ru' if text is majority Cyrillic, 'en' otherwise."""
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in text if c.isalpha() and c.isascii())
    return 'ru' if cyrillic > latin else 'en'


def convert(text: str, layout_map: dict[str, str]) -> str:
    """Convert each character using layout_map; unmapped characters pass through."""
    return ''.join(layout_map.get(c, c) for c in text)


def auto_convert(
    text: str,
    en_ru: dict[str, str],
    ru_en: dict[str, str],
) -> str:
    """Auto-detect layout direction and convert to the other layout."""
    layout = detect_layout(text)
    if layout == 'ru':
        return convert(text, ru_en)
    return convert(text, en_ru)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_converter.py -v
```

Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add src/converter.py tests/test_converter.py
git commit -m "feat: add layout detection and conversion logic"
```

---

## Task 4: config.py — Settings Load/Save

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_config.py
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from src.config import Config, load_config, save_config

def test_default_config():
    cfg = Config()
    assert cfg.hotkey == 'ctrl+space'
    assert cfg.language_pair == 'en_ru'
    assert cfg.selection_mode is True
    assert cfg.buffer_mode is True
    assert cfg.buffer_size == 200
    assert cfg.launch_at_startup is False

def test_save_and_load_roundtrip(tmp_path):
    cfg = Config(hotkey='ctrl+alt+z', language_pair='en_ru', selection_mode=False)
    config_file = tmp_path / 'config.json'
    with patch('src.config.CONFIG_PATH', config_file):
        save_config(cfg)
        loaded = load_config()
    assert loaded.hotkey == 'ctrl+alt+z'
    assert loaded.selection_mode is False

def test_load_missing_file_returns_defaults(tmp_path):
    missing = tmp_path / 'nonexistent' / 'config.json'
    with patch('src.config.CONFIG_PATH', missing):
        cfg = load_config()
    assert cfg.hotkey == 'ctrl+space'

def test_save_creates_parent_dirs(tmp_path):
    config_file = tmp_path / 'nested' / 'dir' / 'config.json'
    with patch('src.config.CONFIG_PATH', config_file):
        save_config(Config())
    assert config_file.exists()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.config'`

- [ ] **Step 3: Implement config.py**

```python
# src/config.py
import json
from dataclasses import dataclass, asdict, fields
from pathlib import Path

CONFIG_PATH = Path.home() / '.heerif' / 'config.json'


@dataclass
class Config:
    hotkey: str = 'ctrl+space'
    language_pair: str = 'en_ru'
    selection_mode: bool = True
    buffer_mode: bool = True
    buffer_size: int = 200
    launch_at_startup: bool = False


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    data = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    valid_keys = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in valid_keys})


def save_config(config: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_config.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add config load/save with JSON persistence"
```

---

## Task 5: keyboard_hook.py — Keystroke Buffer

**Files:**
- Create: `src/keyboard_hook.py`
- Create: `tests/test_keyboard_hook.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_keyboard_hook.py
from unittest.mock import MagicMock, patch
from src.keyboard_hook import KeystrokeBuffer, KeyboardHook

# --- KeystrokeBuffer ---

def test_buffer_add_and_peek():
    buf = KeystrokeBuffer(max_size=10)
    buf.add('h')
    buf.add('i')
    assert buf.peek(2) == 'hi'

def test_buffer_peek_does_not_clear():
    buf = KeystrokeBuffer(max_size=10)
    buf.add('a')
    buf.peek(1)
    assert buf.peek(1) == 'a'

def test_buffer_pop_returns_and_clears():
    buf = KeystrokeBuffer(max_size=10)
    for c in 'hello':
        buf.add(c)
    result = buf.pop(3)
    assert result == 'llo'
    assert buf.peek(10) == 'he'

def test_buffer_respects_max_size():
    buf = KeystrokeBuffer(max_size=3)
    for c in 'abcde':
        buf.add(c)
    assert buf.peek(10) == 'cde'

def test_buffer_clear():
    buf = KeystrokeBuffer(max_size=10)
    buf.add('x')
    buf.clear()
    assert buf.peek(10) == ''

# --- KeyboardHook ---

def test_hook_adds_printable_chars_to_buffer():
    buf = KeystrokeBuffer()
    hook = KeyboardHook(buf)
    key = MagicMock()
    key.char = 'a'
    hook._on_press(key)
    assert buf.peek(1) == 'a'

def test_hook_ignores_none_char():
    buf = KeystrokeBuffer()
    hook = KeyboardHook(buf)
    key = MagicMock()
    key.char = None
    hook._on_press(key)
    assert buf.peek(10) == ''

def test_hook_backspace_removes_last_char():
    from pynput.keyboard import Key
    buf = KeystrokeBuffer()
    buf.add('a')
    buf.add('b')
    hook = KeyboardHook(buf)
    key = MagicMock(spec=[])
    key.__eq__ = lambda self, other: other == Key.backspace
    with patch('src.keyboard_hook.keyboard') as mock_kb:
        mock_kb.Key.backspace = Key.backspace
        hook._on_press(Key.backspace)
    assert buf.peek(10) == 'a'
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_keyboard_hook.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.keyboard_hook'`

- [ ] **Step 3: Implement keyboard_hook.py**

```python
# src/keyboard_hook.py
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_keyboard_hook.py -v
```

Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add src/keyboard_hook.py tests/test_keyboard_hook.py
git commit -m "feat: add keystroke ring buffer and keyboard hook"
```

---

## Task 6: clipboard_manager.py — Clipboard Operations

**Files:**
- Create: `src/clipboard_manager.py`
- Create: `tests/test_clipboard_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_clipboard_manager.py
from unittest.mock import patch, MagicMock
from src.clipboard_manager import ClipboardManager

def test_save_and_restore(mocker):
    mock_paste = mocker.patch('src.clipboard_manager.pyperclip.paste', return_value='original')
    mock_copy = mocker.patch('src.clipboard_manager.pyperclip.copy')
    mgr = ClipboardManager()
    mgr.save()
    mgr.restore()
    mock_copy.assert_called_once_with('original')

def test_get_returns_clipboard(mocker):
    mocker.patch('src.clipboard_manager.pyperclip.paste', return_value='hello')
    mgr = ClipboardManager()
    assert mgr.get() == 'hello'

def test_set_writes_to_clipboard(mocker):
    mock_copy = mocker.patch('src.clipboard_manager.pyperclip.copy')
    mgr = ClipboardManager()
    mgr.set('world')
    mock_copy.assert_called_once_with('world')

def test_get_selection_returns_none_when_unchanged(mocker):
    mocker.patch('src.clipboard_manager.pyperclip.paste', return_value='same')
    mock_ctrl = MagicMock()
    mocker.patch('src.clipboard_manager.keyboard.Controller', return_value=mock_ctrl)
    mocker.patch('src.clipboard_manager.time.sleep')
    mgr = ClipboardManager()
    result = mgr.get_selection()
    assert result is None

def test_get_selection_returns_text_when_changed(mocker):
    call_count = {'n': 0}
    def fake_paste():
        call_count['n'] += 1
        return 'before' if call_count['n'] == 1 else 'selected text'
    mocker.patch('src.clipboard_manager.pyperclip.paste', side_effect=fake_paste)
    mocker.patch('src.clipboard_manager.pyperclip.copy')
    mock_ctrl = MagicMock()
    mocker.patch('src.clipboard_manager.keyboard.Controller', return_value=mock_ctrl)
    mocker.patch('src.clipboard_manager.time.sleep')
    mgr = ClipboardManager()
    result = mgr.get_selection()
    assert result == 'selected text'
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_clipboard_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.clipboard_manager'`

- [ ] **Step 3: Implement clipboard_manager.py**

```python
# src/clipboard_manager.py
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
        if after and after != before:
            return after
        return None
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_clipboard_manager.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/clipboard_manager.py tests/test_clipboard_manager.py
git commit -m "feat: add clipboard manager with selection detection"
```

---

## Task 7: hotkey_manager.py — Global Hotkey Listener

**Files:**
- Create: `src/hotkey_manager.py`
- Create: `tests/test_hotkey_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_hotkey_manager.py
from src.hotkey_manager import HotkeyManager

def test_parse_ctrl_space():
    mgr = HotkeyManager('ctrl+space', lambda: None)
    assert mgr._format_hotkey('ctrl+space') == '<ctrl>+<space>'

def test_parse_ctrl_alt_z():
    mgr = HotkeyManager('ctrl+space', lambda: None)
    assert mgr._format_hotkey('ctrl+alt+z') == '<ctrl>+<alt>+z'

def test_parse_single_letter():
    mgr = HotkeyManager('ctrl+space', lambda: None)
    assert mgr._format_hotkey('ctrl+z') == '<ctrl>+z'

def test_update_hotkey_replaces_string():
    mgr = HotkeyManager('ctrl+space', lambda: None)
    mgr.update_hotkey('ctrl+alt+z')
    assert mgr._hotkey_str == 'ctrl+alt+z'
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_hotkey_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.hotkey_manager'`

- [ ] **Step 3: Implement hotkey_manager.py**

```python
# src/hotkey_manager.py
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
        parts = [p.strip().lower() for p in hotkey_str.split('+')]
        formatted = []
        for part in parts:
            if part in _MODIFIER_KEYS or len(part) > 1:
                formatted.append(f'<{part}>')
            else:
                formatted.append(part)
        return '+'.join(formatted)

    def start(self) -> None:
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
        if self._listener:
            self._listener.stop()
            self._listener = None

    def update_hotkey(self, new_hotkey_str: str) -> None:
        self.stop()
        self._hotkey_str = new_hotkey_str
        self.start()

    def _on_press(self, key) -> None:
        if self._hotkey_obj and self._listener:
            self._hotkey_obj.press(self._listener.canonical(key))

    def _on_release(self, key) -> None:
        if self._hotkey_obj and self._listener:
            self._hotkey_obj.release(self._listener.canonical(key))
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_hotkey_manager.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/hotkey_manager.py tests/test_hotkey_manager.py
git commit -m "feat: add global hotkey listener"
```

---

## Task 8: pipeline.py — Conversion Orchestration

**Files:**
- Create: `src/pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pipeline.py
from unittest.mock import MagicMock, patch
from src.pipeline import ConversionPipeline
from src.config import Config
from src.layout_maps import EN_RU, RU_EN

MAPS = {'en_ru': EN_RU, 'ru_en': RU_EN}

def _make_pipeline(config=None, clipboard_text=None, buffer_text=''):
    cfg = config or Config()
    buffer = MagicMock()
    buffer.peek.return_value = buffer_text
    clipboard = MagicMock()
    clipboard.get_selection.return_value = clipboard_text
    return ConversionPipeline(cfg, buffer, clipboard, MAPS), buffer, clipboard

def test_uses_selection_when_available():
    pipeline, buf, clip = _make_pipeline(clipboard_text='ghbdtn')
    with patch('src.pipeline.paste_text') as mock_paste:
        pipeline.run()
    mock_paste.assert_called_once_with(clip, 'привет')

def test_falls_back_to_buffer_when_no_selection():
    pipeline, buf, clip = _make_pipeline(clipboard_text=None, buffer_text='ghbdtn')
    with patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_type.assert_called_once_with('ghbdtn', 'привет')

def test_does_nothing_when_both_empty():
    pipeline, buf, clip = _make_pipeline(clipboard_text=None, buffer_text='')
    with patch('src.pipeline.paste_text') as mock_paste, \
         patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_paste.assert_not_called()
    mock_type.assert_not_called()

def test_selection_mode_disabled_skips_clipboard():
    cfg = Config(selection_mode=False, buffer_mode=True)
    pipeline, buf, clip = _make_pipeline(config=cfg, clipboard_text='ghbdtn', buffer_text='ghbdtn')
    with patch('src.pipeline.type_replacing'):
        pipeline.run()
    clip.get_selection.assert_not_called()

def test_buffer_mode_disabled_skips_buffer():
    cfg = Config(selection_mode=True, buffer_mode=False)
    pipeline, buf, clip = _make_pipeline(config=cfg, clipboard_text=None, buffer_text='ghbdtn')
    with patch('src.pipeline.paste_text') as mock_paste, \
         patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_type.assert_not_called()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_pipeline.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.pipeline'`

- [ ] **Step 3: Implement pipeline.py**

```python
# src/pipeline.py
import time
from pynput import keyboard as kb
from src.config import Config
from src.keyboard_hook import KeystrokeBuffer
from src.clipboard_manager import ClipboardManager
from src.converter import auto_convert


def paste_text(clipboard: ClipboardManager, text: str) -> None:
    """Set clipboard to text and simulate Ctrl+V, then restore clipboard."""
    clipboard.save()
    clipboard.set(text)
    ctrl = kb.Controller()
    ctrl.press(kb.Key.ctrl)
    ctrl.press('v')
    ctrl.release('v')
    ctrl.release(kb.Key.ctrl)
    time.sleep(0.05)
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
        maps: dict,
    ) -> None:
        self._config = config
        self._buffer = buffer
        self._clipboard = clipboard
        self._maps = maps

    def run(self) -> None:
        text: str | None = None
        source: str | None = None

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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_pipeline.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/pipeline.py tests/test_pipeline.py
git commit -m "feat: add conversion pipeline orchestration"
```

---

## Task 9: startup.py — Windows Autostart via Registry

**Files:**
- Create: `src/startup.py`
- Create: `tests/test_startup.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_startup.py
from unittest.mock import patch, MagicMock, call
import sys
from src.startup import set_startup, APP_NAME

def test_set_startup_enabled(mocker):
    mock_key = MagicMock()
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_key)
    mock_set = mocker.patch('src.startup.winreg.SetValueEx')
    mocker.patch('src.startup.winreg.CloseKey')
    set_startup(True)
    mock_set.assert_called_once()
    args = mock_set.call_args[0]
    assert args[1] == APP_NAME
    assert sys.executable in args[4]

def test_set_startup_disabled(mocker):
    mock_key = MagicMock()
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_key)
    mock_del = mocker.patch('src.startup.winreg.DeleteValue')
    mocker.patch('src.startup.winreg.CloseKey')
    set_startup(False)
    mock_del.assert_called_once_with(mock_key, APP_NAME)

def test_set_startup_disabled_ignores_missing_key(mocker):
    mock_key = MagicMock()
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_key)
    mocker.patch('src.startup.winreg.DeleteValue', side_effect=FileNotFoundError)
    mocker.patch('src.startup.winreg.CloseKey')
    # Should not raise
    set_startup(False)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_startup.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.startup'`

- [ ] **Step 3: Implement startup.py**

```python
# src/startup.py
import sys
import winreg

APP_NAME = 'Heerif'
_STARTUP_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def set_startup(enabled: bool) -> None:
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        _STARTUP_KEY,
        0,
        winreg.KEY_SET_VALUE,
    )
    if enabled:
        value = f'"{sys.executable}" "{sys.argv[0]}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_startup.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/startup.py tests/test_startup.py
git commit -m "feat: add Windows registry autostart"
```

---

## Task 10: tray_app.py — System Tray + Settings Popup

**Files:**
- Create: `src/tray_app.py`

> Note: tkinter UI is not unit-tested. Verify manually by running the app.

- [ ] **Step 1: Implement tray_app.py**

```python
# src/tray_app.py
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

import pystray
from PIL import Image, ImageDraw

from src.config import Config, save_config
from src.startup import set_startup


def _create_icon_image() -> Image.Image:
    img = Image.new('RGB', (64, 64), color='#1e1e2e')
    draw = ImageDraw.Draw(img)
    draw.text((14, 14), 'H', fill='#cdd6f4')
    return img


class SettingsPopup:
    def __init__(
        self,
        config: Config,
        on_save: Callable[[Config], None],
    ) -> None:
        self._config = config
        self._on_save = on_save

    def show(self) -> None:
        root = tk.Tk()
        root.title('Heerif — Настройки')
        root.resizable(False, False)
        root.attributes('-topmost', True)

        pad = {'padx': 10, 'pady': 4}

        tk.Label(root, text='Горячая клавиша:').grid(row=0, column=0, sticky='w', **pad)
        hotkey_var = tk.StringVar(value=self._config.hotkey)
        tk.Entry(root, textvariable=hotkey_var, width=18).grid(row=0, column=1, **pad)

        tk.Label(root, text='Языки:').grid(row=1, column=0, sticky='w', **pad)
        pair_var = tk.StringVar(value=self._config.language_pair)
        ttk.Combobox(
            root, textvariable=pair_var, values=['en_ru'], width=16, state='readonly'
        ).grid(row=1, column=1, **pad)

        sel_var = tk.BooleanVar(value=self._config.selection_mode)
        tk.Checkbutton(root, text='Режим выделения', variable=sel_var).grid(
            row=2, columnspan=2, sticky='w', **pad
        )

        buf_var = tk.BooleanVar(value=self._config.buffer_mode)
        tk.Checkbutton(root, text='Режим буфера', variable=buf_var).grid(
            row=3, columnspan=2, sticky='w', **pad
        )

        start_var = tk.BooleanVar(value=self._config.launch_at_startup)
        tk.Checkbutton(root, text='Автозапуск', variable=start_var).grid(
            row=4, columnspan=2, sticky='w', **pad
        )

        def _save() -> None:
            self._config.hotkey = hotkey_var.get().strip()
            self._config.language_pair = pair_var.get()
            self._config.selection_mode = sel_var.get()
            self._config.buffer_mode = buf_var.get()
            self._config.launch_at_startup = start_var.get()
            set_startup(self._config.launch_at_startup)
            self._on_save(self._config)
            root.destroy()

        tk.Button(root, text='Сохранить', command=_save).grid(
            row=5, columnspan=2, pady=8
        )
        root.mainloop()


class TrayApp:
    def __init__(
        self,
        config: Config,
        on_settings_saved: Callable[[Config], None],
    ) -> None:
        self._config = config
        self._on_settings_saved = on_settings_saved
        self._popup_open = False

    def _show_settings(self, icon: pystray.Icon, item) -> None:
        if self._popup_open:
            return
        self._popup_open = True
        try:
            popup = SettingsPopup(self._config, self._on_settings_saved)
            popup.show()
        finally:
            self._popup_open = False

    def _quit(self, icon: pystray.Icon, item) -> None:
        icon.stop()

    def run(self) -> None:
        icon = pystray.Icon(
            'heerif',
            _create_icon_image(),
            'Heerif',
            menu=pystray.Menu(
                pystray.MenuItem('Настройки', self._show_settings),
                pystray.MenuItem('Выход', self._quit),
            ),
        )
        icon.run()
```

- [ ] **Step 2: Commit**

```bash
git add src/tray_app.py
git commit -m "feat: add system tray icon and settings popup"
```

---

## Task 11: main.py — Entry Point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Implement main.py**

```python
# main.py
from src.config import load_config, save_config
from src.layout_maps import get_maps
from src.keyboard_hook import KeystrokeBuffer, KeyboardHook
from src.clipboard_manager import ClipboardManager
from src.hotkey_manager import HotkeyManager
from src.pipeline import ConversionPipeline
from src.tray_app import TrayApp


def main() -> None:
    config = load_config()
    maps = get_maps(config.language_pair)

    buffer = KeystrokeBuffer(max_size=config.buffer_size)
    clipboard = ClipboardManager()

    pipeline = ConversionPipeline(
        config=config,
        buffer=buffer,
        clipboard=clipboard,
        maps=maps,
    )

    hotkey_mgr = HotkeyManager(config.hotkey, pipeline.run)
    kb_hook = KeyboardHook(buffer)

    def on_settings_saved(updated_config) -> None:
        nonlocal maps
        maps = get_maps(updated_config.language_pair)
        pipeline._maps = maps
        pipeline._config = updated_config
        hotkey_mgr.update_hotkey(updated_config.hotkey)
        save_config(updated_config)

    kb_hook.start()
    hotkey_mgr.start()

    tray = TrayApp(config, on_settings_saved)
    tray.run()  # blocks until user quits

    kb_hook.stop()
    hotkey_mgr.stop()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the full test suite**

```bash
pytest -v
```

Expected: all tests pass (no failures)

- [ ] **Step 3: Smoke test — run the app**

```bash
python main.py
```

Expected: Heerif icon appears in system tray. Right-click shows "Настройки" and "Выход".
Test: Open Notepad, type "ghbdtn", press `Ctrl+Space` → text changes to "привет".

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point — Heerif is runnable"
```

---

## Task 12: Final Cleanup

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add .heerif config dir to .gitignore (already done in Task 1 — verify)**

```bash
grep '.heerif' .gitignore
```

Expected output: `.heerif/`

- [ ] **Step 2: Run full test suite one last time**

```bash
pytest -v --tb=short
```

Expected: all tests pass

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup and verification"
```
