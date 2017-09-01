import treelib
from termcolor import colored

import getcher


class TreePicker(object):
    _OPTION_NEXT = "Down"
    _OPTION_PREV = "Previous"
    _OPTION_UP = "Up"
    _OPTION_TOGGLE = "Toggle"
    _OPTION_RETURN = "Enter"
    _OPTION_EXPLORE = "Explore"
    _OPTION_QUIT = "Quit"
    _OPTION_MOVE_TO_SEARCH_MODE = "Move to search mode"

    _MODE_NAVIGATION = 'navigation'
    _MODE_SEARCH = 'search'
    _MODE_QUIT = 'quit'

    _UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"

    def __init__(self, tree, min_nr_options=0, max_nr_options=None):
        self._tree = tree
        self._current_node = self._tree.get_node(self._tree.root)
        self._picked = dict()
        self._getcher = getcher.GetchUnix()
        self._sorted_children_by_nid_cache = dict()
        self._mode = self._MODE_NAVIGATION
        self._print_tree_once = True
        self._search_filter = None

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
            self._current_node = self._tree.get_node(self._tree.root)
            self._explore()
        while True:
            if self._mode == self._MODE_NAVIGATION:
                result = self._navigate(max_nr_lines, min_nr_options, max_nr_options, including_root)
                if result is not None:
                    return result
            elif self._mode == self._MODE_SEARCH:
                self._search()
            elif self._mode == self._MODE_QUIT:
                break
            else:
                raise ValueError(self._mode)

    def _search(self):
        print "Type a regex search filter:",
        self._search_filter = raw_input()
        self._mode = self._MODE_NAVIGATION

    def _navigate(self, max_nr_lines, min_nr_options, max_nr_options, including_root):
        if self._print_tree_once:
            self._print_tree(max_nr_lines)
            if self._current_node.data is None:
                label = self._current_node.tag
            else:
                label = self._current_node.data
            print '\nCurrent:', label
        self._print_tree_once = True
        option = self._scan_option()
        if option == self._OPTION_NEXT:
            result = self._next()
            if not result:
                self._print_tree_once = False
        elif option == self._OPTION_PREV:
            result = self._prev()
            if not result:
                self._print_tree_once = False
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
                return [self._current_node.data]
            if len(self._picked) <= max_nr_options and \
                    len(self._picked) >= min_nr_options:
                return self._picked.values()
        elif option == self._OPTION_QUIT:
            self._mode = self._MODE_QUIT
        elif option == self._OPTION_MOVE_TO_SEARCH_MODE:
            if self._mode == self._MODE_NAVIGATION:
                self._mode = self._MODE_SEARCH
        else:
            assert False, option
        return None

    @classmethod
    def _add_id_to_end_of_tags_in_all_nodes(cls, tree):
        for node in tree.nodes.values():
            node.tag = (cls._UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + node.tag +
                        cls._UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + node.identifier)

    @classmethod
    def _decode_encoded_tree_line(cls, tag):
        parts = tag.split(cls._UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
        return parts[1:]

    @classmethod
    def _remove_id_to_end_of_tags_in_all_nodes(cls, tree):
        for node in tree.nodes.values():
            original_tag, _ = cls._decode_encoded_tree_line(node.tag)
            node.tag = original_tag

    def _prepare_tree_for_printing(self, max_nr_lines):
        # Find root node from which to print tree
        current_root_nid = self._current_node.identifier
        if current_root_nid != self._tree.root:
            current_root_nid = self._current_node.bpointer

        # Pick the uppermost root that allows printing below the limit of #lines
        while (current_root_nid != self._tree.root):
            parent_nid = self._tree.get_node(current_root_nid).bpointer
            if self._tree.subtree(parent_nid).size() <= max_nr_lines:
                current_root_nid = parent_nid
            else:
                break
        tree = self._tree.subtree(current_root_nid)
        # Pick the uppermost root that allows printing below the limit of #lines

        # Limit the level of printing until reaching limit of #lines
        current_depth = tree.depth()
        while current_depth >= 1 and current_depth > tree.depth(self._current_node):
            nodes_in_current_depth = [node for node in tree.nodes if tree.level(node) <= current_depth]
            if len(nodes_in_current_depth) > max_nr_lines:
                current_depth -= 1
            else:
                break

        # Generate the subtree according to the new depth
        tree = treelib.Tree(tree, deep=True)
        while tree.depth() > current_depth:
            nodes_too_deep = [nid for nid in tree.nodes if tree.depth(nid) == current_depth + 1]
            for nid in nodes_too_deep:
                tree.remove_node(nid)

        return tree

    def _print_tree(self, max_nr_lines):
        tree = self._prepare_tree_for_printing(max_nr_lines)
        root_nid = tree.root
        self._add_id_to_end_of_tags_in_all_nodes(tree)
        lines = str(tree.subtree(root_nid)).splitlines()
        line_index_to_nid = [self._decode_encoded_tree_line(line)[1] for line in lines]
        self._remove_id_to_end_of_tags_in_all_nodes(tree)
        lines = str(tree.subtree(root_nid)).splitlines()
        for line_index, line in enumerate(lines):
            nid = line_index_to_nid[line_index]
            if not tree.children(nid) and self._tree.children(nid):
                line += " (...)"
            prefix = ""
            prefix +=  ">" if nid == self._current_node.identifier else " "
            prefix += " "
            prefix +=  "X" if nid in self._picked else " "
            line = "%s %s" % (prefix, line)
            if nid == self._current_node.identifier:
                color = "blue" if nid in self._picked else "green"
                line = colored(line, color)
            elif nid in self._picked:
                line = colored(line, "red")
            print line

    def _sorted_children(self, nid):
        if nid not in self._sorted_children_by_nid_cache:
            self._sorted_children_by_nid_cache[nid] = sorted(self._tree.children(nid))
        return self._sorted_children_by_nid_cache[nid]

    def _next(self):
        if self._current_node.identifier != self._tree.root:
            parent = self._tree.get_node(self._current_node.bpointer)
            siblings = self._sorted_children(parent.identifier)
            index = siblings.index(self._current_node)
            if len(siblings) > index + 1:
                self._current_node = siblings[index + 1]
                return True
        return False

    def _prev(self):
        if self._current_node.identifier != self._tree.root:
            parent = self._tree.get_node(self._current_node.bpointer)
            siblings = self._sorted_children(parent.identifier)
            index = siblings.index(self._current_node)
            if index > 0:
                self._current_node = siblings[index - 1]
                return True
        return False

    def _explore(self):
        if self._tree.children(self._current_node.identifier):
            children = self._tree.children(self._current_node.identifier)
            children = self._sorted_children(self._current_node.identifier)
            self._current_node = sorted(children)[0]
            return True
        return False

    def _go_up(self, including_root=False):
        if self._current_node.identifier != self._tree.root:
            if not including_root and \
                    self._tree.get_node(self._current_node.identifier) in \
                    self._tree.children(self._tree.root):
                return False
            self._current_node = self._tree.get_node(self._current_node.bpointer)
            return True
        return False

    def _scan_option(self):
        key_to_option = {'j': self._OPTION_NEXT,
                         'k': self._OPTION_PREV,
                         'l': self._OPTION_EXPLORE,
                         'h': self._OPTION_UP,
                         'q': self._OPTION_QUIT,
                         '/': self._OPTION_MOVE_TO_SEARCH_MODE,
                         chr(13): self._OPTION_RETURN,
                         chr(32): self._OPTION_TOGGLE}
        key = None
        while key not in key_to_option:
            key = self._getcher()
        return key_to_option[key]

    def _toggle(self):
        if self._current_node.identifier in self._picked:
            del self._picked[self._current_node.identifier]
            for nid, node in self._tree.subtree(self._current_node.identifier).nodes.iteritems():
                if node.identifier in self._picked:
                    del self._picked[nid]
        else:
            self._picked[self._current_node.identifier] = \
                    self._tree.get_node(self._current_node.identifier).data
            for nid, node in self._tree.subtree(self._current_node.identifier).nodes.iteritems():
                if node.identifier not in self._picked:
                    self._picked[nid] = self._tree.get_node(nid).data


if __name__ == '__main__':
    import treewithops
    tree = treewithops.TreeWithOps()
    root_ = tree.create_node(identifier='rootnodeid', tag='rootnodetag', data='rootnodeval')
    a = tree.create_node('childnode1', 'childnode1', parent='rootnodeid', data='child1data')
    tree.create_node('grandson3', 'grandson3', parent='childnode1', data='grandson3data')
    tree.create_node('grandson4', 'grandson4', parent='childnode1', data='grandson4data')
    tree.create_node('grandson5', 'grandson5', parent='childnode1', data='grandson5data')
    tree.create_node('grandson6', 'grandson6', parent='childnode1', data='grandson6data')
    tree.create_node('grandson7', 'grandson7', parent='childnode1', data='grandson7data')
    tree.create_node('grandson8', 'grandson8', parent='childnode1', data='grandson8data')

    tree.create_node('grandgrandson1', 'grandgrandson1', parent='grandson7', data='grandgrand1data')
    tree.create_node('grandgrandson2', 'grandgrandson2', parent='grandson7', data='grandgrand2data')
    tree.create_node('grandgrandson3', 'grandgrandson3', parent='grandson7', data='grandgrand3data')
    tree.create_node('grandgrandson4', 'grandgrandson4', parent='grandson7', data='grandgrand4data')
    tree.create_node('grandgrandson5', 'grandgrandson5', parent='grandson7', data='grandgrand5data')
    tree.create_node('grandgrandson6', 'grandgrandson6', parent='grandson7', data='grandgrand6data')
    tree.create_node('grandgrandson7', 'grandgrandson7', parent='grandson7', data='grandgrand7data')
    tree.create_node('grandgrandson9', 'grandgrandson8', parent='grandson7', data='grandgrand9data')

    tree.create_node('grandgrandson11', 'grandgrandson11', parent='grandson8', data='grandgrand11')
    tree.create_node('grandgrandson22', 'grandgrandson22', parent='grandson8', data='grandgrand22')
    tree.create_node('grandgrandson33', 'grandgrandson33', parent='grandson8', data='grandgrand33')
    tree.create_node('grandgrandson44', 'grandgrandson44', parent='grandson8', data='grandgrand44')
    tree.create_node('grandgrandson55', 'grandgrandson55', parent='grandson8', data='grandgrand55')
    tree.create_node('grandgrandson66', 'grandgrandson66', parent='grandson8', data='grandgrand66')
    tree.create_node('grandgrandson77', 'grandgrandson77', parent='grandson8', data='grandgrand77')
    tree.create_node('grandgrandson99', 'grandgrandson88', parent='grandson8', data='grandgrand99')

    b = tree.create_node('childnode2', 'childnode2', parent='rootnodeid', data='child2data')
    b = tree.create_node('childnode3', 'childnode3', parent='rootnodeid', data='child3data')
    b = tree.create_node('childnode4', 'childnode4', parent='rootnodeid', data='child4data')
    b = tree.create_node('childnode5', 'childnode5', parent='rootnodeid', data='child5data')
    treepicker = TreePicker(tree)
    picked = treepicker.pick(max_nr_lines=25)
