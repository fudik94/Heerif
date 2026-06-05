from unittest.mock import patch
from src.config import Config, load_config, save_config

def test_default_config():
    cfg = Config()
    assert cfg.hotkey == 'ctrl+f12'
    assert cfg.language_pair == 'en_ru'
    assert cfg.selection_mode is True
    assert cfg.buffer_mode is True
    assert cfg.buffer_size == 200
    assert cfg.launch_at_startup is False

def test_save_and_load_roundtrip(tmp_path):
    cfg = Config(hotkey='ctrl+alt+z', language_pair='en_ru', selection_mode=False)
    config_file = tmp_path / 'config.json'
    with patch('src.config.CONFIG_PATH', config_file):
        save_config(cfg)
        loaded = load_config()
    assert loaded.hotkey == 'ctrl+alt+z'
    assert loaded.selection_mode is False

def test_load_missing_file_returns_defaults(tmp_path):
    missing = tmp_path / 'nonexistent' / 'config.json'
    with patch('src.config.CONFIG_PATH', missing):
        cfg = load_config()
    assert cfg.hotkey == 'ctrl+f12'

def test_save_creates_parent_dirs(tmp_path):
    config_file = tmp_path / 'nested' / 'dir' / 'config.json'
    with patch('src.config.CONFIG_PATH', config_file):
        save_config(Config())
    assert config_file.exists()
