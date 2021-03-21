#!/usr/bin/env python3

import re

import tkinter as tk
from tkinter import messagebox as mb


DEFAULT_GRAVITATION = "NEWS"
re_constant_split = re.compile("\+")
re_weight_split = re.compile("\.")


def proces_params_data(data):
    if len(data) > 1:
        size = int(data[1])
    else:
        size = 0
    data = re_weight_split.split(data[0])
    if len(data) > 1:
        weight = int(data[1])
    else:
        weight = 1
    return size, weight, int(data[0])


class Application:
    class WidgetOrCommand:
        def __read_geometry(self):
            gravitation_split = re.compile("/")
            cur_data = gravitation_split.split(self.geometry)

            if len(cur_data) > 1:
                self.gravitation = cur_data[1]
            else:
                self.gravitation = DEFAULT_GRAVITATION

            cur_data = cur_data[0]

            params_row, params_col = list(
                map(re_constant_split.split, cur_data.split(":"))
            )

            self.height, self.row_weight, self.row = proces_params_data(params_row)
            self.width, self.column_weight, self.column = proces_params_data(params_col)

        def __init__(self, master):
            self.master = master
            pass

        def __call__(self, *args, **kwargs):
            if "text" not in kwargs:
                self.category = "command"
                self.key = args[0]
                self.func = args[1]
                return
            self.category = "widget"
            self.type = args[0]
            self.geometry = args[1]
            self.text = kwargs["text"]

            if "command" in kwargs:
                self.command = kwargs["command"]

        def __getattr__(self, name: str):
            if name not in self.__dict__:
                self.__setattr__(name, Application.WidgetOrCommand(master=self))

            return self.__dict__[name]

        def configure_widget(self):
            self.__read_geometry()

            self.master.widget.rowconfigure(index=self.row, weight=self.row_weight)
            self.master.widget.columnconfigure(
                index=self.column, weight=self.column_weight
            )

            self.widget = self.type(self.master.widget, text=self.text)
            self.widget.grid(
                column=self.column,
                row=self.row,
                sticky=self.gravitation,
                rowspan=self.height + 1,
                columnspan=self.width + 1,
            )

            if self.text.lower() == "quit":
                self.widget["command"] = self.widget.quit

        def mainloop(self):
            self.configure_widget()

            for child_name, child in self.__dict__.items():
                if isinstance(child, Application.WidgetOrCommand):
                    if child != self.master:
                        if child.category == "widget":
                            child.mainloop()

    def __init__(self, title):
        self.widget = tk.Tk()

    def mainloop(self):
        self.createWidgets()

        self.configure_window()

        for child_name, child in self.__dict__.items():
            if isinstance(child, self.WidgetOrCommand):
                if child.category == "widget":
                    child.mainloop()

        self.widget.mainloop()

    def create_widgets(self):
        raise NotImplementedError()

    def __getattr__(self, name):
        if name not in self.__dict__:
            self.__setattr__(name, self.WidgetOrCommand(master=self))

        return self.__dict__[name]

    def configure_window(self):
        self.widget.rowconfigure(index=1, weight=1)
        self.widget.rowconfigure(index=2, weight=1)
        self.widget.columnconfigure(index=0, weight=1)
        self.widget.columnconfigure(index=1, weight=1)


class App(Application):
    def createWidgets(self):
        self.message = "Congratulations!\nYou've found a sercet level!"
        self.F1(tk.LabelFrame, "1:0", text="Frame 1")
        self.F1.B1(tk.Button, "0:0/NW", text="1")
        self.F1.B2(tk.Button, "0:1/NE", text="2")
        self.F1.B3(tk.Button, "1:0+1/SEW", text="3")
        self.F2(tk.LabelFrame, "1:1", text="Frame 2")
        self.F2.B1(tk.Button, "0:0/N", text="4")
        self.F2.B2(tk.Button, "0+1:1/SEN", text="5")
        self.F2.B3(tk.Button, "1:0/S", text="6")
        self.Q(tk.Button, "2.0:1.2/SE", text="Quit", command=self.quit)
        self.F1.B3.bind(
            "<Any-Key>",
            lambda event: mb.showinfo(self.message.split()[0], self.message),
        )


app = App(title="Sample application")
app.mainloop()
