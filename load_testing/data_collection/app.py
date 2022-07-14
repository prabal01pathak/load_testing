#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: server to save the data
"""

from pathlib import Path
from queue import Queue

from fastapi import FastAPI
from pydantic import BaseModel

from ..utils.save_data import Save


class Data(BaseModel):
    """data to save

    Args:
        BaseModel (pydantic.basemodel): pydantic basemodel
    name: str, time: float
    """

    name: str
    time: float


class FileMetaData(BaseModel):
    """file meta data required

    Args:
        BaseModel (pydantic.basemodel): pydantic basemodel
    path: pathlib.Path
    """

    path: Path


app = FastAPI()

METADATA = {}


@app.get("/")
def root() -> dict:
    """root route

    Returns:
        dict: acknowledgment
    """
    return {"message": "running"}


@app.post("/create_file")
def create_file(data: FileMetaData) -> dict:
    """

    Args:
        data (FileMetaData): file path to create

    Returns:
        dict: acknowledgment
    """
    _save = Save(Queue, data.path)
    _save.write_initial_json()
    METADATA["path"] = data.path
    return {"message": "file created succesfully"}


@app.post("/save")
def start_saving(data: Data) -> dict:
    """save the posted data

    Args:
        data (Data): dict values {name, time}

    Returns:
        dict: acknowledgment
    """
    path: Path = METADATA.get("path")
    _save = Save(Queue, path)
    new_data = {data.name: data.time}
    print("New data: ", new_data)
    _save.append_data(new_data)
    return {"message": "saved succesfully"}
