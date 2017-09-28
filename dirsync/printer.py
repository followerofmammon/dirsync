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

    if os.getenv("MODE", "") == "nonstatic":
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
        self._current_line_index = 0
        self._last_printed_string_index = -1
        self._window = window
        self._initialize_colors()
        self._lines = [[]]

    def _initialize_colors(self):
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def _draw(self):
        window_height, max_width = self._window.getmaxyx()
        nr_lines_printed = self._current_line_index
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

        def was_last_string_in_current_line_printed():
            return (self._last_printed_string_index ==
                    len(self._lines[self._current_line_index]) - 1)

        if was_last_string_in_current_line_printed() and self._current_line_index < max_possible_index:
            self._current_line_index += 1
            self._last_printed_string_index = -1

        iteration = 0
        while self._current_line_index <= max_possible_index:
            iteration += 1
            self._print_line(self._current_line_index, max_width)
            self._current_line_index = self._current_line_index
            if self._current_line_index < max_possible_index:
                self._current_line_index += 1
                self._last_printed_string_index = -1
            else:
                break

    def _print_line(self, line_index, max_width):
        line = self._lines[line_index]
        column = 0
        for index, (string, color, is_bold) in enumerate(line):
            if column + len(string) > max_width:
                string = string[:max(0, max_width - column)]
            if color is None:
                color = 0
            else:
                color = curses.color_pair(self._COLOR_NAME_TO_NUMBEER[color])
            attrs = color
            if is_bold:
                attrs |= curses.A_BOLD
            self._window.addstr(line_index, column, string, attrs)
            column += len(string.decode('utf-8'))
            self._last_printed_string_index = index

    def print_line(self, string, color=None, is_bold=False):
        string += "\n"
        self.print_line(string, color, is_bold)

    def print_string(self, string, color=None, is_bold=False):
        last_line_index = len(self._lines) - 1
        new_lines = string.split('\n')
        nr_new_lines = len(new_lines) - 1
        for _ in xrange(nr_new_lines):
            self._lines.append(list())
        for new_line_index, new_line in enumerate(new_lines):
            if new_line:
                target_line_index =  last_line_index + new_line_index
                current_line = self._lines[target_line_index]
                current_line.append((new_line, color, is_bold))
        self._draw()

    def clear_screen(self):
        self._lines = [[]]
        self._current_line_index = 0
        self._last_printed_string_index = -1
        self._window.clear()
        self._window.refresh()


class _ConsolePrinter(_Printer):
    def __init__(self):
        super(_ConsolePrinter, self).__init__()

    def print_string(self, string, color=None, is_bold=False):
        if color is None:
            print string,
        else:
            attrs = list()
            if is_bold:
                attrs.append('bold')
            print termcolor.colored(string, color, attrs=attrs),

    def clear_screen(self):
        print


_printer = _ConsolePrinter()
