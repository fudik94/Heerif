"""Tests for the conversion pipeline orchestration."""
from unittest.mock import MagicMock, patch
from src.pipeline import ConversionPipeline
from src.config import Config
from src.layout_maps import EN_RU, RU_EN

MAPS = {'en_ru': EN_RU, 'ru_en': RU_EN}


def _make_pipeline(config=None, clipboard_text=None, buffer_text=''):
    cfg = config or Config()
    buffer = MagicMock()
    buffer.peek.return_value = buffer_text
    clipboard = MagicMock()
    clipboard.get_selection.return_value = clipboard_text
    return ConversionPipeline(cfg, buffer, clipboard, MAPS), buffer, clipboard


def test_uses_selection_when_available():
    pipeline, buf, clip = _make_pipeline(clipboard_text='ghbdtn')
    with patch('src.pipeline.paste_text') as mock_paste:
        pipeline.run()
    mock_paste.assert_called_once_with(clip, 'привет')


def test_falls_back_to_buffer_when_no_selection():
    pipeline, buf, clip = _make_pipeline(clipboard_text=None, buffer_text='ghbdtn')
    with patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_type.assert_called_once_with('ghbdtn', 'привет')


def test_does_nothing_when_both_empty():
    pipeline, buf, clip = _make_pipeline(clipboard_text=None, buffer_text='')
    with patch('src.pipeline.paste_text') as mock_paste, \
         patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_paste.assert_not_called()
    mock_type.assert_not_called()


def test_selection_mode_disabled_skips_clipboard():
    cfg = Config(selection_mode=False, buffer_mode=True)
    pipeline, buf, clip = _make_pipeline(config=cfg, clipboard_text='ghbdtn', buffer_text='ghbdtn')
    with patch('src.pipeline.type_replacing'):
        pipeline.run()
    clip.get_selection.assert_not_called()


def test_buffer_mode_disabled_skips_buffer():
    cfg = Config(selection_mode=True, buffer_mode=False)
    pipeline, buf, clip = _make_pipeline(config=cfg, clipboard_text=None, buffer_text='ghbdtn')
    with patch('src.pipeline.paste_text') as mock_paste, \
         patch('src.pipeline.type_replacing') as mock_type:
        pipeline.run()
    mock_paste.assert_not_called()
    mock_type.assert_not_called()
