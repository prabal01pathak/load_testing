from pathlib import Path
from multiprocessing import Queue
from load_testing.utils.save_data import Save, check_exists


DATA_PATH = "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/test_files/"


def test_save():
    """test save function"""
    queue = Queue()
    file_name = "new_file_23_0.json"
    new_path = check_exists(Path(f"{DATA_PATH}{file_name}"))
    s = Save(queue=queue, path=new_path)
    assert s.write_initial_json() is None
    assert s.read_json() is None
    assert s.write_json(append_data={"frame_23_22332": 0.00034343}) is None
