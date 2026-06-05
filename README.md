# ⌨️Heerif - Layout Switcher

> Typed in the wrong keyboard layout? Fix it instantly.

[![Download](https://img.shields.io/badge/Download-Heerif.exe-blue?style=for-the-badge)](https://github.com/fudik94/Heerif/releases/download/v0.2.0/Heerif.exe)

Heerif was born out of a daily frustration - switching between EN and RU layouts constantly and realizing only after typing a whole sentence that the layout was wrong. Instead of accepting it as a fact of life, this app fixes it with a single keystroke.

**Heerif** sits in the system tray. Press `Ctrl+F12` — and your mistyped text converts between English and Russian layouts on the spot.

```
ghbdtn  →  привет
цудсщьу  →  welcome
```

---

## How It Works

| Scenario | What Heerif does |
|---|---|
| You have text **selected** | Converts the selection |
| Nothing selected | Auto-selects current line and converts |

Direction is detected automatically — no need to specify EN→RU or RU→EN.

---

## Features

- Global hotkey (`Ctrl+F12` by default)
- Auto-detects conversion direction
- Selection mode + keystroke buffer mode
- System tray icon with settings popup
- Optional Windows autostart
- Configurable via `~/.heerif/config.json`

---

## Settings

Right-click the tray icon → **Настройки**

| Setting | Default | Description |
|---|---|---|
| Hotkey | `Ctrl+F12` | Key combination to trigger conversion |
| Language pair | `en_ru` | EN ↔ RU (more pairs planned) |
| Selection mode | on | Convert selected text via Ctrl+C |
| Buffer mode | on | Convert last typed text |
| Autostart | off | Launch with Windows |

---

## Project Structure

```
src/
  layout_maps.py      # EN↔RU character mapping tables
  converter.py        # Layout detection and conversion logic
  keyboard_hook.py    # Keystroke buffer
  hotkey_manager.py   # Global hotkey listener (Windows RegisterHotKey)
  clipboard_manager.py# Clipboard save/restore + selection detection
  pipeline.py         # Orchestrates detection → conversion → paste
  config.py           # Settings load/save (~/.heerif/config.json)
  startup.py          # Windows registry autostart
  tray_app.py         # System tray icon + settings popup
main.py               # Entry point
```

---

## Tech Stack

- [`pyperclip`](https://pyperclip.readthedocs.io/) — clipboard access
- [`pystray`](https://pystray.readthedocs.io/) — system tray icon
- [`Pillow`](https://pillow.readthedocs.io/) — tray icon image
- `tkinter` — settings window (built into Python)

---

## License

MIT

---

## Author

Made by **Fuad Ismayilbayli**
