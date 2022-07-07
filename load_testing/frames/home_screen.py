#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from multiprocessing import Process, Queue
from tkinter import Tk, ttk
import tkinter as tk


class Home(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.button = ttk.Button(self, text="Click Me")
        self.button.place(relx=0.2, rely = 0.2, relheight=0.4, relwidth=0.1)
        self.home_label = ttk.Label(text="Home", font=("IBMPlexSans SemiBold", 16 * -1, "bold"),
                                    style="NavBar.TLabel")
        self.home_label.place(relx=0.75, rely=0.00, relwidth=0.07, relheight=0.07)

