# Layout Switcher — Design Spec

**Date:** 2026-04-07  
**Status:** Approved

## Overview

A Windows background utility written in Python that converts text typed in the wrong keyboard layout. When the user accidentally types in the wrong layout (e.g. "цудсщьу" instead of "welcome"), they press a hotkey and the text is instantly converted to the correct layout.

## User-Facing Behavior

- App runs silently in the system tray
- Default hotkey: `Ctrl+Space` (configurable)
- On hotkey press:
  - If text is selected → converts the selection
  - If nothing is selected → converts the last typed characters from the internal buffer
- Auto-detects conversion direction: Cyrillic → Latin or Latin → Cyrillic based on the characters in the text
- Default language pair: EN ↔ RU (QWERTY ↔ ЙЦУКЕН), configurable in settings

## Architecture

### Modules

| File | Responsibility |
|---|---|
| `main.py` | Entry point — initializes and connects all modules |
| `keyboard_hook.py` | Global keyboard listener (pynput); maintains a ring buffer of the last ~200 keystrokes |
| `hotkey_manager.py` | Watches for the configured hotkey; triggers the conversion pipeline |
| `converter.py` | Converts text between layouts; auto-detects direction by inspecting characters |
| `clipboard_manager.py` | Handles clipboard copy/paste; saves and restores the original clipboard contents |
| `layout_maps.py` | Keyboard layout mapping tables (EN↔RU, extensible for other pairs) |
| `tray_app.py` | System tray icon (pystray) + compact tkinter settings popup |
| `config.py` | Loads/saves settings to `~/.layoutswitcher/config.json` |

### Conversion Flow

```
User types text
    → keyboard_hook appends each character to ring buffer (max 200 chars)

User presses hotkey (e.g. Ctrl+Space)
    → Save current clipboard contents
    → If "selection mode" is enabled:
        → Simulate Ctrl+C
        → If clipboard changed → selected text detected, use it
    → Else if "buffer mode" is enabled:
        → Take text from keystroke buffer
    → Pass text to converter:
        → Scan characters to determine layout (Cyrillic or Latin)
        → Apply reverse mapping using layout_maps
    → Paste converted text back:
        → For selected text: set clipboard → Ctrl+V
        → For buffer text: send Backspace × len(text) → type converted text
    → Restore original clipboard contents
```

## Settings Popup (Compact)

A small tkinter window that appears above the tray icon on click. Contains:

- **Hotkey** — displays current hotkey; click to rebind (press new combination)
- **Language pair** — dropdown: `EN ↔ RU`, `DE ↔ RU`, etc.
- **Selection mode toggle** — on/off
- **Buffer mode toggle** — on/off
- **Launch at startup toggle** — on/off (writes to Windows registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`)

## Default Configuration

```json
{
  "hotkey": "ctrl+space",
  "language_pair": "en_ru",
  "selection_mode": true,
  "buffer_mode": true,
  "buffer_size": 200,
  "launch_at_startup": false
}
```

## Layout Maps

`layout_maps.py` stores bidirectional character mappings. Each pair maps a QWERTY key position to its Cyrillic equivalent:

```python
EN_RU = {
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
    'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    # ... full mapping
}
RU_EN = {v: k for k, v in EN_RU.items()}  # auto-generated reverse
```

Additional pairs (DE↔RU, etc.) follow the same pattern and are selected by `config.language_pair`.

## Python Dependencies

```
pynput      # global keyboard hook
pyperclip   # clipboard access
pystray     # system tray icon
Pillow      # tray icon image
tkinter     # settings popup (bundled with Python)
```

## Error Handling

- If both modes are disabled: show a notification "Enable at least one mode in settings"
- If hotkey conflicts with another app: log warning, let user rebind
- If clipboard access fails: fall back to buffer mode only

## Out of Scope

- macOS / Linux support
- More than 2 languages active simultaneously
- Real-time auto-correction (without hotkey press)
- OCR or image-based text conversion
