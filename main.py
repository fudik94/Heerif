import ctypes
import threading
from src.config import load_config, save_config
from src.layout_maps import get_maps
from src.clipboard_manager import ClipboardManager
from src.hotkey_manager import HotkeyManager
from src.pipeline import ConversionPipeline
from src.tray_app import TrayApp


def main() -> None:
    config = load_config()
    maps = get_maps(config.language_pair)
    clipboard = ClipboardManager()
    pipeline = ConversionPipeline(config=config, clipboard=clipboard, maps=maps)

    def on_hotkey() -> None:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        clipboard.set_target_window(hwnd)
        threading.Thread(target=pipeline.run, daemon=True).start()

    hotkey_mgr = HotkeyManager(config.hotkey, on_hotkey)

    def on_settings_saved(updated_config) -> None:
        nonlocal maps
        maps = get_maps(updated_config.language_pair)
        pipeline._maps = maps
        pipeline._config = updated_config
        hotkey_mgr.update_hotkey(updated_config.hotkey)
        save_config(updated_config)

    hotkey_mgr.start()
    tray = TrayApp(config, on_settings_saved)
    tray.run()
    hotkey_mgr.stop()


if __name__ == '__main__':
    main()
