"""
Description: save generated data from other processes
Author: Prabal Pathak
"""
from multiprocessing import Process, Queue
from pathlib import Path
import json


class Save:
    """Save the data to json file"""

    def __init__(self, queue: Queue, path: Path, **kwargs):
        self.queue = queue
        self.path = path
        self.kwargs = kwargs
        self.data = None
        self.encoding = "utf-8"

    def write_json(self, append_data: dict):
        """get all the data and filter write"""
        key = list(append_data.keys())[0]
        if not self.data.get(key):
            self.data[key] = [append_data[key]]
        else:
            self.data[key].append(append_data[key])
        with open(self.path, "w", encoding=self.encoding) as write_object:
            json.dump(self.data, write_object)

    def write_initial_json(self):
        """write initial objects for json"""
        if self.path.exists():
            raise ValueError("Path already exists")
        with open(self.path, "w", encoding=self.encoding) as write_object:
            json.dump({}, write_object)

    def read_json(self):
        """read the json file"""
        with open(self.path, "r", encoding=self.encoding) as f:
            self.data = json.load(f)
            print(self.data)

    def run(self):
        """run the process in a while loop"""
        self.write_initial_json()
        while True:
            if self.queue.empty():
                continue
            data = self.queue.get()
            print("Putting: ", data)
            self.read_json()
            self.write_json(data)


def check_exists(path: Path) -> Path:
    """check if path exists if yes then return
    modified path

    Args:
        path (Path): _description_

    Returns:
        Path: _description_
    """
    if path.exists():
        count = 0
        parent = path.parent
        while path.exists():
            file_name = path.stem
            data = file_name.split("_")
            data.pop()
            file_name = f'{"_".join(data)}_{str(count)}'
            path = Path(f"{str(parent)}/{file_name}.json")
            count += 1
    return path


def start_save_process(path: Path, queue: Queue) -> None:
    """start saving process"""
    new_path = check_exists(path)
    s = Save(queue=queue, path=new_path)
    Process(target=s.run).start()


if __name__ == "__main__":
    csv_file_path = Path(
        "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/test_files/new_file_13_0.json"
    )
    data_path = check_exists(csv_file_path)
    data_path.touch()
    print(data_path)
