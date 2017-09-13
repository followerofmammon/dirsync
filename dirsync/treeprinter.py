import treelib
import binascii

import printer
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

    def _get_tree_lines(self):
        tree = self._prepare_tree_for_printing()
        self._add_id_to_end_of_tags_in_all_nodes(tree)
        lines = treelib_printwrapper.get_tree_output(tree, key=self._node_key).splitlines()
        for line_index, line in enumerate(lines):
            tag, nid = self._decode_encoded_tree_line(line)
            encoded_tag_index = line.index(_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
            line = line[:encoded_tag_index] + tag
            if not nid.startswith("__UNLIKELY_IDENTIFIER__"):
                if not tree.children(nid) and self._tree.children(nid):
                    line += " (...)"
            prefix = ">" if nid == self._selected_node.identifier else " "
            prefix += " "
            prefix += "X" if nid in self._picked_nodes else " "
            line = "%s %s" % (prefix, line)
            if nid == self._selected_node.identifier:
                color = "blue" if nid in self._picked_nodes else "green"
            elif nid in self._picked_nodes:
                color = "red"
            else:
                color = None
            yield line, color

    def _print_info_lines(self):
        label = self._selected_node.tag if self._selected_node.data is None else self._selected_node.data
        header = "Current: %s, %d items selected" % (label, len(self._picked_nodes))
        printer.print_string(header)

    def _get_max_possible_depth(self, tree):
        node_counter = 0
        bfs_queue = [(tree.get_node(tree.root), 0)]
        self._nodes_by_depth_cache = dict()
        max_depth = -1
        depth = 0
        selected_node_depth = tree.depth(self._selected_node.identifier)
        while bfs_queue:
            node, depth = bfs_queue.pop(0)
            if depth - 1 > max_depth and node_counter <= self._max_nr_lines:
                max_depth = depth - 1
            node_counter += 1
            if depth < selected_node_depth or node_counter < self._max_nr_lines:
                for child in tree.children(node.identifier):
                    bfs_queue.append((child, depth + 1))
            self._nodes_by_depth_cache.setdefault(depth, list()).append(node)
        if node_counter <= self._max_nr_lines and depth > max_depth:
            max_depth = depth
        return max(max_depth, selected_node_depth)

    def _prepare_tree_for_printing(self):
        # Find root node from which to print tree
        if self._selected_node.identifier == self._tree.root:
            tree = self._tree
        else:
            parent_nid = self._selected_node.bpointer
            tree = self._tree.subtree(parent_nid)
        root_nid = tree.root

        # Decrease the level of printing until reaching limit of #lines
        max_depth = self._get_max_possible_depth(tree)

        # Paginate siblings of selected node
        _tree = treelib.Tree()
        root = tree.get_node(root_nid)
        _tree.create_node(identifier=root.identifier, tag=root.tag, data=root.data)
        for depth in xrange(1, max_depth + 1):
            nodes = self._nodes_by_depth_cache[depth]
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
        return 1 if cls._node_key(node_a) > cls._node_key(node_b) else -1

    @staticmethod
    def _add_id_to_end_of_tags_in_all_nodes(tree):
        for node in tree.nodes.values():
            node.tag = (_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + binascii.hexlify(node.tag) +
                        _UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + binascii.hexlify(node.identifier))

    @staticmethod
    def _decode_encoded_tree_line(tag):
        parts = tag.split(_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
        encoded_tag = binascii.unhexlify(parts[1])
        encoded_nid = binascii.unhexlify(parts[2])
        return encoded_tag, encoded_nid


if __name__ == '__main__':
    from exampletree import tree
    treeprinter = TreePrinter(tree)
    treeprinter.calculate_lines_to_print(selected_node=tree.nodes['grandson7'],
                                         picked_nodes=['childnode4', 'grandson5'])
    treeprinter.print_tree()
