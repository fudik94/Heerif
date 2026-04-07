import json
from dataclasses import dataclass, asdict, fields
from pathlib import Path

CONFIG_PATH = Path.home() / '.heerif' / 'config.json'


@dataclass
class Config:
    hotkey: str = 'ctrl+space'
    language_pair: str = 'en_ru'
    selection_mode: bool = True
    buffer_mode: bool = True
    buffer_size: int = 200
    launch_at_startup: bool = False


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    data = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    valid_keys = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in valid_keys})


def save_config(config: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
