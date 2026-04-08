"""System tray icon and settings popup for Heerif."""
import tkinter as tk
from tkinter import ttk
from typing import Callable

import pystray
from PIL import Image, ImageDraw

from src.config import Config, save_config
from src.startup import set_startup


def _create_icon_image() -> Image.Image:
    img = Image.new('RGB', (64, 64), color='#1e1e2e')
    draw = ImageDraw.Draw(img)
    draw.text((14, 14), 'H', fill='#cdd6f4')
    return img


class SettingsPopup:
    def __init__(
        self,
        config: Config,
        on_save: Callable[[Config], None],
    ) -> None:
        self._config = config
        self._on_save = on_save

    def show(self) -> None:
        root = tk.Tk()
        root.title('Heerif — Настройки')
        root.resizable(False, False)
        root.attributes('-topmost', True)

        pad = {'padx': 10, 'pady': 4}

        tk.Label(root, text='Горячая клавиша:').grid(row=0, column=0, sticky='w', **pad)
        hotkey_var = tk.StringVar(value=self._config.hotkey)
        tk.Entry(root, textvariable=hotkey_var, width=18).grid(row=0, column=1, **pad)

        tk.Label(root, text='Языки:').grid(row=1, column=0, sticky='w', **pad)
        pair_var = tk.StringVar(value=self._config.language_pair)
        ttk.Combobox(
            root, textvariable=pair_var, values=['en_ru'], width=16, state='readonly'
        ).grid(row=1, column=1, **pad)

        sel_var = tk.BooleanVar(value=self._config.selection_mode)
        tk.Checkbutton(root, text='Режим выделения', variable=sel_var).grid(
            row=2, columnspan=2, sticky='w', **pad
        )

        buf_var = tk.BooleanVar(value=self._config.buffer_mode)
        tk.Checkbutton(root, text='Режим буфера', variable=buf_var).grid(
            row=3, columnspan=2, sticky='w', **pad
        )

        start_var = tk.BooleanVar(value=self._config.launch_at_startup)
        tk.Checkbutton(root, text='Автозапуск', variable=start_var).grid(
            row=4, columnspan=2, sticky='w', **pad
        )

        def _save() -> None:
            self._config.hotkey = hotkey_var.get().strip()
            self._config.language_pair = pair_var.get()
            self._config.selection_mode = sel_var.get()
            self._config.buffer_mode = buf_var.get()
            self._config.launch_at_startup = start_var.get()
            set_startup(self._config.launch_at_startup)
            self._on_save(self._config)
            root.destroy()

        tk.Button(root, text='Сохранить', command=_save).grid(
            row=5, columnspan=2, pady=8
        )
        root.mainloop()


class TrayApp:
    def __init__(
        self,
        config: Config,
        on_settings_saved: Callable[[Config], None],
    ) -> None:
        self._config = config
        self._on_settings_saved = on_settings_saved
        self._popup_open = False

    def _show_settings(self, icon: pystray.Icon, item) -> None:
        if self._popup_open:
            return
        self._popup_open = True
        try:
            popup = SettingsPopup(self._config, self._on_settings_saved)
            popup.show()
        finally:
            self._popup_open = False

    def _quit(self, icon: pystray.Icon, item) -> None:
        icon.stop()

    def run(self) -> None:
        """Start the system tray icon. Blocks until user clicks Quit."""
        icon = pystray.Icon(
            'heerif',
            _create_icon_image(),
            'Heerif',
            menu=pystray.Menu(
                pystray.MenuItem('Настройки', self._show_settings),
                pystray.MenuItem('Выход', self._quit),
            ),
        )
        icon.run()
