import os
import treelib

import keybind
import printer
import treesearch
import linescanner
import treenavigator
import treepicker_keybindings
import treepicker_shelloutput


class TreePicker(object):
    _MODE_NAVIGATION = 'navigation'
    _MODE_SEARCH = 'search'
    _MODE_INTERACTIVE_SEARCH = 'interactive search'
    _MODE_RETURN = 'return'
    _MODE_QUIT = 'quit'

    def __init__(self, tree, including_root=True, header=None, max_nr_lines=25,
                 min_nr_options=1, max_nr_options=None):
        self._tree = tree
        self._min_nr_options = min_nr_options
        self._max_nr_options = len(self._tree) if max_nr_options is None else max_nr_options
        self._max_nr_lines = max_nr_lines
        self._picked = dict()
        self._mode = self._MODE_NAVIGATION
        self._header = header
        self._tree_search = treesearch.TreeSearch(self._tree)
        self._line_scanner = linescanner.LineScanner()
        self._navigation_actions = keybind.KeyBind()
        self._tree_navigator = treenavigator.TreeNavigator(self._tree, including_root)
        treepicker_keybindings.populate_bindings(self._navigation_actions)
        treepicker_keybindings.register_actions(self._navigation_actions, self, self._tree_navigator)
        self._shelloutput = treepicker_shelloutput.TreePickerShellOutput(self._tree, self._header, max_nr_lines)

    def pick_one(self):
        choices = self.pick()
        return None if not choices else choices[0]

    def pick(self):
        print_tree_once = True
        picked = None
        while picked is None:
            if print_tree_once:
                self._print_tree()
            print_tree_once = True
            if self._mode == self._MODE_NAVIGATION:
                previous_state = self._capture_state()
                self._navigation_actions.do_one_action()
                current_state = self._capture_state()
                print_tree_once = previous_state != current_state
            elif self._mode == self._MODE_SEARCH:
                result = self._line_scanner.scan_char()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._filter_tree_entries_by_search_pattern()
                    self._mode = self._MODE_NAVIGATION
            elif self._mode == self._MODE_INTERACTIVE_SEARCH:
                result = self._line_scanner.scan_char()
                self._filter_tree_entries_by_search_pattern()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._mode = self._MODE_NAVIGATION
            elif self._mode == self._MODE_RETURN:
                picked = self._picked.values()
            elif self._mode == self._MODE_QUIT:
                picked = list()
            else:
                raise ValueError(self._mode)
        return [node.data for node in picked]

    def start_search(self):
        self._mode = self._MODE_SEARCH
        self._line_scanner.clear_line()

    def start_interactive_search(self):
        self._mode = self._MODE_INTERACTIVE_SEARCH
        self._line_scanner.clear_line()

    def quit(self):
        self._mode = self._MODE_QUIT

    def toggle(self):
        selected_node = self._tree_navigator.get_selected_node()
        # No toggle with only one option
        if self._min_nr_options == self._max_nr_options == 1:
            return
        is_picked = selected_node.identifier in self._picked
        toggle_node = self._unpick_node if is_picked else self._pick_node
        toggle_node(selected_node)
        for node in self._tree.subtree(selected_node.identifier).nodes.itervalues():
            toggle_node(node)

    def return_picked_nodes(self):
        if self._min_nr_options == self._max_nr_options == 1:
            selected_node = self._tree_navigator.get_selected_node()
            self._picked = {selected_node.identifier: selected_node}
            self._mode = self._MODE_RETURN
        elif self._min_nr_options <= len(self._picked) <= self._max_nr_options:
            self._mode = self._MODE_RETURN

    def _print_tree(self):
        search_pattern = self._line_scanner.get_line()
        self._shelloutput.print_tree(self._tree_navigator.get_selected_node(), search_pattern, self._picked,
                                     self._mode)
    def _capture_state(self):
        picked = hash(str(self._picked.keys()))
        return (picked, self._tree_navigator.get_selected_node().identifier, self._mode)

    def _filter_tree_entries_by_search_pattern(self):
        search_pattern = self._line_scanner.get_line()
        self._tree = self._tree_search.get_filtered_tree(search_pattern)
        self._tree_navigator.set_tree(self._tree)
        self._shelloutput.set_tree(self._tree)

    def _pick_node(self, node):
        self._picked[node.identifier] = node

    def _unpick_node(self, node):
        if node.identifier in self._picked:
            del self._picked[node.identifier]


if __name__ == '__main__':
    thetree = treelib.Tree()
    root_ = thetree.create_node(identifier='rootnodeid', tag='rootnodetag', data='rootnodeval')
    for i in range(5) + range(10, 15):
        name = "childnode%s" % (i,)
        thetree.create_node(name, name, parent='rootnodeid', data=name)
    for i in xrange(3, 9):
        name = "grandson%d" % (i,)
        thetree.create_node(name, name, parent='childnode4', data=name)
    for i in xrange(7):
        name = "grandgrandson%d" % (i,)
        thetree.create_node(name, name, parent='grandson7', data=name)
    for i in [7, 8, 9]:
        name = "grandgrandson%d" % (i * 11,)
        thetree.create_node(name, name, parent='grandson8', data=name)

    treepicker = TreePicker(thetree, header='stuff:')

    if os.getenv('MODE') == 'static':
        printer.wrapper(treepicker.pick)
    else:
        print treepicker.pick()
