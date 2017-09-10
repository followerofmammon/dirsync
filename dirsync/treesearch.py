import re
import collections

import treelib


class TreeSearch(object):
    TREE_CACHE_SIZE = 20

    def __init__(self, tree):
        self._original_tree = tree
        self._tree = None
        self._previous_pattern = None
        self._nodes_that_match_search_filter = dict()
        self._pattern_to_base_tree_cache = collections.OrderedDict()

    def get_filtered_tree(self, pattern):
        self._tree = self._get_base_tree(pattern)
        if pattern:
            self._scan_nodes_that_match_search_pattern(pattern)
            self._filter_matching_nodes()
        self._previous_pattern = pattern
        self._populate_tree_cache(pattern)
        return self._tree

    def _get_base_tree(self, pattern):
        if pattern in self._pattern_to_base_tree_cache:
            return self._pattern_to_base_tree_cache.pop(pattern)
        if self._previous_pattern is None or not pattern.startswith(self._previous_pattern):
            self._tree = treelib.Tree(self._original_tree, deep=True)
        return treelib.Tree(self._tree, deep=True)

    def _populate_tree_cache(self, pattern):
        if len(self._pattern_to_base_tree_cache) > self.TREE_CACHE_SIZE:
            oldest_keyin_cahe = self._pattern_to_base_tree_cache.keys()[0]
            del oldest_keyin_cahe[oldest_keyin_cahe]
        self._pattern_to_base_tree_cache[pattern] = self._tree

    def _scan_nodes_that_match_search_pattern(self, pattern):
        self._nodes_that_match_search_filter = {self._tree.root: True}
        for nid, node in self._tree.nodes.iteritems():
            node_data = node.tag if node.data is None else str(node.data)
            if re.findall(pattern, node_data):
                for ancestor_nid in self._tree.rsearch(nid):
                    self._nodes_that_match_search_filter[ancestor_nid] = True

    def _filter_matching_nodes(self):
        while True:
            for nid, node in self._tree.nodes.iteritems():
                if nid not in self._nodes_that_match_search_filter:
                    self._tree.remove_node(node.identifier)
                    break
            else:
                break

    def _interactive_search_iteration(self):
        result = self._scan_char()
        if result == self._SEARCH_RESULT_SERACH_ENDED:
            if not self._search_pattern:
                self._tree = treelib.Tree(self._original_tree, deep=True)
        elif result == self._SERACH_RESULT_SERACH_CONTINUES:
            self._tree = treelib.Tree(self._original_tree, deep=True)
            self._scan_nodes_that_match_search_pattern()
            self._filter_matching_nodes()
            result = self._SERACH_RESULT_SERACH_CONTINUES
        else:
            assert False, result
