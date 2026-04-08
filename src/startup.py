"""Windows registry autostart management for Heerif."""
import sys
import winreg

APP_NAME = 'Heerif'
_STARTUP_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def set_startup(enabled: bool) -> None:
    """Add or remove Heerif from Windows startup registry."""
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
