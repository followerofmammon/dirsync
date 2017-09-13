def get_max_possible_depth(tree, max_nr_lines, min_depth):
    node_counter = 0
    depth = 0
    bfs_queue = [(tree.get_node(tree.root), depth)]
    nodes_by_depth = dict()
    max_depth = min_depth
    while bfs_queue:
        node, depth = bfs_queue.pop(0)
        if depth - 1 > max_depth and node_counter <= max_nr_lines:
            max_depth = depth - 1
        node_counter += 1
        if depth < min_depth or node_counter < max_nr_lines:
            for child in tree.children(node.identifier):
                bfs_queue.append((child, depth + 1))
        nodes_by_depth.setdefault(depth, list()).append(node)
    if node_counter <= max_nr_lines and depth > max_depth:
        max_depth = depth
    return max_depth, nodes_by_depth
