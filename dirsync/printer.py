import os
import curses
import locale
import termcolor


_printer = None


def print_string(string, color=None, is_bold=False):
    _printer.print_string(string, color, is_bold)


def clear_screen():
    _printer.clear_screen()


def wrapper(main, *args, **kwargs):

    def store_window_and_run(window):
        global _printer
        _printer = _CursesWindowPrinter(window)
        main(*args, **kwargs)

    if not os.getenv("nonstatic", False):
        main(*args, **kwargs)
    else:
        locale.setlocale(locale.LC_ALL, "")
        curses.initscr()
        curses.wrapper(store_window_and_run)


class _Printer(object):
    def print_string(self, string, color=None, is_bold=False):
        raise NotImplementedError

    def clear_screen(self, string, color=None):
        raise NotImplementedError


class _CursesWindowPrinter(object):
    _COLOR_NAME_TO_NUMBEER = {'red': 2, 'green': 3, 'blue': 5, "magenta": 6, "yellow": 4,
                              'grey': 60, 'purple': 8, 'orange': 203, 'bla': 44}

    def __init__(self, window):
        super(_CursesWindowPrinter, self).__init__()
        self._index_of_last_drawn_line = -1
        self._window = window
        self._initialize_colors()
        self._lines = []

    def _initialize_colors(self):
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def _draw(self):
        window_height, max_width = self._window.getmaxyx()
        nr_lines_printed = self._index_of_last_drawn_line + 1
        is_there_room_for_more_lines = nr_lines_printed < window_height
        are_there_unprinted_lines = nr_lines_printed < len(self._lines)
        do_drawn_lines_exceed_bounds = nr_lines_printed > window_height
        if is_there_room_for_more_lines:
            if are_there_unprinted_lines:
                self._print_missing_lines(window_height, max_width)
                self._window.refresh()
        elif do_drawn_lines_exceed_bounds:
            self.clear_screen()
            self._print_missing_lines(window_height, max_width)
            self._window.refresh()

    def _print_missing_lines(self, window_height, max_width):
        max_possible_index = min(window_height, len(self._lines)) - 1
        while self._index_of_last_drawn_line < max_possible_index:
            self._index_of_last_drawn_line += 1
            line, color, is_bold = self._lines[self._index_of_last_drawn_line]
            self._print_line(line, color, self._index_of_last_drawn_line, max_width, is_bold)

    def _print_line(self, line, color, line_index, max_width, is_bold):
        if len(line) >= max_width:
            line = line[:max_width]
        if color is None:
            color = 0
        else:
            color = curses.color_pair(self._COLOR_NAME_TO_NUMBEER[color])
        attrs = color
        if is_bold:
            attrs |= curses.A_BOLD
        self._window.addstr(line_index, 0, line, attrs)

    def print_string(self, string, color=None, is_bold=False):
        for line in string.splitlines():
            self._lines.append((line, color, is_bold))
        self._draw()

    def clear_screen(self):
        self._lines = []
        self._index_of_last_drawn_line = -1
        self._window.clear()
        self._window.refresh()


class _ConsolePrinter(_Printer):
    def __init__(self):
        super(_ConsolePrinter, self).__init__()

    def print_string(self, string, color=None, is_bold=False):
        if color is None:
            print string
        else:
            attrs = list()
            if is_bold:
                attrs.append('bold')
            print termcolor.colored(string, color, attrs=attrs)

    def clear_screen(self):
        print


_printer = _ConsolePrinter()
