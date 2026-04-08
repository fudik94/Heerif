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
    # Pass Key.backspace directly - it will be caught in AttributeError and compared
    hook._on_press(Key.backspace)
    assert buf.peek(10) == 'a'
