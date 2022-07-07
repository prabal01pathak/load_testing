#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Optional

from pydantic import BaseModel
from fastapi import Depends


class Args:
    host: Optional[str] = "127.0.0.1"
    port: Optional[int] = 8000

def main(data: Args):
    print(data)
    os.system(f"uvicorn load_testing.main:app --host {data.host} --port {data.port} --reload")


def test(host: Optional[str], port: Optional[int]):
    data = Args()
    print(data.host, data.port)
    return data

if __name__ == "__main__":
    test(host="name", port="hi")
