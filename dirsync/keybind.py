import getcher


class KeyBind(object):
    def __init__(self):
        self._actions = dict()
        self._bindings = dict()
        self._getcher = getcher.GetchUnix()

    def add_action(self, name, callback, *args, **kwargs):
        self._actions[name] = (callback, args, kwargs)

    def bind(self, key, action_name):
        self._bindings[key] = action_name

    def do_one_action(self):
        key = self._getcher()
        if key in self._bindings:
            action_name = self._bindings[key]
            action, args, kwargs = self._actions[action_name]
            action(*args, **kwargs)
