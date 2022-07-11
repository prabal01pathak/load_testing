#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: server to save the data
Author: Prabal Pathak
"""

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from queue import Queue

from ..utils.save_data import Save


class Data(BaseModel):
    name: str
    time: float


class FileMetaData(BaseModel):
    path: Path


app = FastAPI()

METADATA = {}


@app.get("/")
def root():
    return {"message": "running"}


@app.post("/create_file")
def create_file(data: FileMetaData):
    _save = Save(Queue, data.path)
    _save.write_initial_json()
    METADATA["path"] = data.path
    return {"message": "file created succesfully"}


@app.post("/save")
def start_saving(data: Data) -> dict:
    path: Path = METADATA.get("path")
    _save = Save(Queue, path)
    new_data = {data.name: data.time}
    print("New data: ", new_data)
    _save.append_data(new_data)
    return {"message": "saved succesfully"}
