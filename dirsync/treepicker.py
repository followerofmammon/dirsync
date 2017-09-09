import os
import treelib

import keybind
import printer
import treesearch
import linescanner
import treeprinter


class TreePicker(object):
    _MODE_NAVIGATION = 'navigation'
    _MODE_SEARCH = 'search'
    _MODE_INTERACTIVE_SEARCH = 'interactive search'
    _MODE_RETURN = 'return'
    _MODE_QUIT = 'quit'

    def __init__(self, tree, including_root=True, tree_header=None, max_nr_lines=25):
        self._original_tree = tree
        self._tree = treelib.Tree(self._original_tree, deep=True)
        self._min_nr_options = 0
        self._max_nr_options = len(self._tree)
        self._max_nr_lines = max_nr_lines
        self._including_root = including_root
        self._sorted_children_by_nid_cache = dict()
        self._selected_node = self._calculate_initial_node(self._including_root)
        self._picked = dict()
        self._mode = self._MODE_NAVIGATION
        self._nodes_that_match_search_filter = dict()
        self._tree_header = tree_header
        self._tree_search = treesearch.TreeSearch(self._tree)
        self._line_scanner = linescanner.LineScanner()
        self._navigation_actions = keybind.KeyBind()
        self._register_key_bindings()

    def pick_one(self):
        choices = self.pick(min_nr_options=1, max_nr_options=1)
        if not choices:
            return None
        return choices[0]

    def pick(self, min_nr_options=None, max_nr_options=None):
        if min_nr_options is not None:
            self._min_nr_options = min_nr_options
        if max_nr_options is not None:
            self._max_nr_options = max_nr_options
        print_tree_once = True
        picked = list()
        while self._mode != self._MODE_QUIT:
            is_search_pattern_being_edited = self._mode in (self._MODE_SEARCH,
                                                            self._MODE_INTERACTIVE_SEARCH)
            if print_tree_once:
                self._print_tree(is_search_pattern_being_edited=is_search_pattern_being_edited)
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
                break
            elif self._mode == self._MODE_QUIT:
                break
            else:
                raise ValueError(self._mode)
        return picked

    def _capture_state(self):
        picked = hash(str(self._picked.keys()))
        return (picked, self._selected_node.identifier, self._mode)

    def _start_search(self):
        self._mode = self._MODE_SEARCH
        self._line_scanner.clear_line()

    def _start_interactive_search(self):
        self._mode = self._MODE_INTERACTIVE_SEARCH
        self._line_scanner.clear_line()

    def _return_picked_nodes(self):
        if self._min_nr_options == self._max_nr_options == 1:
            self._picked = {self._selected_node.identifier: self._selected_node}
            self._mode = self._MODE_RETURN
        if self._min_nr_options <= len(self._picked) <= self._max_nr_options:
            self._mode = self._MODE_RETURN

    def _filter_tree_entries_by_search_pattern(self):
        search_pattern = self._line_scanner.get_line()
        if search_pattern:
            self._sorted_children_by_nid_cache = dict()
            self._tree = self._tree_search.get_filtered_tree(search_pattern)
        else:
            self._tree = treelib.Tree(self._original_tree, deep=True)
        self._selected_node = self._tree.get_node(self._selected_node.identifier)
        if self._selected_node is None:
            self._selected_node = self._tree.get_node(self._tree.root)

    def _print_tree(self, is_search_pattern_being_edited=False):
        treeprinter.print_tree(self._tree, self._selected_node, self._picked,
                               self._max_nr_lines, self._line_scanner.get_line(), self._tree_header,
                               show_search_pattern_if_empty=True)
        search_pattern = self._line_scanner.get_line()
        header = ""
        if is_search_pattern_being_edited:
            header = '\nInsert Search filter: %s <<--' % (search_pattern.strip(),)
            color = "magenta"
        elif search_pattern:
            header = '\nCurrent Search filter: %s' % (search_pattern.strip(),)
            color = "yellow"
        if header:
            printer.print_string(header, color)

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
        siblings = self._get_siblings()
        wanted_index = siblings.index(self._selected_node) + distance
        if wanted_index >= 0 and wanted_index < len(siblings):
            self._selected_node = siblings[wanted_index]
        elif wanted_index < 0:
            self._selected_node = siblings[0]
        elif wanted_index >= len(siblings):
            self._selected_node = siblings[-1]

    def _move_selection_absolute(self, index):
        siblings = self._get_siblings()
        self._selected_node = siblings[index]

    def _explore(self):
        children = self._sorted_children(self._selected_node)
        if children:
            self._selected_node = children[0]

    def _go_up(self):
        if self._selected_node.identifier != self._tree.root:
            if not self._including_root and self._selected_node.bpointer == self._tree.root:
                return
            self._selected_node = self._tree.get_node(self._selected_node.bpointer)

    def _quit(self):
        self._mode = self._MODE_QUIT

    def _register_key_bindings(self):
        self._navigation_actions.add_action('next', self._move_selection_relative, distance=1)
        self._navigation_actions.add_action('previous', self._move_selection_relative, distance=-1)
        self._navigation_actions.add_action('explore', self._explore)
        self._navigation_actions.add_action('up', self._go_up)
        self._navigation_actions.add_action('last_node', self._move_selection_absolute, index=-1)
        self._navigation_actions.add_action('first_node', self._move_selection_absolute, index=0)
        self._navigation_actions.add_action('quit', self._quit)
        self._navigation_actions.add_action('start_search', self._start_search)
        self._navigation_actions.add_action('start_interactive_search', self._start_interactive_search)
        self._navigation_actions.add_action('return_picked_nodes', self._return_picked_nodes)
        self._navigation_actions.add_action('toggle', self._toggle)
        self._navigation_actions.add_action('page_up', self._move_selection_relative, distance=-4)
        self._navigation_actions.add_action('page_down', self._move_selection_relative, distance=4)
        self._navigation_actions.bind('j', 'next')
        self._navigation_actions.bind('k', 'previous')
        self._navigation_actions.bind('l', 'explore')
        self._navigation_actions.bind('h', 'up')
        self._navigation_actions.bind('q', 'quit')
        self._navigation_actions.bind('G', 'last_node')
        self._navigation_actions.bind('g', 'first_node')
        self._navigation_actions.bind(chr(3), 'quit')  # Ctrl-C
        self._navigation_actions.bind('/', 'start_search')
        self._navigation_actions.bind(chr(16), 'start_interactive_search')  # Ctrl-P
        self._navigation_actions.bind(chr(13), 'return_picked_nodes')  # Return
        self._navigation_actions.bind(chr(32), 'toggle')  # Space
        self._navigation_actions.bind(chr(4), 'page_down')  # Ctrl-D
        self._navigation_actions.bind(chr(21), 'page_up')  # Ctrl-U
        self._navigation_actions.bind('u', 'page_up')
        self._navigation_actions.bind('d', 'page_down')

    def _toggle(self):
        if not (self._min_nr_options == self._max_nr_options == 1):
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

    def _calculate_initial_node(self, including_root):
        node = self._tree.get_node(self._tree.root)
        if not including_root:
            children = self._tree.children(self._tree.root)
            assert children, "Root must have children if including_root==False"
            node = self._sorted_children(node)[0]
        return node


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

    treepicker = TreePicker(thetree)

    if os.getenv('MODE') == 'static':
        printer.wrapper(treepicker.pick)
    else:
        print treepicker.pick()
