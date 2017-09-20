class TreeSearch(object):
    TREE_CACHE_SIZE = 20

    def __init__(self, tree):
        self._tree = tree

    def get_filtered_tree(self, pattern):
        pattern = pattern.lower()
        dfs_stack = [self._tree.get_node(self._tree.root)]
        path_from_root = []

        # Performance optimization
        narrowing_previous_pattern_result = (hasattr(self._tree, 'pattern') and self._tree.pattern and
                                             self._tree.pattern in pattern)

        while dfs_stack:
            node = dfs_stack.pop()

            if path_from_root:
                counter = 0
                while path_from_root[0].identifier != node.bpointer:
                    if counter >= 50:
                        raise ValueError()
                    path_from_root.pop(0)
                    counter += 1
            path_from_root.insert(0, node)

            node_data = node.tag if node.data is None else str(node.data)
            is_matching = pattern in node_data.lower()
            node.original_matching = is_matching
            node.matching = is_matching
            if is_matching:
                for ancestor in path_from_root[1:]:
                    if ancestor.matching:
                        break
                    ancestor.matching = True

            children = self._tree.children(node.identifier)
            if narrowing_previous_pattern_result:
                children = [child for child in children if child.matching]
            dfs_stack.extend(children)

        # Performance optimization
        self._tree.pattern = pattern


if __name__ == "__main__":
    import dirtree
    _dir = dirtree.DirTree.factory_from_filesystem('/home/eliran/Music')
    search = TreeSearch(_dir)
    import cProfile
    profile = cProfile.Profile()
    profile.enable()
    search.get_filtered_tree('B')
    profile.disable()
    profile.dump_stats('profile.bin')
