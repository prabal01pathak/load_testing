"""
Description: Convert json log data to csv
Author: Prabal Pathak
"""

import json
from pathlib import Path
import pandas as pd


class Converter:
    """convert json to csv
    Args:
        file_name(str): json file name
        csv_path(Path): output csv path
        encoding(str): utf-8
    """

    def __init__(self, file_name: str, csv_path: Path, encoding: str = "utf-8") -> None:
        self.file_name = file_name
        self.csv_path = csv_path
        self.encoding = encoding

    def convert_json_to_csv(self) -> dict:
        """convert json data to pd.Dataframe"""
        with open(self.file_name, "r", encoding=self.encoding) as file:
            data = json.load(file)
        dataframe = pd.DataFrame(data)
        dataframe = self.clean_dataframe(dataframe=dataframe)
        return self.save_to_csv(dataframe=dataframe)

    def clean_dataframe(self, dataframe: pd.DataFrame):
        """clean the dataframe remove nan values

        Args:
            dataframe (pd.DataFrame): dataframe to clean
        """
        keys = sorted(dataframe.keys())
        new_dataframe = pd.DataFrame()
        for key in keys:
            if keys == "unnamed":
                continue
            _column = dataframe[key]
            _column = _column.dropna(axis=0)
            new_dataframe[key] = _column.reset_index(drop=True)
        return new_dataframe

    def save_to_csv(self, dataframe: pd.DataFrame) -> bool:
        """save converted dataframe to csv

        Args:
            dataframe (pd.Dataframe): dataframe to save
        """
        dataframe.to_csv(self.csv_path)
        return True


if __name__ == "__main__":
    convert = Converter("../../logs/logs5.json")
    convert.convert_json_to_csv()
