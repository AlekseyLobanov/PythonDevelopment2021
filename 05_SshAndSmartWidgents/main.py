#!/usr/bin/env python3

import re

import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.constants import *


MODE_NEW = "new"
MODE_EDIT = "edit"
TAG_INCORRECT = "incorrect"
DEFAULT_FILL = "white"
DEFAULT_OUTLINE = "black"

re_descrption = re.compile(
    r"^"
    r"(?P<type>oval)"
    r"[\s]*"
    r"<"
    r"[\s]*"
    r"(?P<x0>[+\-]?\d+(\.\d*)?)"
    r"[\s]+"
    r"(?P<y0>[+\-]?\d+(\.\d*)?)"
    r"[\s]+"
    r"(?P<x1>[+\-]?\d+(\.\d*)?)"
    r"[\s]+"
    r"(?P<y1>[+\-]?\d+(\.\d*)?)"
    r"[\s]*"
    r">"
    r"[\s]*"
    r"(?P<outline_thickness>\d+(\.\d*)?)"
    r"[\s]+"
    r"(?P<outline_color>#?\w+)"
    r"[\s]+"
    r"(?P<fill_color>#?\w+)"
    r"$"
)


def text_to_shape(canvas, line):
    match = re_descrption.match(line)
    if not match:
        return
    attributes = match.groupdict()

    for color in ["fill_color", "outline_color"]:
        try:
            canvas.master.winfo_rgb(attributes[color])
        except tk.TclError:
            attributes[color] = "black"

    shape_creator = getattr(canvas, f"create_{attributes['type']}")
    shape_creator(
        attributes["x0"],
        attributes["y0"],
        attributes["x1"],
        attributes["y1"],
        width=attributes["outline_thickness"],
        outline=attributes["outline_color"],
        fill=attributes["fill_color"],
    )


def shape_to_text(canvas, shape):
    shape_type = canvas.type(shape)
    x0, y0, x1, y1 = canvas.coords(shape)
    outline_thickness = canvas.itemcget(shape, "width")
    outline_color = canvas.itemcget(shape, "outline")
    fill_color = canvas.itemcget(shape, "fill")
    return (
        f"{shape_type} "
        f"<{x0} {y0} {x1} {y1}> "
        f"{outline_thickness} "
        f"{outline_color} "
        f"{fill_color}"
    )


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master=master)

        self._text_frame = tk.LabelFrame(master=self)
        self._text = tk.Text(master=self._text_frame)
        self._text.bind("<<Modified>>", self._update_canvas)

        self._editor_frame = tk.Frame(master=self)
        self._control_pnl = tk.Frame(master=self._editor_frame)
        self._outline_color_btn = tk.Button(
            master=self._control_pnl,
            text="Цвет границы",
            command=self.show_outline_color_picker,
        )
        self._outline_color_btn.grid(row=0, column=0, padx=(20, 20))
        self._fill_color_btn = tk.Button(
            master=self._control_pnl,
            text="Цвет заливки",
            command=self.show_fill_color_picker,
        )
        self._fill_color_btn.grid(row=0, column=1)

        self._canvas = tk.Canvas(master=self._editor_frame, height=400, width=600)
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Motion>", self._on_drag)

        self.pack(expand=True, fill=BOTH)
        self._text_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self._text.pack(expand=True, fill=BOTH)
        self._text.tag_config(TAG_INCORRECT, background="#ed4b11")
        self._editor_frame.pack(side=RIGHT, expand=True, fill=BOTH)
        self._control_pnl.pack(side=TOP, expand=True, fill=X)
        self._canvas.pack(expand=True, fill=BOTH)

        self._current_shape = None
        self._outline_color = DEFAULT_OUTLINE
        self._fill_color = DEFAULT_FILL

    def _on_click(self, event):
        x0, y0, x1, y1 = event.x, event.y, event.x, event.y
        overlapping = self._canvas.find_overlapping(x0, y0, x1, y1)
        if not overlapping:
            shape = self._canvas.create_oval(
                x0, y0, x1, y1, fill=self._fill_color, outline=self._outline_color
            )
            self._current_shape = (MODE_NEW, x0, y0, shape)
        else:
            self._current_shape = (MODE_EDIT, x0, y0, overlapping[-1])

    def _on_drag(self, event):
        if self._current_shape is None:
            return
        x_event, y_event = event.x, event.y
        mode, x_origin, y_origin, shape = self._current_shape
        if mode != MODE_NEW:
            self._canvas.move(shape, x_event - x_origin, y_event - y_origin)
            self._current_shape = (MODE_EDIT, x_event, y_event, shape)
        else:
            x0, y0, x1, y1 = self._canvas.coords(shape)
            x1, y1 = x_event, y_event
            if x_event < x_origin:
                x0, x1 = x_event, x_origin
            if y_event < y_origin:
                y0, y1 = y_event, y_origin
            self._canvas.coords(shape, x0, y0, x1, y1)

    def _on_release(self, *args):
        self._current_shape = None
        self._update_text()

    def show_outline_color_picker(self):
        self._outline_color = askcolor(color=self._outline_color)[-1]

    def show_fill_color_picker(self):
        self._fill_color = askcolor(color=self._fill_color)[-1]

    def _update_text(self):
        old_text = self._text.get("1.0", END).split("\n")
        incorrect_lines = [
            line
            for line in old_text
            if re_descrption.match(line) is None and line != ""
        ]
        new_shapes = [shape_to_text(self._canvas, o) for o in self._canvas.find_all()]
        new_text = "\n".join(new_shapes + incorrect_lines)
        self._text.delete("1.0", END)
        self._text.insert("1.0", new_text)
        self._highlight_errors()

    def _update_canvas(self, *args):
        self._canvas.delete(ALL)
        text = self._text.get("1.0", END).split("\n")
        for line in text:
            text_to_shape(self._canvas, line)
        self._highlight_errors()
        self._text.edit_modified(False)

    def _highlight_errors(self):
        self._text.tag_remove(TAG_INCORRECT, "1.0", END)
        for line_ind, line in enumerate(self._text.get("1.0", END).split("\n")):
            if line and re_descrption.match(line) is None:
                self._text.tag_add(
                    TAG_INCORRECT, f"{line_ind + 1}.0", f"{line_ind + 1}.end"
                )


if __name__ == "__main__":
    app = App(master=tk.Tk())
    app.master.title("Редактор")
    app.mainloop()
