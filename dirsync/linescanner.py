import getcher


class LineScanner(object):
    COLOR = "magenta"
    STATE_EDIT_IN_PROGRESS = 1
    STATE_EDIT_ENDED = 2

    def __init__(self):
        self._getcher = getcher.GetchUnix()
        self._line = ""

    def get_line(self):
        return self._line

    def clear_line(self):
        self._line = ""

    def scan_char(self):
        key = self._getcher()
        result = self.STATE_EDIT_IN_PROGRESS
        if key == chr(13):
            result = self.STATE_EDIT_ENDED
        elif key == chr(127):
            if self._line:
                self._line = self._line[:-1]
            else:
                result = self.STATE_EDIT_ENDED
        elif ord(key) in (8, 21, 23):
            self._line = ""
        elif key in (chr(3), chr(27)):
            self._line = ""
            result = self.STATE_EDIT_ENDED
        else:
            self._line += key
        return result
