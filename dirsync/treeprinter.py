import treelib
import binascii

import printer
import treeops
import pagination
import treelib_printwrapper


_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"


class TreePrinter(object):
    DEFAULT_MAX_NR_LINES = 25
    MAX_ALLOWED_NR_LINES = 100

    _DATA_THAT_WILL_APPEAR_FIRST = chr(0)
    _DATA_THAT_WILL_APPEAR_LAST = chr(127)

    def __init__(self, tree, max_nr_lines=None):
        self.set_tree(tree)
        self._tree_lines = None
        self._selected_node = None
        self._picked_nodes = None
        self._max_nr_lines = len(tree.nodes) if max_nr_lines is None else self.DEFAULT_MAX_NR_LINES
        if self._max_nr_lines > self.MAX_ALLOWED_NR_LINES:
            self._max_nr_lines = self.DEFAULT_MAX_NR_LINES
        self._nodes_by_depth_cache = None

    def set_tree(self, tree):
        self._tree = tree

    def calculate_lines_to_print(self, selected_node, picked_nodes):
        self._selected_node = selected_node
        self._picked_nodes = picked_nodes
        self._tree_lines = list(self._get_tree_lines())

    def print_tree(self):
        for line, color in self._tree_lines:
            printer.print_string(line, color)
        self._print_info_lines()

    def _get_tree_lines(self, max_allowed_depth=20):
        tree = self._prepare_tree_for_printing()
        depth = 0
        max_depth = depth
        is_last_child = True
        bfs_stack = [(tree.get_node(tree.root), depth, is_last_child)]
        lines = []
        while bfs_stack:
            node, depth, is_last_child = bfs_stack.pop()
            max_depth = max(depth, max_depth)
            lines.append((node, depth, is_last_child))
            if depth < max_allowed_depth:
                children = tree.children(node.identifier)
                if children:
                    children.sort(self._compare_nodes)
                    bfs_stack.append((children[0], depth + 1, True))
                    bfs_stack.extend([(child, depth + 1, False) for child in children[1:]])
        does_parent_in_height_n_has_more_nodes = [False] * (max_depth + 1)
        for node, depth, is_last_child in lines:
            if node.identifier == self._selected_node.identifier:
                color = "blue" if node.identifier in self._picked_nodes else "green"
            elif node.identifier in self._picked_nodes:
                color = "red"
            else:
                color = None
            prefix = ">" if node.identifier == self._selected_node.identifier else " "
            prefix += " "
            prefix += "X" if node.identifier in self._picked_nodes else " "
            does_parent_in_height_n_has_more_nodes[depth] = not is_last_child
            line = ""
            if node.identifier != tree.root:
                for lower_depth in xrange(1, depth):
                    if does_parent_in_height_n_has_more_nodes[lower_depth]:
                        prefix += "\xe2\x94\x82   "
                    else:
                        prefix += "    "
                if is_last_child:
                    prefix += '\xe2\x94\x94'
                else:
                    prefix += '\xe2\x94\x9c'
                prefix += '\xe2\x94\x80' * 2
                prefix += " "
            line += prefix
            line += node.tag
            if not node.identifier.startswith("__UNLIKELY_IDENTIFIER__"):
                if not tree.children(node.identifier) and self._tree.children(node.identifier):
                    line += " (...)"
            yield line, color

    def _print_info_lines(self):
        label = self._selected_node.tag if self._selected_node.data is None else self._selected_node.data
        header = "Current: %s, %d items selected" % (label, len(self._picked_nodes))
        printer.print_string(header)

    def _prepare_tree_for_printing(self):
        # Find root node from which to print tree
        if self._selected_node.identifier == self._tree.root:
            tree = self._tree
        else:
            parent_nid = self._selected_node.bpointer
            tree = self._tree.subtree(parent_nid)

        max_depth, nodes_by_depth = treeops.get_max_possible_depth(tree, self._max_nr_lines,
                                                                   min_depth=tree.depth(self._selected_node))

        # Paginate siblings of selected node
        _tree = treelib.Tree()
        root = tree.get_node(tree.root)
        _tree.create_node(identifier=root.identifier, tag=root.tag, data=root.data)
        for depth in xrange(1, max_depth + 1):
            nodes = nodes_by_depth[depth]
            nonsiblings = [node for node in nodes if node.bpointer != self._selected_node.bpointer]
            for node in nonsiblings:
                _tree.create_node(identifier=node.identifier, tag=node.tag, data=node.data,
                                  parent=node.bpointer)

            siblings = [node for node in nodes if node.bpointer == self._selected_node.bpointer]
            self._populate_siblings_with_pagination(_tree, siblings)
        return _tree

    def _populate_siblings_with_pagination(self, tree, siblings):
        if len(siblings) > self._max_nr_lines:
            siblings.sort(self._compare_nodes)
            siblings, nr_nodes_removed_at_beginning, nr_nodes_removed_at_end = \
                pagination.paginate(siblings, self._selected_node, self._max_nr_lines)
            if nr_nodes_removed_at_beginning:
                tag = "... (%d more)" % (nr_nodes_removed_at_beginning)
                tree.create_node(identifier='__UNLIKELY_IDENTIFIER__BEFORE', tag=tag,
                                 data=self._DATA_THAT_WILL_APPEAR_FIRST,
                                 parent=self._selected_node.bpointer)
            if nr_nodes_removed_at_end:
                tag = "... (%d more)" % (nr_nodes_removed_at_end)
                tree.create_node(identifier='__UNLIKELY_IDENTIFIER__AFTER', tag=tag,
                                 data=self._DATA_THAT_WILL_APPEAR_LAST,
                                 parent=self._selected_node.bpointer)
        for node in siblings:
            tree.create_node(identifier=node.identifier, tag=node.tag, data=node.data, parent=node.bpointer)

    @staticmethod
    def _node_key(node):
        return str(node.data)

    @classmethod
    def _compare_nodes(cls, node_a, node_b):
        return 1 if cls._node_key(node_a) < cls._node_key(node_b) else -1


if __name__ == '__main__':
    from exampletree import tree
    treeprinter = TreePrinter(tree)
    treeprinter.calculate_lines_to_print(selected_node=tree.nodes['grandson7'],
                                         picked_nodes=['childnode4', 'grandson5'])
    treeprinter.print_tree()
