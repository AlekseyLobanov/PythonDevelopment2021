#!/usr/bin/env python3

import random
import time
from functools import partial

import tkinter as tk
from tkinter import messagebox as mb


GAME_SIZE = 4
POSSIBLE_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
INIT_RANDOM_STEPS = 5
NEW_GAME_RANDOM_STEPS = 1000


def get_val_pos(state, val):
    for i in range(GAME_SIZE):
        for j in range(GAME_SIZE):
            if state[i][j] == val:
                return i, j


def swap_cells(state, first, second):
    state[first[0]][first[1]], state[second[0]][second[1]] = (
        state[second[0]][second[1]],
        state[first[0]][first[1]],
    )


def get_game_state(steps=0):
    res = [[0 for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]
    for i in range(GAME_SIZE):
        for j in range(4):
            if i == GAME_SIZE - 1 and j == GAME_SIZE - 1:
                # empty cell
                continue
            res[i][j] = i * GAME_SIZE + j + 1

    empty_pos = get_val_pos(res, 0)
    for step_ind in range(steps):
        possbile_next_cells = []
        for delta_x, delta_y in POSSIBLE_MOVES:
            next_cell = (empty_pos[0] + delta_x, empty_pos[1] + delta_y)
            if 0 <= next_cell[0] < GAME_SIZE and 0 <= next_cell[1] < GAME_SIZE:
                possbile_next_cells.append(next_cell)
        next_cell = random.choice(possbile_next_cells)
        # swap == one move
        swap_cells(res, empty_pos, next_cell)
        empty_pos = next_cell
    return res


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)
        self.grid(sticky="news", column=0, row=0)
        self.createWidgets()

        self.rowconfigure(0, weight=1)
        for i in range(1, 5):
            self.rowconfigure(i, weight=3)
        for i in range(4):
            self.columnconfigure(i, weight=1)

    def createWidgets(self):
        self.new_bt = tk.Button(self, text="New", command=self.process_new_game)
        self.exit_bt = tk.Button(self, text="Exit", command=self.quit)
        self.new_bt.grid(row=0, column=0, columnspan=2)
        self.exit_bt.grid(row=0, column=2, columnspan=2)
        self.game_buttons = self.create_game_buttons()
        self.game_state = get_game_state(INIT_RANDOM_STEPS)
        self.render_current_state()

    def create_game_buttons(self):
        res = {}
        for i in range(GAME_SIZE * GAME_SIZE):
            btn_value = i + 1
            btn = tk.Button(
                self,
                text=str(btn_value),
                command=partial(self.process_number_press, btn_value),
            )
            res[btn_value] = btn
        return res

    def process_number_press(self, val):
        val_pos = get_val_pos(self.game_state, val)
        empty_pos = get_val_pos(self.game_state, 0)
        delta = (empty_pos[0] - val_pos[0], empty_pos[1] - val_pos[1])
        if delta not in POSSIBLE_MOVES:
            return
        swap_cells(self.game_state, val_pos, empty_pos)
        self.render_current_state()
        if self.game_state == get_game_state(0):
            mb.showinfo(title="Info", message="You win!")
            self.game_state = get_game_state(NEW_GAME_RANDOM_STEPS)
            self.render_current_state()

    def process_new_game(self):
        self.game_state = get_game_state(NEW_GAME_RANDOM_STEPS)
        self.render_current_state()

    def render_current_state(self):
        for i in range(4):
            for j in range(4):
                btn_value = self.game_state[i][j]
                if btn_value == 0:
                    continue
                btn = self.game_buttons[btn_value]
                btn.grid(row=i + 1, column=j, sticky="news")


if __name__ == "__main__":
    app = Application()
    app.master.title("15-шки")
    app.mainloop()
