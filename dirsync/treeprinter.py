import printer
import treeops
import pagination


_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"


class TreePrinter(object):
    DEFAULT_MAX_NR_LINES = 25
    MAX_ALLOWED_NR_LINES = 100

    _DATA_THAT_WILL_APPEAR_FIRST = chr(0)
    _DATA_THAT_WILL_APPEAR_LAST = chr(127)

    def __init__(self, tree, max_nr_lines=None, including_root=True):
        self._tree = tree
        self._tree_lines = None
        self._selected_node = None
        self._node_shown_as_selected = None
        self._picked_nodes = None
        self._max_nr_lines = self.DEFAULT_MAX_NR_LINES if max_nr_lines is None else max_nr_lines
        if self._max_nr_lines > self.MAX_ALLOWED_NR_LINES:
            self._max_nr_lines = self.DEFAULT_MAX_NR_LINES
        self._nodes_by_depth_cache = None
        self._root = None
        self._max_allowed_depth = None
        self._search_pattern = ""
        self._including_root = including_root

    def calculate_lines_to_print(self, selected_node_id, picked_nodes, search_pattern):
        self._selected_node = self._tree.get_node(selected_node_id)
        self._node_shown_as_selected = self._tree.get_node(selected_node_id)
        self._search_pattern = search_pattern
        self._picked_nodes = picked_nodes
        self._prepare_tree_for_printing()
        self._tree_lines = list(self._get_tree_lines())

    def print_tree(self, print_info_line=True):
        for line, color, is_bold in self._tree_lines:
            printer.print_string(line, color, is_bold)
        if print_info_line:
            self._print_info_lines()

    def _get_tree_lines(self):
        tree = self._tree
        depth = 0
        max_depth = depth
        is_last_child = True
        dfs_stack = [(tree.get_node(self._root), depth, is_last_child)]
        lines = []
        siblings_of_selected = None
        children_of_root = None
        while dfs_stack:
            node, depth, is_last_child = dfs_stack.pop()
            max_depth = max(depth, max_depth)
            lines.append((node, depth, is_last_child))
            if depth < self._max_allowed_depth:
                children = self._children(tree, node.identifier)
                if node.identifier == self._tree.root:
                    children_of_root = children
                if node.identifier == self._node_shown_as_selected.bpointer:
                    siblings_of_selected = children
                if children:
                    children.sort(self._compare_nodes)
                    dfs_stack.append((children[0], depth + 1, True))
                    dfs_stack.extend([(child, depth + 1, False) for child in children[1:]])
        does_parent_in_height_n_has_more_nodes = [False] * (max_depth + 1)
        if siblings_of_selected is None:
            siblings_of_selected = self._get_siblings_of_node(tree, self._node_shown_as_selected)
            siblings_of_selected.sort(self._compare_nodes)
        siblings_of_selected.reverse()
        index_of_selected = siblings_of_selected.index(self._node_shown_as_selected)
        nr_items_to_remove_at_beginning, nr_items_to_remove_at_end = (
                pagination.paginate(len(siblings_of_selected), index_of_selected, self._max_nr_lines))
        index_in_siblings_of_selected = 0
        for node, depth, is_last_child in lines:
            if not self._including_root and node.identifier == self._tree.root:
                continue
            if node.identifier == self._node_shown_as_selected.identifier:
                color = "blue" if node.identifier in self._picked_nodes else "green"
            elif node.identifier in self._picked_nodes:
                color = "red"
            else:
                color = None
            pre_line = ">" if node.identifier == self._node_shown_as_selected.identifier else " "
            pre_line += " "
            pre_line += "X" if node.identifier in self._picked_nodes else " "
            if hasattr(node, 'original_matching') and node.original_matching and self._search_pattern:
                if color is None:
                    color = "yellow"
                pre_line += "~"
            else:
                pre_line += " "
            does_parent_in_height_n_has_more_nodes[depth] = not is_last_child
            lower_depth_marks = ""
            current_depth_marks = ""
            if node.identifier != self._root:
                for lower_depth in xrange(1, depth):
                    if does_parent_in_height_n_has_more_nodes[lower_depth]:
                        lower_depth_marks += "\xe2\x94\x82   "
                    else:
                        lower_depth_marks += "    "
                if is_last_child:
                    current_depth_marks += '\xe2\x94\x94'
                else:
                    if not self._including_root and node == children_of_root[0]:
                        current_depth_marks += '\xe2\x94\x8c'
                    else:
                        current_depth_marks += '\xe2\x94\x9c'
                current_depth_marks += '\xe2\x94\x80' * 2
                current_depth_marks += " "
            prefix = pre_line + lower_depth_marks + current_depth_marks
            if isinstance(node.tag, str):
                node_lines = [[node_line, color, False] for node_line in node.tag.splitlines()]
            else:
                node_lines = [[node_line[0],
                               color if node_line[1] is None else node_line[1],
                               node_line[2]]
                              for node_line in node.tag]
            node_lines[0][0] = prefix + node_lines[0][0]
            non_first_lines_addition = ' ' * len(pre_line) + lower_depth_marks
            if is_last_child:
                non_first_lines_addition += '   '
            else:
                non_first_lines_addition += '\xe2\x94\x82' + '  '
            for index in xrange(1, len(node_lines)):
                node_lines[index][0] = non_first_lines_addition + node_lines[index][0]
            if node.bpointer == self._node_shown_as_selected.bpointer:
                index_in_siblings_of_selected += 1
                if nr_items_to_remove_at_beginning and index_in_siblings_of_selected == 1:
                    tag = prefix + "... (%d more)" % (nr_items_to_remove_at_beginning)
                    yield tag, None, False
                    continue
                elif index_in_siblings_of_selected <= nr_items_to_remove_at_beginning:
                    continue
                elif (nr_items_to_remove_at_end and
                      index_in_siblings_of_selected == len(siblings_of_selected)):
                    tag = prefix + "... (%d more)" % (nr_items_to_remove_at_end)
                    yield tag, None, False
                    continue
                elif index_in_siblings_of_selected > len(siblings_of_selected) - nr_items_to_remove_at_end:
                    continue
            if self._children(tree, node.identifier) and depth == self._max_allowed_depth:
                node_lines[-1][0] += " (...)"
            if depth == max_depth:
                lines_to_print = node_lines
            else:
                lines_to_print = [node_lines[0]]
            for line, color, is_bold in lines_to_print:
                yield line, color, is_bold

    def _children(self, tree, nid):
        return [node for node in tree.children(nid) if
                (hasattr(node, 'matching') and node.matching) or
                not hasattr(node, 'matching')]

    def _get_siblings_of_node(self, tree, node):
        if node.identifier == tree.root:
            result = [tree.get_node(tree.root)]
        else:
            result = list(self._children(tree, node.bpointer))
        if node not in result:
            result.append(node)
        return result

    def _print_info_lines(self):
        if self._selected_node is None:
            header = "No node selected"
        else:
            label = self._selected_node.tag if self._selected_node.data is None else self._selected_node.data
            header = "Current: %s, %d items selected" % (label, len(self._picked_nodes))
        printer.print_string(header)

    def _prepare_tree_for_printing(self):
        # Find root node from which to print tree
        is_selected_node_in_filter = (self._selected_node is not None and
                                      (not hasattr(self._selected_node, 'matching') or
                                       self._selected_node.matching))
        if self._selected_node is None:
            self._root = self._tree.root
        elif self._selected_node.identifier == self._tree.root:
            self._root = self._tree.root
        elif is_selected_node_in_filter:
            self._root = self._selected_node.bpointer
        else:
            self._root = self._tree.root
        if is_selected_node_in_filter:
            self._node_shown_as_selected = self._selected_node
        else:
            self._node_shown_as_selected = self._tree.get_node(self._root)
        min_depth = self._tree.depth(self._node_shown_as_selected)

        self._max_allowed_depth, node_counter = treeops.get_max_possible_depth(self._tree,
                                                                               self._root,
                                                                               self._max_nr_lines,
                                                                               min_depth=min_depth)
        candidate_root = self._root
        candidate_depth = self._max_allowed_depth
        while node_counter <= self._max_nr_lines:
            self._root = candidate_root
            self._max_allowed_depth = candidate_depth
            candidate_root = self._tree.get_node(self._root).bpointer
            if candidate_root is None:
                break
            candidate_depth, node_counter = treeops.get_max_possible_depth(self._tree,
                                                                           candidate_root,
                                                                           self._max_nr_lines,
                                                                           min_depth=min_depth)

    @staticmethod
    def _node_key(node):
        return str(node.data)

    @classmethod
    def _compare_nodes(cls, node_a, node_b):
        return 1 if cls._node_key(node_a) < cls._node_key(node_b) else -1


if __name__ == '__main__':
    from exampletree import tree
    treeprinter = TreePrinter(tree)
    treeprinter.calculate_lines_to_print(selected_node_id='grandson7',
                                         picked_nodes=['childnode4', 'grandson5'])
    treeprinter.print_tree()
