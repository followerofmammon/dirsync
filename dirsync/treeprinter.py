import printer
import treeops
import pagination


_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"


class TreePrinter(object):
    DEFAULT_MAX_NR_LINES = 25
    MAX_ALLOWED_NR_LINES = 100

    _DATA_THAT_WILL_APPEAR_FIRST = chr(0)
    _DATA_THAT_WILL_APPEAR_LAST = chr(127)

    def __init__(self, tree, max_nr_lines=None):
        self._tree = tree
        self._tree_lines = None
        self._selected_node = None
        self._picked_nodes = None
        self._max_nr_lines = self.DEFAULT_MAX_NR_LINES if max_nr_lines is None else max_nr_lines
        if self._max_nr_lines > self.MAX_ALLOWED_NR_LINES:
            self._max_nr_lines = self.DEFAULT_MAX_NR_LINES
        self._nodes_by_depth_cache = None
        self._root = None
        self._max_allowed_depth = None
        self._search_pattern = ""

    def calculate_lines_to_print(self, selected_node_id, picked_nodes, search_pattern):
        self._selected_node = self._tree.get_node(selected_node_id)
        self._search_pattern = search_pattern
        self._picked_nodes = picked_nodes
        self._prepare_tree_for_printing()
        self._tree_lines = list(self._get_tree_lines())

    def print_tree(self):
        for line, color in self._tree_lines:
            printer.print_string(line, color)
        self._print_info_lines()

    def _get_tree_lines(self):
        tree = self._tree
        depth = 0
        max_depth = depth
        is_last_child = True
        dfs_stack = [(tree.get_node(self._root), depth, is_last_child)]
        lines = []
        siblings_of_selected = None
        while dfs_stack:
            node, depth, is_last_child = dfs_stack.pop()
            max_depth = max(depth, max_depth)
            lines.append((node, depth, is_last_child))
            if depth < self._max_allowed_depth:
                children = self._children(tree, node.identifier)
                if node.identifier == self._selected_node.bpointer:
                    siblings_of_selected = children
                if children:
                    children.sort(self._compare_nodes)
                    dfs_stack.append((children[0], depth + 1, True))
                    dfs_stack.extend([(child, depth + 1, False) for child in children[1:]])
        does_parent_in_height_n_has_more_nodes = [False] * (max_depth + 1)
        if siblings_of_selected is None:
            siblings_of_selected = self._get_siblings_of_node(tree, self._selected_node)
            siblings_of_selected.sort(self._compare_nodes)
        siblings_of_selected.reverse()
        index_of_selected = siblings_of_selected.index(self._selected_node)
        nr_items_to_remove_at_beginning, nr_items_to_remove_at_end = (
                pagination.paginate(len(siblings_of_selected), index_of_selected, self._max_nr_lines))
        index_in_siblings_of_selected = 0
        for node, depth, is_last_child in lines:
            if node.identifier == self._selected_node.identifier:
                color = "blue" if node.identifier in self._picked_nodes else "green"
            elif node.identifier in self._picked_nodes:
                color = "red"
            else:
                color = None
            pre_line = ">" if node.identifier == self._selected_node.identifier else " "
            pre_line += " "
            pre_line += "X" if node.identifier in self._picked_nodes else " "
            if hasattr(node, 'original_matching') and node.original_matching and self._search_pattern:
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
                    current_depth_marks += '\xe2\x94\x9c'
                current_depth_marks += '\xe2\x94\x80' * 2
                current_depth_marks += " "
            prefix = pre_line + lower_depth_marks + current_depth_marks
            lines = node.tag.splitlines()
            lines[0] = prefix + lines[0]
            non_first_lines_addition = ' ' * len(pre_line) + lower_depth_marks
            if is_last_child:
                non_first_lines_addition += '   '
            else:
                non_first_lines_addition += '\xe2\x94\x82' + '  '
            for index in xrange(1, len(lines)):
                lines[index] = non_first_lines_addition + lines[index]
            if lines[1:]:
                import pdb
                # pdb.set_trace()
            if node.bpointer == self._selected_node.bpointer:
                index_in_siblings_of_selected += 1
                if nr_items_to_remove_at_beginning and index_in_siblings_of_selected == 1:
                    tag = prefix + "... (%d more)" % (nr_items_to_remove_at_beginning)
                    yield tag, None
                elif index_in_siblings_of_selected <= nr_items_to_remove_at_beginning:
                    continue
                elif (nr_items_to_remove_at_end and
                      index_in_siblings_of_selected == len(siblings_of_selected)):
                    tag = prefix + "... (%d more)" % (nr_items_to_remove_at_end)
                    yield tag, None
                elif index_in_siblings_of_selected > len(siblings_of_selected) - nr_items_to_remove_at_end:
                    continue
            if self._children(tree, node.identifier) and depth == self._max_allowed_depth:
                lines[-1] += " (...)"
            for line in lines:
                yield line, color

    def _children(self, tree, nid):
        return [node for node in tree.children(nid) if
                (hasattr(node, 'matching') and node.matching) or
                not hasattr(node, 'matching')]

    def _get_siblings_of_node(self, tree, node):
        if node.identifier == tree.root:
            return [tree.get_node(tree.root)]
        return self._children(tree, node.bpointer)

    def _print_info_lines(self):
        label = self._selected_node.tag if self._selected_node.data is None else self._selected_node.data
        header = "Current: %s, %d items selected" % (label, len(self._picked_nodes))
        printer.print_string(header)

    def _prepare_tree_for_printing(self):
        # Find root node from which to print tree
        if self._selected_node.identifier == self._tree.root:
            self._root = self._tree.root
        else:
            self._root = self._selected_node.bpointer
        min_depth = self._tree.depth(self._selected_node)
        self._max_allowed_depth = treeops.get_max_possible_depth(self._tree,
                                                                 self._root,
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
