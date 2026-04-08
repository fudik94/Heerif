"""Windows registry autostart management for Heerif."""
import sys
from pathlib import Path
import winreg

APP_NAME = 'Heerif'
_STARTUP_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def set_startup(enabled: bool) -> None:
    """Add or remove Heerif from Windows startup registry."""
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        _STARTUP_KEY,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            value = f'"{sys.executable}" "{Path(sys.argv[0]).resolve()}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
