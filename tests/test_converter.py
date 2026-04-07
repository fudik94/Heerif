from src.converter import detect_layout, convert, auto_convert
from src.layout_maps import EN_RU, RU_EN


def test_detect_cyrillic():
    assert detect_layout('привет') == 'ru'


def test_detect_latin():
    assert detect_layout('hello') == 'en'


def test_detect_mixed_majority_cyrillic():
    assert detect_layout('приветhello') == 'ru'


def test_detect_empty_defaults_to_en():
    assert detect_layout('') == 'en'


def test_convert_with_map():
    result = convert('ghbdtn', EN_RU)
    assert result == 'привет'


def test_convert_unmapped_chars_preserved():
    result = convert('hello 123!', EN_RU)
    assert '1' in result
    assert '2' in result
    assert '3' in result
    assert '!' in result
    assert ' ' in result


def test_auto_convert_latin_to_cyrillic():
    # 'ghbdtn' typed on EN layout → should become 'привет'
    result = auto_convert('ghbdtn', EN_RU, RU_EN)
    assert result == 'привет'


def test_auto_convert_cyrillic_to_latin():
    # 'цудсщьу' typed on RU layout → should become 'welcome'
    result = auto_convert('цудсщьу', EN_RU, RU_EN)
    assert result == 'welcome'


def test_auto_convert_preserves_spaces():
    result = auto_convert('ghbdtn ьшк', EN_RU, RU_EN)
    assert result == 'привет mir'
