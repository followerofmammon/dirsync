class TreeNavigator(object):
    def __init__(self, tree, including_root):
        self._tree = tree
        self._including_root = including_root
        self._sorted_children_by_nid_cache = dict()
        self._selected_node = None
        self._calculate_initial_selected_node()

    def get_selected_node(self):
        if self._selected_node is None:
            return None
        return self._selected_node.identifier

    def select_first_match(self):
        if not self._selected_node.original_matching:
            self.go_to_root()
        while not self._selected_node.original_matching:
            previous = self._selected_node
            self.explore()
            if previous == self._selected_node:
                break

    def next(self):
        self._move_selection_relative(distance=1)

    def previous(self):
        self._move_selection_relative(distance=-1)

    def explore(self):
        children = self._sorted_children(self._selected_node)
        if children:
            self._selected_node = children[0]

    def last_node(self):
        self._move_selection_absolute(index=-1)

    def first_node(self):
        self._move_selection_absolute(index=0)

    def go_up(self):
        if self._selected_node.identifier != self._tree.root:
            if not self._including_root and self._selected_node.bpointer == self._tree.root:
                return
            self._selected_node = self._tree.get_node(self._selected_node.bpointer)

    def page_down(self):
        self._move_selection_relative(distance=4)

    def page_up(self):
        self._move_selection_relative(distance=-4)

    def next_leaf(self):
        self._move_selection_relative_leaf(self._DIRECTION_NEXT)

    def prev_leaf(self):
        self._move_selection_relative_leaf(self._DIRECTION_PREV)

    _DIRECTION_NEXT = 1
    _DIRECTION_PREV = 2

    def go_to_root(self):
        # self._selected_node = self._tree.get_node(self._tree.root)
        root = self._tree.get_node(self._tree.root)
        if self._including_root:
            self._selected_node = root
        else:
            self._selected_node = self._children(root)[0]

    def explore_deepest_child(self):
        while True:
            previously_selected_node = self._selected_node
            self.explore()
            if previously_selected_node == self._selected_node:
                break

    def _move_selection_relative_leaf(self, direction):
        # Find next parent
        next_parent = None
        original_selection = self._selected_node
        if not self._sorted_children(original_selection):
            while next_parent is None:
                previously_selected_node = self._selected_node
                distance = 1 if direction == self._DIRECTION_NEXT else -1
                self._move_selection_relative(distance)
                is_last_child_of_parent = self._selected_node == previously_selected_node
                if is_last_child_of_parent and self._selected_node.identifier != self._tree.root:
                    self.go_up()
                    if self._selected_node.identifier == self._tree.root:
                        self._selected_node = original_selection
                        return
                else:
                    next_parent = self._selected_node
        self.explore_deepest_child()

    def set_tree(self, tree):
        self._tree = tree
        self._sorted_children_by_nid_cache = dict()
        self._calculate_initial_selected_node()

    def _node_index_in_list(self, nodes, node):
        match = [idx for idx, _node in enumerate(nodes) if _node.identifier == node.identifier]
        return match[0]

    def _move_selection_relative(self, distance):
        siblings = self._get_siblings()
        wanted_index = self._node_index_in_list(siblings, self._selected_node) + distance
        if wanted_index >= 0 and wanted_index < len(siblings):
            self._selected_node = siblings[wanted_index]
        elif wanted_index < 0:
            self._selected_node = siblings[0]
        elif wanted_index >= len(siblings):
            self._selected_node = siblings[-1]

    def _calculate_initial_selected_node(self):
        node = self._selected_node
        if node is None or node.identifier not in self._tree.nodes:
            node = self._tree.get_node(self._tree.root)
            if not self._including_root:
                children = self._sorted_children(node)
                # assert children, "Root must have children if including_root==False"
                if children:
                    node = children[0]
                else:
                    node = None
        self._selected_node = node

    def _move_selection_absolute(self, index):
        siblings = self._get_siblings()
        self._selected_node = siblings[index]

    def _sorted_children(self, node):
        nid = node.identifier
        if nid not in self._sorted_children_by_nid_cache:
            self._sorted_children_by_nid_cache[nid] = sorted(self._tree.children(nid),
                                                             key=self._node_key)
        return self._sorted_children_by_nid_cache[nid]

    def _get_siblings(self):
        if self._selected_node.identifier == self._tree.root:
            return [self._tree.get_node(self._tree.root)]
        parent = self._tree.get_node(self._selected_node.bpointer)
        return self._sorted_children(parent)

    @staticmethod
    def _node_key(node):
        return str(node.data)

    @classmethod
    def _compare_nodes(cls, node_a, node_b):
        return 1 if cls._node_key(node_a) < cls._node_key(node_b) else -1
