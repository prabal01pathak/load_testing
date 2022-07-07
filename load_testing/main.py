#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import Tk, ttk
from .frames.home_screen import Home


class WindowManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.resizable(True, True)
        self.home_container = Home(self)
        self.home_container.tkraise()
        


def main():
    root = WindowManager()
    root.mainloop()


if __name__ == "__main__":
    main()
