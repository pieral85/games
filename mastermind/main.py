#!/usr/bin/env python3

# TODO Améliorer les perfs (par exemple les palettes de couleurs pourraient n'en être qu'une)

from collections import defaultdict
from random import choice, shuffle
import tkinter
from tkinter.constants import *

COLORS = ('red', 'yellow', 'green', 'blue', 'black', 'white')
N_COLORS = 4
N_TRIALS = 10
SQUARES_SIZE = 60

tk = tkinter.Tk()


# TODO Move this class in a specific file
class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        # self.errors = errors


class Cell(tkinter.Frame):
    """docstring for Cell"""
    def __init__(self, fr_master, size=None, editable=False, *args, **kwargs):
        super().__init__(fr_master, *args, **kwargs)
        if not size:
            self.size_frame = self.cget('height')
        else:
            self.size_frame = size
        # self.size_frame = 75  # TODO Delete me
        # print(self.size_frame)
        self.config(width=self.size_frame, height=self.size_frame)
        self.fr_color = tkinter.Frame(self, width=self.size_frame, height=self.size_frame)
        self.fr_color.pack(side=TOP)
        self._add_frame_palette()
        self.color = ''
        self.editable = editable

    @property
    def color(self):
        return self._color
        # return self.fr_color.cget('bg')
    @color.setter
    def color(self, color):
        self._color = color
        self.fr_color.config(bg=color)

    @property
    def editable(self):
        return self._editable
    @editable.setter
    def editable(self, editable):
        self._editable = editable
        if editable:
            self.fr_palette.pack(side=BOTTOM)# fill=BOTH, expand=1, side=TOP)  # TODO Delete comment?
        else:
            self.fr_palette.pack_forget()


    def _add_frame_palette(self):
        self.fr_palette = tkinter.Frame(self, width=self.size_frame, height=self.size_frame)
        self.fr_palette_colors = []
        n_cols = max(len(COLORS) // 2 + len(COLORS) % 2, 2)
        size = self.size_frame // n_cols

        def set_color(color):
            self.color = color

        for i, color in enumerate(COLORS):
            fr_color = tkinter.Frame(self.fr_palette, bg=color, width=size, height=size)
            # fr_color.bind('<Button-1>', lambda ev, col=color: self.fr_color.config(bg=col))
            fr_color.bind('<Button-1>', lambda ev, col=color: set_color(col))
            fr_color.grid(row=i//n_cols, column=i%n_cols)
            self.fr_palette_colors.append(fr_color)
        # TODO Add a "reset color frame" here


# TODO Should not be instanciable (only used for inheritance) --> import ABC???
class Row(tkinter.Frame):
    """docstring for Row"""
    def __init__(self, fr_master, n_colors):
        super().__init__(fr_master)
        self.cells = []  # old: self.fr_colors
        self.n_colors = n_colors
        self._editable = False
        self.height = fr_master.cget('height')
        self.default_color = self.cget('bg')

        for _ in range(self.n_colors):
            cell = Cell(fr_master=self, size=self.height, editable=self._editable,
                        relief=RIDGE, borderwidth=1)
            cell.pack(side=LEFT, expand=1)# TODO Test with expand=0
            self.cells.append(cell)

    @property
    def editable(self):
        return self._editable
    @editable.setter
    def editable(self, editable):
        self._editable = editable
        for cell in self.cells:
            cell.editable = editable

    @property
    def colors(self):
        return [cell.color for cell in self.cells]
    @colors.setter
    def colors(self, colors):
        # TODO Test me!
        import ipdb; ipdb.set_trace()
        for color, cell in zip(colors, self.cells):
            # self.fr_color.config(bg=color)
            self.cell.color = color


class RowSolution(Row):
    """docstring for RowSolution"""
    def __init__(self, fr_master, n_colors):
        super().__init__(fr_master=fr_master, n_colors=n_colors)

    def renew_colors(self, unique_colors=True):
        if unique_colors:
            shuffled_colors = list(COLORS[:])
            shuffle(shuffled_colors)
            get_color_function = shuffled_colors.pop
        else:
            get_color_function = lambda: choice(COLORS)

        for cell in self.cells:
            cell.color = get_color_function()


class RowTrial(Row):
    """docstring for RowTrial"""
    def __init__(self, fr_master, row_solution):
        super().__init__(fr_master=fr_master, n_colors=row_solution.n_colors)
        self.row_solution = row_solution
        self._add_frame_answers()

    @property
    def answers(self):
        """ Returns a list of tuples containing the answers.
            TODO Write doc
            0: Uncorrect color
            1: Correct color with uncorrect order
            2: Correct color with correct order
        """
        answers = []
        d=defaultdict(list)
        # d['tutu'].append(5)
        # d[color].append(i) for i, color in (self.colors)
        # 1°) Check for correct colors with correct rank
        # import ipdb; ipdb.set_trace()
        for i, color in enumerate(self.colors):
            answers.append(0)  # answers.append([i, 0])
            if not color:
                raise UserError('Not able to check answers: at least one cell has not been colored.')
            color_sol = self.row_solution.colors[i]
            if color_sol == color:
                answers[i] = 2  # answers[i][1] = 2
            else:
                d[color_sol].append(i)

        # 2°) Check for correct colors w/ correct rank
        for i, color in enumerate(self.colors):
            # color already treated --> skipped
            if answers[i] != 0:  # if answers[i][1] != 0:
                continue
            if d[color]:
                answers[i] = 1  # answers[i][1] = 1
                d[color].pop()
            # else:  # not needed
            #     answers[i][1]
        return answers

    def check_answers(self, preserve_order=False):
        # TODO preserve_order
        # if not preserve_order:
        #     shuffle(answers)...TODO mettre ici ou dans get_answers?
        colors = [self.default_color, 'white', 'black']
        try:
            print('ans:', self.answers)
            answers = self.answers
            if not preserve_order:
                answers.sort(reverse=True)
            for i, answer in enumerate(answers):
                self.fr_answers[i].config(bg=colors[answer])
        except UserError:
            pass

    def _add_frame_answers(self):
        self.fr_answers_master = tkinter.Frame(self, width=self.height, height=self.height, bg='pink')
        self.fr_answers = []
        n_cols = max(self.n_colors // 2 + self.n_colors % 2, 2)
        size = self.height // n_cols
        for i in range(self.n_colors):
            fr_answer = tkinter.Frame(self.fr_answers_master, width=size, height=size, relief=RIDGE, borderwidth=1)
            fr_answer.grid(row=i//n_cols, column=i%n_cols)
            self.fr_answers.append(fr_answer)
        self.fr_answers_master.pack(side=LEFT, padx=10, anchor='nw')


class Mastermind(tkinter.Frame):
    """docstring for Mastermind"""
    def __init__(self, fr_master, square_size):
        super().__init__(fr_master)
        # fr_row_master = tkinter.Frame(fr_game, relief=RIDGE, borderwidth=2, height=SQUARES_SIZE)
        # fr_row_master.pack(fill=BOTH, expand=1)#, side=BOTTOM)
# fr_row_trials = tkinter.Frame(fr_game, relief=RIDGE, borderwidth=2, height=SQUARES_SIZE)  # , height=50)
# fr_row_trials.pack(fill=BOTH, expand=1, side=BOTTOM)

        # row_solution = RowSolution(fr_master=fr_row_master, n_colors=N_COLORS)
        # row_solution.pack(fill=BOTH, expand=1, side=TOP)
        self.config(height=square_size)
        row_solution = RowSolution(fr_master=self, n_colors=N_COLORS)
        row_solution.config(height=80)
        row_solution.pack(fill=BOTH, expand=1, side=TOP)

# row_trials = []
# for _ in range(N_TRIALS):
#     row_trial = RowTrial(fr_master=fr_row_trials, row_solution=row_solution)
#     row_trial.pack(fill=BOTH, expand=1, side=BOTTOM)
#     row_trials.append(row_trial)
# row_trials[0].editable = True


    def start(self):
        pass #tk.mainloop()


fr_main = tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
fr_main.pack(fill=BOTH, expand=1)
# fr_game = tkinter.Frame(fr_main) #, relief=RIDGE, borderwidth=2, height=50)
# fr_game.pack(fill=BOTH, expand=1, side=TOP)
fr_menu = tkinter.Frame(fr_main) #, relief=RIDGE, borderwidth=2, height=50)
fr_menu.pack(fill=BOTH, expand=1, side=TOP)

bt_exit = tkinter.Button(fr_main, text="Exit", command=tk.destroy)
bt_exit.pack(fill=X, side=BOTTOM)

# fr_row_master = tkinter.Frame(fr_game, relief=RIDGE, borderwidth=2, height=SQUARES_SIZE)
# fr_row_master.pack(fill=BOTH, expand=1)#, side=BOTTOM)
# fr_row_trials = tkinter.Frame(fr_game, relief=RIDGE, borderwidth=2, height=SQUARES_SIZE)  # , height=50)
# fr_row_trials.pack(fill=BOTH, expand=1, side=BOTTOM)

# row_solution = RowSolution(fr_master=fr_row_master, n_colors=N_COLORS)
# row_solution.pack(fill=BOTH, expand=1, side=TOP)

# row_trials = []
# for _ in range(N_TRIALS):
#     row_trial = RowTrial(fr_master=fr_row_trials, row_solution=row_solution)
#     row_trial.pack(fill=BOTH, expand=1, side=BOTTOM)
#     row_trials.append(row_trial)
# row_trials[0].editable = True


if __name__ == '__main__':
    # debug mode
    var_unique_colors = tkinter.BooleanVar(value=True)
    var_preserve_order = tkinter.BooleanVar(value=False)

    fr_debug = tkinter.Frame(fr_menu, relief=RIDGE, borderwidth=2)
    fr_debug.pack(side=TOP, fill=BOTH)  # , , expand=1
    # fill=BOTH, expand=1, side=TOP
    bt_renew_colors = tkinter.Button(fr_debug, text="New Colors")
    bt_renew_colors.grid(row=0, column=0, sticky=W)
# ...    bt_renew_colors.config(command=lambda: row_solution.renew_colors(var_unique_colors.get()))
    cb_unique_colors = tkinter.Checkbutton(fr_debug, text="Unique Colors", variable=var_unique_colors)
    cb_unique_colors.grid(row=0, column=1, sticky=W)
    bt_check_answers = tkinter.Button(fr_debug, text="Check Solution")
    bt_check_answers.grid(row=1, column=0, sticky=W)
    bt_check_answers.config(command=lambda: row_trials[0].check_answers(var_preserve_order.get()))
    cb_preserve_order = tkinter.Checkbutton(fr_debug, text="Preserve Answers Order", variable=var_preserve_order)
    cb_preserve_order.grid(row=1, column=1, sticky=W)

    mastermind = Mastermind(fr_master=fr_main, square_size=SQUARES_SIZE)
    mastermind.pack(side=TOP, fill=BOTH)
    tk.mainloop()

    # mastermind.start()
