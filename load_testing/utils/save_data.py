"""
Description: save generated data from other processes
Author: Prabal Pathak
"""
import time
from multiprocessing import Process, Queue
from pathlib import Path
import json


class Save:
    """Save the data to json file"""

    def __init__(self, queue: Queue, path: Path, **kwargs: dict):
        self.queue = queue
        self.path = path
        self.kwargs = kwargs
        self.run_time = self.kwargs.get("run_time")
        self.encoding = "utf-8"
        self.start_time = time.time()

    def write_json(self, append_data: dict, read_data: dict):
        """get all the data and filter write"""
        key = list(append_data.keys())[0]
        if not read_data.get(key):
            read_data[key] = [append_data[key]]
        else:
            read_data[key].append(append_data[key])
        with open(self.path, "w", encoding=self.encoding) as write_object:
            json.dump(read_data, write_object)

    def write_initial_json(self):
        """write initial objects for json"""
        if self.path.exists():
            raise ValueError("Path already exists")
        with open(self.path, "w", encoding=self.encoding) as write_object:
            json.dump({}, write_object)

    def read_json(self):
        """read the json file"""
        with open(self.path, "r", encoding=self.encoding) as _f:
            read_data = json.loads(_f.read())
            # print(self.data)
        return read_data

    def save_without_run(self, data: dict):
        """save data to json without running in different process

        Args:
            data (dict): data to append
        """
        read_data = self.read_json()
        self.write_json(data, read_data)

    def append_data(self, data):
        """append data without running in different process"""
        read_data = self.read_json()
        with open(self.path, "w", encoding=self.encoding) as _f:
            read_data.append(data)
            json.dump(read_data, _f)

    def stopping_condition(self):
        """Process Stopping condition
        run for time and then till queue is not empty
        """
        stopping_time = time.time() - self.start_time
        if stopping_time <= self.run_time:
            return True
        if not self.queue.empty():
            return True
        return False

    def run(self):
        """run the process in a while loop"""
        self.write_initial_json()
        while self.stopping_condition():
            data = self.queue.get()
            print("Putting: ", data)
            read_data = self.read_json()
            self.write_json(append_data=data, read_data=read_data)
        print("Stopping json saving process queue size: ", self.queue.qsize())


def check_exists(path: Path, ext: str = "json") -> Path:
    """check if path exists if yes then return
    modified path

    Args:
        path (Path): path to file or folder
        ext (str): extension default json if folder give it None

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
            if not ext:
                path = Path(f"{str(parent)}/{file_name}")
            else:
                path = Path(f"{str(parent)}/{file_name}.{ext}")
            count += 1
    return path


def start_save_process(path: Path, queue: Queue, **kwargs) -> None:
    """start saving process"""
    new_path = check_exists(path)
    _s = Save(queue=queue, path=new_path, **kwargs)
    Process(target=_s.run).start()


if __name__ == "__main__":
    csv_file_path = Path(
        "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/test_files/new_file_13_0",
    )
    data_path = check_exists(path=csv_file_path, ext=None)
    data_path.mkdir()
    print(data_path)
