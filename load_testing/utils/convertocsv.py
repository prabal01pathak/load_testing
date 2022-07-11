"""
Description: Convert json log data to csv
Author: Prabal Pathak
"""

import json
import pandas as pd


class Converter:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.encoding = "utf-8"

    def convert_json_to_csv(self):
        """convert json data to pd.Dataframe"""
        with open(self.file_name, "r", encoding=self.encoding) as file:
            data = json.load(file)
        dataframe = pd.DataFrame(data)
        dataframe = self.clean_dataframe(dataframe=dataframe)
        print(dataframe)
        self.save_to_csv(dataframe=dataframe)

    def clean_dataframe(self, dataframe: pd.DataFrame):
        """clean the dataframe remove nan values

        Args:
            dataframe (pd.DataFrame): dataframe to clean
        """
        keys = sorted(dataframe.keys())
        new_dataframe = pd.DataFrame()
        for key in keys:
            _column = dataframe[key]
            _column = _column.dropna(axis=0)
            new_dataframe[key] = _column.reset_index(drop=True)
        print(_column.index)
        print(new_dataframe.index)
        return new_dataframe
        # remove nan values

    def save_to_csv(self, dataframe: pd.DataFrame):
        """save converted dataframe to csv

        Args:
            dataframe (pd.Dataframe): dataframe to save
        """
        dataframe.to_csv("logs4.csv")


if __name__ == "__main__":
    convert = Converter("../../logs/logs5.json")
    convert.convert_json_to_csv()
