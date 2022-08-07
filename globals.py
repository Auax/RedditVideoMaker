import os
from pathlib import Path
import toml
from rich.console import Console


def is_comment_valid(text):
    return len(text) <= 1000 and "http" not in text


def abs_path(path: [str, Path]):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


toml_config = toml.load(abs_path("config.toml"))  # Global toml_config obj
console = Console()  # Global rich console instance
