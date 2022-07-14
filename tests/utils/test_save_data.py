"""
Description: Utils.save_data file Testing Module
"""
import os
from pathlib import Path
from multiprocessing import Queue
from load_testing.utils.save_data import Save, check_exists


DATA_PATH = "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/test_files/"


def test_check_exists_folder():
    """test check exists function to test folders if they exists"""
    path = Path(f"{DATA_PATH}test_folder_23_0")
    folder_path = check_exists(path=path, ext=None)
    assert folder_path.exists() is False
    folder_path.mkdir()
    assert folder_path.exists() is True
    folder_path.rmdir()


def test_check_exists_file():
    """test check exists function to test files if they exists"""
    path = Path(f"{DATA_PATH}test_file_23_0.json")
    folder_path = check_exists(path=path, ext="json")
    assert folder_path.exists() is False
    folder_path.touch()
    assert folder_path.exists() is True
    os.remove(folder_path)


def test_save():
    """test save function"""
    queue = Queue()
    file_name = "new_file_23_0.json"
    new_path = check_exists(Path(f"{DATA_PATH}{file_name}"))
    _s = Save(queue=queue, path=new_path)
    assert _s.write_initial_json() is None
    assert _s.read_json() == {}
    assert (
        _s.write_json(append_data={"frame_23_22332": 0.00034343}, read_data={}) is None
    )
    os.remove(new_path)
