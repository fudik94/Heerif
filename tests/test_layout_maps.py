from src.layout_maps import EN_RU, RU_EN, get_maps


def test_en_ru_sample():
    assert EN_RU['q'] == 'й'
    assert EN_RU['a'] == 'ф'
    assert EN_RU['g'] == 'п'
    assert EN_RU['h'] == 'р'
    assert EN_RU['b'] == 'и'


def test_uppercase_preserved():
    assert EN_RU['Q'] == 'Й'
    assert EN_RU['G'] == 'П'


def test_ru_en_is_reverse_of_en_ru():
    for en_char, ru_char in EN_RU.items():
        assert RU_EN[ru_char] == en_char


def test_get_maps_en_ru():
    maps = get_maps('en_ru')
    assert maps['en_ru'] is EN_RU
    assert maps['ru_en'] is RU_EN


def test_known_word_welcome():
    # 'цудсщьу' typed on RU layout when intending 'welcome'
    word = 'цудсщьу'
    result = ''.join(RU_EN.get(c, c) for c in word)
    assert result == 'welcome'


def test_known_word_privet():
    # 'ghbdtn' typed on EN layout when intending 'привет'
    word = 'ghbdtn'
    result = ''.join(EN_RU.get(c, c) for c in word)
    assert result == 'привет'
