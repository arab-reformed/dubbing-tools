#!/usr/bin/env python3
import os
from tkinter import *
import tkinter as ttk
from tkinter import filedialog
from dubbing_tools.transcript import *
import os

root = Tk()

root.title = 'Dubbing Tools'
root.geometry('480x480')
project_path = StringVar()
transcript = None
languages = StringVar()


def select_project():
    global transcript

    project_path.set(filedialog.askdirectory(initialdir=os.getcwd()))
    transcript = Transcript.load(project_path.get())
    languages.set(', '.join(list(transcript.phrases[0].targets.keys())))


project_label = Label(
    root,
    textvariable=project_path,
)
project_label.pack()

project_open = Button(
    root,
    text='Open Project',
    command=select_project,
)
project_open.pack()

langs_label = Label(
    root,
    textvariable=languages,
)
langs_label.pack()

root.mainloop()
