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

    buffer = KeystrokeBuffer(max_size=int(config.buffer_size))
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
    tray.run()  # blocks until user clicks Quit

    kb_hook.stop()
    hotkey_mgr.stop()


if __name__ == '__main__':
    main()
