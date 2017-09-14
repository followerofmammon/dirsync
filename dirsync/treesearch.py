import collections

import treelib


class TreeSearch(object):
    TREE_CACHE_SIZE = 20

    def __init__(self, tree):
        self._tree = treelib.Tree(tree, deep=True)
        self._result_cache = collections.OrderedDict()

    def get_filtered_tree(self, pattern):
        pattern = pattern.lower()
        if pattern in self._result_cache:
            tree = self._result_cache.pop(pattern)
        elif pattern:
            matching_nodes = self._scan_nodes_that_match_search_pattern(pattern)
            tree = self._filter_matching_nodes(matching_nodes)
        else:
            tree = self._tree
        self._populate_tree_cache(pattern, tree)
        return tree

    def _populate_tree_cache(self, pattern, tree):
        if len(self._result_cache) > self.TREE_CACHE_SIZE:
            oldest_keyin_cahe = self._result_cache.keys()[0]
            del oldest_keyin_cahe[oldest_keyin_cahe]
        self._result_cache[pattern] = tree

    def _scan_nodes_that_match_search_pattern(self, pattern):
        matching_nodes = {self._tree.root: True}
        for nid, node in self._tree.nodes.iteritems():
            node_data = node.tag if node.data is None else str(node.data)
            if pattern in node_data.lower():
                for ancestor_nid in self._tree.rsearch(nid):
                    if ancestor_nid in matching_nodes:
                        break
                    else:
                        matching_nodes[ancestor_nid] = True
                        yield ancestor_nid

    def _filter_matching_nodes(self, matching_nodes):
        tree = treelib.Tree()
        root = self._tree.get_node(self._tree.root)
        tree.create_node(tag=root.tag, identifier=root.identifier, data=root.data)
        for matching_nid in matching_nodes:
            nodes_to_add_gen = self._tree.rsearch(matching_nid)
            nodes_to_add = list()
            for nid in nodes_to_add_gen:
                if nid in tree.nodes:
                    break
                else:
                    nodes_to_add.insert(0, nid)
            for nid in nodes_to_add:
                node = self._tree.get_node(nid)
                tree.create_node(tag=node.tag,
                                 identifier=node.identifier,
                                 data=node.data,
                                 parent=node.bpointer)
        return tree

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
