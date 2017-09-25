def get_max_possible_depth(tree, root, max_nr_lines, min_depth):
    node_counter = 0
    rootnode = tree.get_node(root)
    root_depth = tree.depth(rootnode)
    depth = root_depth
    bfs_queue = [(rootnode, depth)]
    max_depth = min_depth
    while bfs_queue:
        node, depth = bfs_queue.pop(0)
        is_matching = not hasattr(node, 'matching') or node.matching
        if depth - 1 > max_depth and node_counter <= max_nr_lines:
            max_depth = depth - 1
        if is_matching:
            node_counter += 1
        if depth < min_depth or node_counter < max_nr_lines and is_matching:
            for child in tree.children(node.identifier):
                bfs_queue.append((child, depth + 1))
    if node_counter <= max_nr_lines and depth > max_depth:
        max_depth = depth
    return max_depth - root_depth, node_counter
