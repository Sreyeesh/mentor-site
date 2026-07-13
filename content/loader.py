from pathlib import Path
from functools import lru_cache
import tomllib
from typing import Any


CONTENT_ROOT = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_toml(relative_path: str) -> dict[str, Any]:
    path = CONTENT_ROOT / relative_path
    return tomllib.loads(path.read_text(encoding='utf-8'))


def load_page(slug: str) -> dict[str, Any]:
    return load_toml(f'pages/{slug}.toml')


def load_messages() -> dict[str, Any]:
    return load_toml('messages.toml')


def message(section: str, key: str, **values: Any) -> str:
    template = load_messages()[section][key]
    return template.format(**values)
