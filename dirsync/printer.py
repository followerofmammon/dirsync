import curses
import termcolor


_printer = None


def print_string(string, color=None):
    _printer.print_string(string, color)


def clear_screen():
    _printer.clear_screen()


def wrapper(main, *args, **kwargs):

    def store_window_and_run(window):
        global _printer
        _printer = _CursesWindowPrinter(window)
        main(*args, **kwargs)

    curses.wrapper(store_window_and_run)


class _Printer(object):
    def print_string(self, string, color=None):
        raise NotImplementedError

    def clear_screen(self, string, color=None):
        raise NotImplementedError


class _CursesWindowPrinter(object):
    _COLOR_NAME_TO_NUMBEER = {'red': 2, 'green': 3, 'blue': 5}
    def __init__(self, window):
        super(_CursesWindowPrinter, self).__init__()
        self._line_index = 0
        self._window = window
        self._initialize_colors()

    def _initialize_colors(self):
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def _add_line(self, string, color):
        string = string.replace('\xe2\x94\x80', '-')
        string = string.replace('\xe2\x94\x82', '|')
        string = string.replace('\xe2\x94\x9c', '+')
        string = string.replace('\xe2\x94\x94', '+')
        if color is None:
            color = 0
        else:
            color = curses.color_pair(self._COLOR_NAME_TO_NUMBEER[color])
        self._window.addstr(self._line_index, 0, string, color)
        self._line_index += 1

    def print_string(self, string, color=None):
        for line in string.splitlines():
            self._add_line(line, color)
        self._window.refresh()

    def clear_screen(self):
        self._window.clear()
        self._line_index = 0
        self._window.refresh()


class _ConsolePrinter(_Printer):
    def __init__(self):
        super(_ConsolePrinter, self).__init__()

    def print_string(self, string, color=None):
        if color is None:
            print string
        else:
            print termcolor.colored(string, color)

    def clear_screen(self):
        print


_printer = _ConsolePrinter()
