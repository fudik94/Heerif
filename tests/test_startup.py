from unittest.mock import MagicMock
import sys
from src.startup import set_startup, APP_NAME

def test_set_startup_enabled(mocker):
    mock_key = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_key
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_ctx)
    mock_set = mocker.patch('src.startup.winreg.SetValueEx')
    set_startup(True)
    mock_set.assert_called_once()
    args = mock_set.call_args[0]
    assert args[1] == APP_NAME
    assert sys.executable in args[4]

def test_set_startup_disabled(mocker):
    mock_key = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_key
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_ctx)
    mock_del = mocker.patch('src.startup.winreg.DeleteValue')
    set_startup(False)
    mock_del.assert_called_once_with(mock_key, APP_NAME)

def test_set_startup_disabled_ignores_missing_key(mocker):
    mock_key = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_key
    mocker.patch('src.startup.winreg.OpenKey', return_value=mock_ctx)
    mocker.patch('src.startup.winreg.DeleteValue', side_effect=FileNotFoundError)
    # Should not raise
    set_startup(False)
