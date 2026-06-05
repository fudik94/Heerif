"""Tests for the conversion pipeline orchestration."""
from unittest.mock import MagicMock, patch
from src.pipeline import ConversionPipeline
from src.config import Config
from src.layout_maps import EN_RU, RU_EN

MAPS = {'en_ru': EN_RU, 'ru_en': RU_EN}


def _make_pipeline(config=None, selection=None):
    cfg = config or Config()
    clipboard = MagicMock()
    clipboard.get_selection.return_value = selection
    pipeline = ConversionPipeline(cfg, clipboard, MAPS)
    return pipeline, clipboard


def test_converts_selected_latin_to_cyrillic():
    pipeline, clip = _make_pipeline(selection='ghbdtn')
    pipeline.run()
    clip.set.assert_called_once_with('привет')


def test_converts_selected_cyrillic_to_latin():
    pipeline, clip = _make_pipeline(selection='привет')
    pipeline.run()
    clip.set.assert_called_once_with('ghbdtn')


def test_does_nothing_when_no_text():
    pipeline, clip = _make_pipeline(selection=None)
    pipeline.run()
    clip.set.assert_not_called()


def test_selection_mode_disabled_skips_ctrl_c():
    cfg = Config(selection_mode=False, buffer_mode=False)
    pipeline, clip = _make_pipeline(config=cfg)
    pipeline.run()
    clip.get_selection.assert_not_called()


def test_buffer_mode_uses_shift_home_when_no_selection():
    cfg = Config(selection_mode=True, buffer_mode=True)
    pipeline, clip = _make_pipeline(config=cfg, selection=None)
    pipeline.run()
    # select_to_line_start should be called to auto-select the current line
    clip.select_to_line_start.assert_called_once()
