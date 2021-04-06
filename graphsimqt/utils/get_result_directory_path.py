import os
from pathlib import Path


def get_result_directory_path(result_directory_name: str) -> Path:
    path_to_this_module = Path(os.path.abspath(__file__))
    return path_to_this_module.parent.parent.parent.joinpath('results').joinpath(result_directory_name)
