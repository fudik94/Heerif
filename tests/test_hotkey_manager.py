"""Tests for HotkeyManager using Windows RegisterHotKey API."""
import ctypes
import ctypes.wintypes
import threading
import pytest
from unittest.mock import patch, MagicMock, call
from src.hotkey_manager import HotkeyManager, _parse


# --- _parse unit tests ---

def test_parse_ctrl_f12():
    mods, vk = _parse('ctrl+f12')
    assert mods == 0x0002  # MOD_CONTROL
    assert vk == 0x7B      # VK_F12


def test_parse_ctrl_shift_f9():
    mods, vk = _parse('ctrl+shift+f9')
    assert mods == 0x0002 | 0x0004  # MOD_CONTROL | MOD_SHIFT
    assert vk == 0x78      # VK_F9


def test_parse_unknown_key_raises():
    with pytest.raises(ValueError, match='Unknown key'):
        _parse('ctrl+invalid_key')


def test_parse_no_main_key_raises():
    with pytest.raises(ValueError, match='No non-modifier key'):
        _parse('ctrl+shift')


# --- HotkeyManager behaviour tests ---

def _make_msg(message: int, wparam: int = 0) -> ctypes.wintypes.MSG:
    msg = ctypes.wintypes.MSG()
    msg.message = message
    msg.wParam = wparam
    return msg


def test_start_registers_hotkey():
    called = []

    def fake_get_message(msg_ptr, hwnd, min_, max_):
        # Deliver one WM_HOTKEY then quit
        msg = ctypes.cast(msg_ptr, ctypes.POINTER(ctypes.wintypes.MSG)).contents
        if not called:
            msg.message = 0x0312  # WM_HOTKEY
            called.append(True)
            return 1
        msg.message = 0  # causes loop exit via WM_QUIT path
        return 0  # stop the loop

    with patch('src.hotkey_manager.user32.RegisterHotKey', return_value=1) as mock_reg, \
         patch('src.hotkey_manager.user32.UnregisterHotKey') as mock_unreg, \
         patch('src.hotkey_manager.user32.GetMessageW', side_effect=fake_get_message), \
         patch('src.hotkey_manager.kernel32.GetCurrentThreadId', return_value=42):
        cb = MagicMock()
        mgr = HotkeyManager('ctrl+f12', cb)
        mgr.start()
        mgr._thread.join(timeout=2.0)
        mock_reg.assert_called_once()
        mock_unreg.assert_called_once()


def test_start_is_noop_if_already_running():
    import threading, time

    barrier = threading.Event()

    def blocking_get_message(msg_ptr, hwnd, min_, max_):
        barrier.wait(timeout=2.0)
        return 0  # exit loop once released

    with patch('src.hotkey_manager.user32.RegisterHotKey', return_value=1) as mock_reg, \
         patch('src.hotkey_manager.user32.UnregisterHotKey'), \
         patch('src.hotkey_manager.user32.GetMessageW', side_effect=blocking_get_message), \
         patch('src.hotkey_manager.kernel32.GetCurrentThreadId', return_value=42):
        mgr = HotkeyManager('ctrl+f12', lambda: None)
        mgr.start()
        time.sleep(0.05)  # let the thread enter the message loop
        t = mgr._thread
        mgr.start()  # should be noop
        assert mgr._thread is t
        assert mock_reg.call_count == 1
        barrier.set()
        t.join(timeout=1.0)


def test_stop_is_noop_if_not_running():
    mgr = HotkeyManager('ctrl+f12', lambda: None)
    mgr.stop()  # should not raise


def test_update_hotkey_replaces_string():
    with patch('src.hotkey_manager.user32.RegisterHotKey', return_value=1), \
         patch('src.hotkey_manager.user32.UnregisterHotKey'), \
         patch('src.hotkey_manager.user32.GetMessageW', return_value=0), \
         patch('src.hotkey_manager.user32.PostThreadMessageW'), \
         patch('src.hotkey_manager.kernel32.GetCurrentThreadId', return_value=42):
        mgr = HotkeyManager('ctrl+f12', lambda: None)
        mgr.start()
        mgr.update_hotkey('ctrl+f9')
        assert mgr._hotkey_str == 'ctrl+f9'


def test_invalid_hotkey_raises_value_error():
    mgr = HotkeyManager('ctrl+invalid_key', lambda: None)
    with pytest.raises(ValueError, match='Unknown key'):
        mgr.start()
