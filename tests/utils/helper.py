"""
Description: Helper functions to test the module
"""
import json
from pathlib import Path


def create_file(path: Path):
    """create file if not exists

    Args:
        path (Path): path to file
    """
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            data = [{"thread-10": 0.2}, {"thread-20": 0.3}]
            json.dump(data, f)
