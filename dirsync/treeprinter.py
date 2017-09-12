import treelib
import binascii

import printer
import treelib_printwrapper


_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"


class TreePrinter(object):
    def __init__(self, tree):
        self.set_tree(tree)
        self._tree_lines = None
        self._selected_node = None
        self._picked_nodes = None
        self._max_nr_lines = None
        self._nodes_by_depth_cache = None

    def set_tree(self, tree):
        self._tree = tree

    def calculate_lines_to_print(self, selected_node, picked_nodes, max_nr_lines=25):
        self._selected_node = selected_node
        self._picked_nodes = picked_nodes
        self._tree_lines = list(self._get_tree_lines(max_nr_lines))

    def print_tree(self):
        for line, color in self._tree_lines:
            printer.print_string(line, color)
        self._print_info_lines()

    def _node_key(self, node):
        return str(node.data)

    def _get_tree_lines(self, max_nr_lines):
        if self._selected_node.identifier not in self._tree.nodes:
            self._selected_node = self._tree.get_node(self._tree.root)
        tree = self._prepare_tree_for_printing(max_nr_lines)
        self._add_id_to_end_of_tags_in_all_nodes(tree)
        lines = treelib_printwrapper.get_tree_output(tree, key=self._node_key).splitlines()
        for line_index, line in enumerate(lines):
            tag, nid = self._decode_encoded_tree_line(line)
            encoded_tag_index = line.index(_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
            line = line[:encoded_tag_index] + tag
            if not tree.children(nid) and self._tree.children(nid):
                line += " (...)"
            prefix = ""
            prefix += ">" if nid == self._selected_node.identifier else " "
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
        if self._selected_node.data is None:
            label = self._selected_node.tag
        else:
            label = self._selected_node.data
        header = "Current: %s, %d items selected" % (label, len(self._picked_nodes))
        printer.print_string(header)

    def _get_max_possible_depth(self, tree, max_nr_lines):
        node_counter = 0
        bfs_queue = [(tree.get_node(tree.root), 0)]
        self._nodes_by_depth_cache = dict()
        max_depth = -1
        depth = 0
        selected_node_depth = tree.depth(self._selected_node.identifier)
        while bfs_queue:
            node, depth = bfs_queue.pop(0)
            if depth - 1 > max_depth and node_counter <= max_nr_lines:
                max_depth = depth - 1
            node_counter += 1
            if depth < selected_node_depth or node_counter < max_nr_lines:
                for child in tree.children(node.identifier):
                    bfs_queue.append((child, depth + 1))
            self._nodes_by_depth_cache.setdefault(depth, list()).append(node)
        if node_counter <= max_nr_lines and depth > max_depth:
            max_depth = depth
        return max(max_depth, selected_node_depth)

    def _prepare_tree_for_printing(self, max_nr_lines):
        # Find root node from which to print tree
        root_nid = self._selected_node.identifier
        if self._selected_node.identifier != self._tree.root:
            root_nid = self._selected_node.bpointer
        tree = self._tree.subtree(root_nid)

        # Decrease the level of printing until reaching limit of #lines
        max_depth = self._get_max_possible_depth(tree, max_nr_lines)

        _tree = treelib.Tree()
        root = tree.get_node(root_nid)
        _tree.create_node(identifier=root.identifier, tag=root.tag, data=root.data)
        for depth in xrange(1, max_depth + 1):
            for node in self._nodes_by_depth_cache[depth]:
                _tree.create_node(identifier=node.identifier,
                                  tag=node.tag,
                                  data=node.data,
                                  parent=node.bpointer)
        return _tree

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
                                         picked_nodes=['childnode4', 'grandson5'],
                                         max_nr_lines=20)
    treeprinter.print_tree()
