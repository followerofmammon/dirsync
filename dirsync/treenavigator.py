class TreeNavigator(object):
    def __init__(self, tree, including_root):
        self._tree = tree
        self._including_root = including_root
        self._sorted_children_by_nid_cache = dict()
        self._selected_node = self._calculate_initial_node()

    def get_selected_node(self):
        return self._selected_node.identifier

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

    def set_tree(self, tree):
        self._tree = tree
        self._sorted_children_by_nid_cache = dict()
        self._selected_node = self._calculate_initial_node()

    def _move_selection_relative(self, distance):
        siblings = self._get_siblings()
        wanted_index = siblings.index(self._selected_node) + distance
        if wanted_index >= 0 and wanted_index < len(siblings):
            self._selected_node = siblings[wanted_index]
        elif wanted_index < 0:
            self._selected_node = siblings[0]
        elif wanted_index >= len(siblings):
            self._selected_node = siblings[-1]

    def _calculate_initial_node(self):
        node = self._tree.get_node(self._tree.root)
        if not self._including_root:
            children = self._tree.children(self._tree.root)
            assert children, "Root must have children if including_root==False"
            node = self._sorted_children(node)[0]
        return node

    def _move_selection_absolute(self, index):
        siblings = self._get_siblings()
        self._selected_node = siblings[index]

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
