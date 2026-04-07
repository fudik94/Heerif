EN_RU: dict[str, str] = {
    # Lowercase
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
    'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п',
    'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д',
    'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и',
    'n': 'т', 'm': 'ь',
    # Uppercase
    'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е',
    'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
    'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П',
    'H': 'Р', 'J': 'О', 'K': 'Л', 'L': 'Д',
    'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И',
    'N': 'Т', 'M': 'Ь',
    # Punctuation
    ';': 'ж', "'": 'э', '[': 'х', ']': 'ъ', ',': 'б', '.': 'ю',
    ':': 'Ж', '"': 'Э', '{': 'Х', '}': 'Ъ', '<': 'Б', '>': 'Ю',
    '`': 'ё', '~': 'Ё',
}

RU_EN: dict[str, str] = {v: k for k, v in EN_RU.items()}


def get_maps(language_pair: str) -> dict[str, dict[str, str]]:
    """Return forward and reverse maps for the given language pair."""
    if language_pair == 'en_ru':
        return {'en_ru': EN_RU, 'ru_en': RU_EN}
    # Default fallback — future pairs can be added here
    return {'en_ru': EN_RU, 'ru_en': RU_EN}
