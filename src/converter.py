"""Layout detection and conversion for keyboard input."""


def detect_layout(text: str) -> str:
    """Return 'ru' if text is majority Cyrillic, 'en' otherwise."""
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in text if c.isalpha() and c.isascii())
    return 'ru' if cyrillic > latin else 'en'


def convert(text: str, layout_map: dict[str, str]) -> str:
    """Convert each character using layout_map; unmapped characters pass through."""
    return ''.join(layout_map.get(c, c) for c in text)


def auto_convert(
    text: str,
    en_ru: dict[str, str],
    ru_en: dict[str, str],
) -> str:
    """Auto-detect majority layout and convert each character to the other layout.

    Latin chars are converted via en_ru; Cyrillic chars via ru_en.
    Detection determines which map is applied to ambiguous (non-alpha) characters.
    """
    layout = detect_layout(text)
    if layout == 'ru':
        return convert(text, ru_en)
    return ''.join(
        ru_en.get(c, c) if '\u0400' <= c <= '\u04FF' else en_ru.get(c, c)
        for c in text
    )
