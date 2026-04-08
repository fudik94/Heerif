from unittest.mock import patch, MagicMock
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
    with patch('src.hotkey_manager.keyboard.Listener') as mock_listener_cls, \
         patch('src.hotkey_manager.keyboard.HotKey'):
        mock_listener_cls.return_value = MagicMock()
        mgr = HotkeyManager('ctrl+space', lambda: None)
        mgr.update_hotkey('ctrl+alt+z')
        assert mgr._hotkey_str == 'ctrl+alt+z'
