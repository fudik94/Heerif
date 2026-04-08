"""Tests for HotkeyManager using the keyboard library."""
from unittest.mock import patch, MagicMock
import pytest
from src.hotkey_manager import HotkeyManager


def test_start_registers_hotkey():
    with patch('src.hotkey_manager.keyboard.add_hotkey') as mock_add:
        mock_add.return_value = MagicMock()
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.start()
        mock_add.assert_called_once_with('ctrl+space', mgr._callback)


def test_start_is_noop_if_already_running():
    with patch('src.hotkey_manager.keyboard.add_hotkey') as mock_add:
        mock_add.return_value = MagicMock()
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.start()
        mgr.start()
        assert mock_add.call_count == 1


def test_stop_removes_hotkey():
    with patch('src.hotkey_manager.keyboard.add_hotkey') as mock_add, \
         patch('src.hotkey_manager.keyboard.remove_hotkey') as mock_remove:
        handle = MagicMock()
        mock_add.return_value = handle
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.start()
        mgr.stop()
        mock_remove.assert_called_once_with(handle)
        assert mgr._hotkey_ref is None


def test_stop_is_noop_if_not_running():
    with patch('src.hotkey_manager.keyboard.remove_hotkey') as mock_remove:
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.stop()
        mock_remove.assert_not_called()


def test_update_hotkey_replaces_string():
    with patch('src.hotkey_manager.keyboard.add_hotkey') as mock_add, \
         patch('src.hotkey_manager.keyboard.remove_hotkey'):
        mock_add.return_value = MagicMock()
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.start()
        mgr.update_hotkey('ctrl+f8')
        assert mgr._hotkey_str == 'ctrl+f8'


def test_invalid_hotkey_raises_value_error():
    with patch('src.hotkey_manager.keyboard.add_hotkey') as mock_add:
        mock_add.side_effect = ValueError("unknown key")
        mgr = HotkeyManager('ctrl+invalid_key', lambda: None)
        with pytest.raises(ValueError, match="Invalid hotkey"):
            mgr.start()
