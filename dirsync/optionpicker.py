import sys
import treelib

import treepicker


class OptionPicker(object):
    def __init__(self, options):
        self._options = options
        self._picked_indices = list()

    def pick_one(self):
        return self._pick(nr_options_to_pick=1)[0]

    def pick_several(self, nr_options_to_pick):
        return self._pick(nr_options_to_pick)

    def _pick(self, nr_options_to_pick):
        raise NotImplementedError


class OptionPickerByNumbers(OptionPicker):
    def __init__(self, options):
        super(OptionPicker, self).__init__(options)

    def _pick(self, nr_options_to_pick):
        assert nr_options_to_pick <= len(self._options)
        if len(self._options) == nr_options_to_pick:
            if nr_options_to_pick == 2:
                print "The following replicas were found:"
                print "To use them, press enter."
            elif nr_options_to_pick == 1:
                print "The following replica was found: \n\n\t%s\n" % (self._options[0],)
                print "To use it, press enter."
            self._continue_only_on_enter()
            picked_options = self._options
        else:
            for _ in xrange(nr_options_to_pick):
                self._pick_option()
            picked_options = [self._options[index] for index in self._picked_indices]
        return picked_options

    def _print_options(self):
        possible_indices = [index for index in xrange(len(self._options)) if
                            index not in self._picked_indices]
        for index in possible_indices:
            print "\t%d: %s" % (index, self._options[index])

    def _pick_option(self):
        print "Pick an option by typing its number"
        self._print_options()
        max_index = len(self._options) - 1
        while True:
            print ">>> ",
            raw_index = raw_input()
            try:
                index = int(raw_index)
            except ValueError:
                print "Cannot parse index. please try again."
                continue
            if index > max_index or index < 0:
                print "Please specify a number between 0 and %d" % (max_index,)
                continue
            break
        self._picked_indices.append(index)

    def _continue_only_on_enter(self):
        if raw_input():
            sys.exit(1)


class OptionPickerByMenuTraverse(OptionPicker):
    def __init__(self, options):
        super(OptionPickerByMenuTraverse, self).__init__(options)

    def _pick(self, nr_options_to_pick):
        tree = treelib.Tree()
        tree.create_node(tag='Options')
        for index, option in enumerate(self._options):
            tree.create_node(tag=option, data=option, identifier=str(index), parent=tree.root)
        picker = treepicker.TreePicker(tree, min_nr_options=1, max_nr_options=1)
        if nr_options_to_pick == 1:
            options = [picker.pick_one(max_nr_lines=10)]
        else:
            options = picker.pick_one(max_nr_lines=10)
        return options


if __name__ == "__main__":
    picker = OptionPickerByMenuTraverse(['first', 'second', 'third'])
    print picker.pick_one()
