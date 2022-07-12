"""
Description: testing module for convert to csv file.
Author: Prabal Pathak
"""
import os
from pathlib import Path

import pandas as pd

from load_testing.utils.convertocsv import Converter
from .helper import create_file


FILE_PATH = Path("data_files/test_files/new_file_23_0.json")
OUTPUT_PATH = "data_files/test_files/new_file_23.0.csv"
create_file(FILE_PATH)
CONVERT = Converter(file_name=FILE_PATH, csv_path=OUTPUT_PATH)
DATAFRAME = pd.DataFrame(
    [
        {"thread-10": 0.00034324, "thread-20": 0.00034324},
        {"thread-10": 0.00032423, "thread-20": 0.00032423},
        {"thread-10": 0.2134, "thread-20": 0.2134},
        {"thread-10": 0.3134, "thread-20": None},
        {"thread-10": 0.1134, "thread-20": None},
        {"thread-10": 0.0002134, "thread-20": None},
    ]
)
FOR_CLEAN_DATAFRAME = pd.DataFrame(
    [
        {"thread-10": 0.00034324},
        {"thread-10": 0.00032423},
        {"thread-10": 0.2134},
        {"thread-10": 0.3134},
        {"thread-10": 0.1134},
        {"thread-10": 0.0002134},
        {"thread-20": 0.00034324},
        {"thread-20": 0.00032423},
        {"thread-20": 0.2134},
    ]
)


def test_converter_convert_json_csv():
    """test converter class"""
    data = CONVERT.convert_json_to_csv()
    assert data == True


def test_clean_dataframe():
    """test convert.clean_dataframe"""
    dataframe = CONVERT.clean_dataframe(dataframe=FOR_CLEAN_DATAFRAME)
    equal_thread_10 = dataframe["thread-10"].to_list()
    equal_thread_20 = dataframe["thread-20"].to_list()
    for i in range(3):
        assert equal_thread_10[i] == equal_thread_20[i]
    for j in range(1, 4):
        assert equal_thread_10[-i] != equal_thread_20[-i]


def test_save_to_csv():
    """test save data to csv file"""
    ack = CONVERT.save_to_csv(FOR_CLEAN_DATAFRAME)
    remove_data()
    assert ack == True


def remove_data():
    """remove generated test files"""
    os.remove(FILE_PATH)
    os.remove(OUTPUT_PATH)
