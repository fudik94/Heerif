from unittest.mock import patch, MagicMock
from src.clipboard_manager import ClipboardManager


def test_save_and_restore(mocker):
    mocker.patch('src.clipboard_manager.pyperclip.paste', return_value='original')
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


def test_get_selection_returns_none_when_clipboard_unchanged(mocker):
    mocker.patch('src.clipboard_manager.pyperclip.paste', return_value='same')
    mocker.patch('src.clipboard_manager._send_ctrl')
    mocker.patch('src.clipboard_manager.time.sleep')
    mgr = ClipboardManager()
    result = mgr.get_selection()
    assert result is None


def test_get_selection_returns_text_when_ctrl_c_copies(mocker):
    call_count = {'n': 0}

    def fake_paste():
        call_count['n'] += 1
        return 'old' if call_count['n'] == 1 else 'selected text'

    mocker.patch('src.clipboard_manager.pyperclip.paste', side_effect=fake_paste)
    mocker.patch('src.clipboard_manager._send_ctrl')
    mocker.patch('src.clipboard_manager.time.sleep')
    mgr = ClipboardManager()
    result = mgr.get_selection()
    assert result == 'selected text'
