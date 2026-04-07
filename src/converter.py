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
    """Auto-detect layout direction and convert to the other layout."""
    layout = detect_layout(text)
    result = []
    for char in text:
        if layout == 'ru':
            result.append(ru_en.get(char, char))
        else:
            # For English layout, apply RU_EN to Cyrillic chars (they're mislabeled)
            # and EN_RU to Latin chars
            if '\u0400' <= char <= '\u04FF':
                result.append(ru_en.get(char, char))
            else:
                result.append(en_ru.get(char, char))
    return ''.join(result)
