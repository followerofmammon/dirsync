import os
import treelib

import keybind
import printer
import treesearch
import linescanner
import treenavigator
import treepicker_keybindings as keybindings
import treepicker_shelloutput as shelloutput


class TreePicker(object):
    _MODE_NAVIGATION = 'navigation'
    _MODE_SEARCH = 'search'
    _MODE_INTERACTIVE_SEARCH = 'interactive search'
    _MODE_RETURN = 'return'
    _MODE_QUIT = 'quit'

    def __init__(self, tree, including_root=True, header=None, max_nr_lines=None,
                 min_nr_options=1, max_nr_options=None):
        self._tree = tree
        self._min_nr_options = min_nr_options
        self._max_nr_options = len(self._tree) if max_nr_options is None else max_nr_options
        self._picked = dict()
        self._mode = self._MODE_NAVIGATION
        self._header = header
        self._tree_search = treesearch.TreeSearch(self._tree)
        self._line_scanner = linescanner.LineScanner()
        self._navigation_actions = keybind.KeyBind()
        self._tree_navigator = treenavigator.TreeNavigator(self._tree, including_root)
        keybindings.populate_bindings(self._navigation_actions)
        keybindings.register_actions(self._navigation_actions, self, self._tree_navigator)
        self._shelloutput = shelloutput.TreePickerShellOutput(self._tree, self._header, max_nr_lines)
        self._were_search_results_changed_since_navigation = False

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
                if self._were_search_results_changed_since_navigation:
                    self._were_search_results_changed_since_navigation = False
                    self._set_tree_for_navigation()
                previous_state = self._capture_state()
                self._navigation_actions.do_one_action()
                current_state = self._capture_state()
                print_tree_once = previous_state != current_state
            elif self._mode == self._MODE_SEARCH:
                result = self._line_scanner.scan_char()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._mode = self._MODE_NAVIGATION
                    self._set_tree_for_navigation()
                    self._mark_matching_tree_nodes()
            elif self._mode == self._MODE_INTERACTIVE_SEARCH:
                result = self._line_scanner.scan_char()
                self._mark_matching_tree_nodes()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._mode = self._MODE_NAVIGATION
                    self._set_tree_for_navigation()
                    self._tree_navigator.select_first_match()
            elif self._mode == self._MODE_RETURN:
                picked = self._picked.values()
            elif self._mode == self._MODE_QUIT:
                picked = list()
            else:
                raise ValueError(self._mode)
        return [node.data for node in picked]

    def _set_tree_for_navigation(self):
        tree = treelib.Tree()
        root_node = self._tree.get_node(self._tree.root)
        bfs_queue = [root_node]
        while bfs_queue:
            node = bfs_queue.pop(0)
            if not hasattr(node, 'matching'):
                node.matching = True
            if node == root_node or node.matching:
                new_node = tree.create_node(identifier=node.identifier, tag=node.tag, data=node.data,
                                            parent=node.bpointer)
                new_node.matching = node.matching
                new_node.original_matching = node.original_matching
            bfs_queue.extend(self._tree.children(node.identifier))
        self._tree_navigator.set_tree(tree)

    def start_search(self):
        self._mode = self._MODE_SEARCH

        # Reset tree search results
        self._line_scanner.clear_line()
        self._mark_matching_tree_nodes()

        self._set_tree_for_navigation()

    def start_interactive_search(self):
        self._mode = self._MODE_INTERACTIVE_SEARCH

        # Reset tree search results
        self._line_scanner.clear_line()
        self._mark_matching_tree_nodes()

        self._set_tree_for_navigation()

    def quit(self):
        self._mode = self._MODE_QUIT

    def toggle(self):
        selected_node_nid = self._tree_navigator.get_selected_node()
        selected_node = self._tree.get_node(selected_node_nid)
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
            selected_node_nid = self._tree_navigator.get_selected_node()
            self._picked = {selected_node_nid: self._tree.get_node(selected_node_nid)}
            self._mode = self._MODE_RETURN
        elif self._min_nr_options <= len(self._picked) <= self._max_nr_options:
            self._mode = self._MODE_RETURN

    def _print_tree(self):
        search_pattern = self._line_scanner.get_line()
        self._shelloutput.print_tree(self._tree_navigator.get_selected_node(), search_pattern, self._picked,
                                     self._mode)

    def _capture_state(self):
        picked = hash(str(self._picked.keys()))
        return (picked, self._tree_navigator.get_selected_node(), self._mode)

    def _mark_matching_tree_nodes(self):
        search_pattern = self._line_scanner.get_line()
        self._tree_search.get_filtered_tree(search_pattern)
        self._were_search_results_changed_since_navigation = True

    def _pick_node(self, node):
        self._picked[node.identifier] = node

    def _unpick_node(self, node):
        if node.identifier in self._picked:
            del self._picked[node.identifier]


if __name__ == '__main__':
    from exampletree import tree
    treepicker = TreePicker(tree, header='stuff:', max_nr_lines=25)
    if os.getenv('MODE') == 'static':
        printer.wrapper(treepicker.pick)
    else:
        print treepicker.pick()
