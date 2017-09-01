import treelib


class TreeWithOps(treelib.Tree):
    def __init__(self):
        super(TreeWithOps, self).__init__()

    def _get_distance_from_node(self, node, base_node):
        dfs_stack = [(base_node, 0)]
        while dfs_stack:
            cur_node, level = dfs_stack.pop()
            if cur_node == node:
                return level
            for child in self.children(cur_node.identifier):
                dfs_stack.append((child, level + 1))
        raise ValueError(node)

