from pathlib import Path
import tomllib
from typing import Any


CONTENT_ROOT = Path(__file__).resolve().parent


def load_toml(relative_path: str) -> dict[str, Any]:
    path = CONTENT_ROOT / relative_path
    return tomllib.loads(path.read_text(encoding='utf-8'))


def load_page(slug: str) -> dict[str, Any]:
    return load_toml(f'pages/{slug}.toml')
