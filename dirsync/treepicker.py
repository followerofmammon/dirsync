import re
import treelib

import getcher
import printer
import treeprinter


class TreePicker(object):
    _OPTION_NEXT = "Down"
    _OPTION_PREV = "Previous"
    _OPTION_UP = "Up"
    _OPTION_TOGGLE = "Toggle"
    _OPTION_RETURN = "Enter"
    _OPTION_EXPLORE = "Explore"
    _OPTION_QUIT = "Quit"
    _OPTION_MOVE_TO_SEARCH_MODE = "Move to search mode"
    _OPTION_MOVE_TO_INTERACTIVE_SEARCH_MODE = "Move to interactive search mode"
    _OPTION_MOVE_TO_FIRST_SIBLING = 'Move to first sibling'
    _OPTION_MOVE_TO_LAST_SIBLING = 'Move to last sibling'
    _OPTION_PAGE_UP = 'Page up'
    _OPTION_PAGE_DOWN = 'Page down'

    _MODE_NAVIGATION = 'navigation'
    _MODE_SEARCH = 'search'
    _MODE_INTERACTIVE_SEARCH = 'interactive search'
    _MODE_QUIT = 'quit'

    _SERACH_RESULT_SERACH_CONTINUES = 1
    _SEARCH_RESULT_SERACH_ENDED = 2

    def __init__(self, tree, min_nr_options=0, max_nr_options=None, tree_header=None):
        self._original_tree = tree
        self._tree = tree
        self._selected_node = self._tree.get_node(self._original_tree.root)
        self._picked = dict()
        self._sorted_children_by_nid_cache = dict()
        self._mode = self._MODE_NAVIGATION
        self._print_tree_once = True
        self._search_pattern = ""
        self._nodes_that_match_search_filter = dict()
        self._tree_header = tree_header

    def pick_one(self, max_nr_lines=10):
        choices = self.pick(max_nr_lines, including_root=False, min_nr_options=1, max_nr_options=1)
        if not choices:
            return None
        return choices[0]

    def pick(self, max_nr_lines, including_root=True, min_nr_options=1, max_nr_options=None):
        if max_nr_options is None:
            max_nr_options = len(self._tree.nodes)
        if not including_root:
            children = self._tree.children(self._tree.root)
            assert children
            self._selected_node = self._tree.get_node(self._tree.root)
            self._explore()
        while True:
            if self._mode == self._MODE_NAVIGATION:
                result = self._navigate(max_nr_lines, min_nr_options, max_nr_options, including_root)
                if result is not None:
                    return result
            elif self._mode == self._MODE_SEARCH:
                result = self._search()
                if result == self._SEARCH_RESULT_SERACH_ENDED:
                    self._mode = self._MODE_NAVIGATION
                else:
                    treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                                        max_nr_lines, self._search_pattern, self._tree_header,
                                        show_search_pattern_if_empty=True,
                                        is_search_patterh_being_edited=True)
            elif self._mode == self._MODE_INTERACTIVE_SEARCH:
                result = self._interactive_search_iteration()
                if result == self._SEARCH_RESULT_SERACH_ENDED:
                    self._mode = self._MODE_NAVIGATION
                else:
                    treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                                        max_nr_lines, self._search_pattern, self._tree_header,
                                        show_search_pattern_if_empty=True,
                                        is_search_patterh_being_edited=True)
            elif self._mode == self._MODE_QUIT:
                break
            else:
                raise ValueError(self._mode)

    def _search(self):
        result = self._scan_char_in_interactive_search()
        if result == self._SEARCH_RESULT_SERACH_ENDED:
            self._tree = treelib.Tree(self._original_tree, deep=True)
            if self._search_pattern:
                self._scan_nodes_that_match_search_pattern()
                self._filter_nodes_that_match()
            self._selected_node = self._tree.get_node(self._selected_node.identifier)
            if self._selected_node is None:
                self._selected_node = self._tree.get_node(self._tree.root)
                assert self._selected_node is not None
            self._sorted_children_by_nid_cache = dict()
        return result

    def _scan_nodes_that_match_search_pattern(self):
        self._nodes_that_match_search_filter = {self._tree.root: True}
        for nid, node in self._tree.nodes.iteritems():
            node_data = node.tag if node.data is None else str(node.data)
            if re.findall(self._search_pattern, node_data):
                for ancestor_nid in self._tree.rsearch(nid):
                    self._nodes_that_match_search_filter[ancestor_nid] = True

    def _filter_nodes_that_match(self):
        while True:
            for nid, node in self._tree.nodes.iteritems():
                if nid not in self._nodes_that_match_search_filter:
                    self._tree.remove_node(node.identifier)
                    break
            else:
                break

    def _navigate(self, max_nr_lines, min_nr_options, max_nr_options, including_root):
        if self._print_tree_once:
            treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                                   max_nr_lines, self._search_pattern, self._tree_header)
        self._print_tree_once = True
        option = self._scan_search_key()
        if option == self._OPTION_NEXT:
            success = self._move_selection_relative(distance=1)
            self._print_tree_once = success
        elif option == self._OPTION_PREV:
            success = self._move_selection_relative(distance=-1)
            self._print_tree_once = success
        elif option == self._OPTION_MOVE_TO_FIRST_SIBLING:
            self._move_selection_absolute(0)
        elif option == self._OPTION_MOVE_TO_LAST_SIBLING:
            self._move_selection_absolute(-1)
        elif option == self._OPTION_PAGE_UP:
            success = self._move_selection_relative(distance=-4)
            self._print_tree_once = success
        elif option == self._OPTION_PAGE_DOWN:
            success = self._move_selection_relative(distance=4)
            self._print_tree_once = success
        elif option == self._OPTION_TOGGLE:
            if not (min_nr_options == max_nr_options == 1):
                self._toggle()
        elif option == self._OPTION_UP:
            result = self._go_up(including_root=including_root)
            if not result:
                self._print_tree_once = False
        elif option == self._OPTION_EXPLORE:
            result = False
            if max_nr_options > 1:
                result = self._explore()
            if not result:
                self._print_tree_once = False
        elif option == self._OPTION_RETURN:
            if min_nr_options == max_nr_options == 1:
                return [self._selected_node.data]
            if len(self._picked) <= max_nr_options and \
                    len(self._picked) >= min_nr_options:
                return self._picked.values()
        elif option == self._OPTION_QUIT:
            self._mode = self._MODE_QUIT
        elif option == self._OPTION_MOVE_TO_SEARCH_MODE:
            if self._mode == self._MODE_NAVIGATION:
                self._mode = self._MODE_SEARCH
                self._search_pattern = ""
                treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                                    max_nr_lines, self._search_pattern, self._tree_header,
                                    show_search_pattern_if_empty=True,
                                    is_search_patterh_being_edited=True)
        elif option == self._OPTION_MOVE_TO_INTERACTIVE_SEARCH_MODE:
            self._mode = self._MODE_INTERACTIVE_SEARCH
            self._search_pattern = ""
            treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                                   max_nr_lines, self._search_pattern, self._tree_header,
                                   show_search_pattern_if_empty=True,
                                   is_search_patterh_being_edited=True)
        else:
            assert False, option
        return None

    def _interactive_search_iteration(self):
        result = self._scan_char_in_interactive_search()
        if result == self._SEARCH_RESULT_SERACH_ENDED:
            if not self._search_pattern:
                self._tree = treelib.Tree(self._original_tree, deep=True)
        elif result == self._SERACH_RESULT_SERACH_CONTINUES:
            self._tree = treelib.Tree(self._original_tree, deep=True)
            self._scan_nodes_that_match_search_pattern()
            self._filter_nodes_that_match()
            result = self._SERACH_RESULT_SERACH_CONTINUES
        else:
            assert False, result
        self._selected_node = self._tree.get_node(self._selected_node.identifier)
        if self._selected_node is None:
            self._selected_node = self._tree.get_node(self._tree.root)
            assert self._selected_node is not None
        self._sorted_children_by_nid_cache = dict()
        return result

    def _sorted_children(self, node):
        nid = node.identifier
        if nid not in self._sorted_children_by_nid_cache:
            self._sorted_children_by_nid_cache[nid] = sorted(self._tree.children(nid))
        return self._sorted_children_by_nid_cache[nid]

    def _get_siblings(self):
        if self._selected_node.identifier == self._tree.root:
            return [self._tree.get_node(self._tree.root)]
        parent = self._tree.get_node(self._selected_node.bpointer)
        return self._sorted_children(parent)

    def _move_selection_relative(self, distance):
        if self._selected_node.identifier != self._tree.root:
            siblings = self._get_siblings()
            wanted_index = siblings.index(self._selected_node) + distance
            if wanted_index >= 0 and wanted_index < len(siblings):
                self._selected_node = siblings[wanted_index]
                return True
            elif wanted_index < 0:
                self._selected_node = siblings[0]
                return True
            elif wanted_index >= len(siblings):
                self._selected_node = siblings[-1]
                return True
        return False

    def _move_selection_absolute(self, index):
        siblings = self._get_siblings()
        self._selected_node = siblings[index]

    def _explore(self):
        if self._tree.children(self._selected_node.identifier):
            self._selected_node = self._sorted_children(self._selected_node)[0]
            return True
        return False

    def _go_up(self, including_root=False):
        if self._selected_node.identifier != self._tree.root:
            if not including_root and \
                    self._tree.get_node(self._selected_node.identifier) in \
                    self._tree.children(self._tree.root):
                return False
            self._selected_node = self._tree.get_node(self._selected_node.bpointer)
            return True
        return False

    def _scan_search_key(self):
        key_to_option = {'j': self._OPTION_NEXT,
                         'k': self._OPTION_PREV,
                         'l': self._OPTION_EXPLORE,
                         'h': self._OPTION_UP,
                         'q': self._OPTION_QUIT,
                         'G': self._OPTION_MOVE_TO_LAST_SIBLING,
                         'g': self._OPTION_MOVE_TO_FIRST_SIBLING,
                         chr(3): self._OPTION_QUIT,
                         '/': self._OPTION_MOVE_TO_SEARCH_MODE,
                         chr(16): self._OPTION_MOVE_TO_INTERACTIVE_SEARCH_MODE,
                         chr(13): self._OPTION_RETURN,
                         chr(32): self._OPTION_TOGGLE,
                         chr(4): self._OPTION_PAGE_DOWN,
                         chr(21): self._OPTION_PAGE_UP,
                         'u': self._OPTION_PAGE_UP,
                         'd': self._OPTION_PAGE_DOWN
                         }
        key = None
        while key not in key_to_option:
            key = getcher.GetchUnix()()
        return key_to_option[key]

    def _scan_char_in_interactive_search(self):
        key = getcher.GetchUnix()()
        result = self._SERACH_RESULT_SERACH_CONTINUES
        if key == chr(13):
            key = None
            result = self._SEARCH_RESULT_SERACH_ENDED
        elif key == chr(127):
            if self._search_pattern:
                self._search_pattern = self._search_pattern[:-1]
        elif ord(key) in (8, 21, 23):
            self._search_pattern = ""
        elif key == chr(3):
            self._search_pattern = ""
            result = self._SEARCH_RESULT_SERACH_ENDED
        else:
            self._search_pattern += key
        return result

    def _toggle(self):
        if self._selected_node.identifier in self._picked:
            del self._picked[self._selected_node.identifier]
            for nid, node in self._tree.subtree(self._selected_node.identifier).nodes.iteritems():
                if node.identifier in self._picked:
                    del self._picked[nid]
        else:
            self._picked[self._selected_node.identifier] = \
                    self._tree.get_node(self._selected_node.identifier).data
            for nid, node in self._tree.subtree(self._selected_node.identifier).nodes.iteritems():
                if node.identifier not in self._picked:
                    self._picked[nid] = self._tree.get_node(nid).data


if __name__ == '__main__':
    import treelib
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

    treepicker = TreePicker(thetree)

    import os
    if os.getenv('MODE') == 'interactive':
        printer.wrapper(treepicker.pick, max_nr_lines=25)
    else:
        print treepicker.pick(max_nr_lines=25)
