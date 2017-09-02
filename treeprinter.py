import treelib
import binascii
import termcolor


_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME = "____UNLIKELY____999999____SHADAG"


def print_tree(tree, selected_node, search_pattern, picked_nodes, max_nr_lines):
    if selected_node.identifier not in tree.nodes:
        selected_node = tree.get_node(tree.root)
    original_tree = tree
    tree = _prepare_tree_for_printing(tree, selected_node, max_nr_lines)
    _add_id_to_end_of_tags_in_all_nodes(tree)
    lines = str(tree).splitlines()
    for line_index, line in enumerate(lines):
        tag, nid = _decode_encoded_tree_line(line)
        encoded_tag_index = line.index(_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
        line = line[:encoded_tag_index] + tag
        if not tree.children(nid) and original_tree.children(nid):
            line += " (...)"
        prefix = ""
        prefix +=  ">" if nid == selected_node.identifier else " "
        prefix += " "
        prefix +=  "X" if nid in picked_nodes else " "
        line = "%s %s" % (prefix, line)
        if nid == selected_node.identifier:
            color = "blue" if nid in picked_nodes else "green"
            line = termcolor.colored(line, color)
        elif nid in picked_nodes:
            line = termcolor.colored(line, "red")
        print line
    _print_info(selected_node, search_pattern)


def _print_info(selected_node, search_pattern):
    if selected_node.data is None:
        label = selected_node.tag
    else:
        label = selected_node.data
    print '\nCurrent:', label,
    if search_pattern is not None:
        print ', Search filter: %s' % (search_pattern,),
    print


def _prepare_tree_for_printing(tree, selected_node, max_nr_lines):
    # Find root node from which to print tree
    current_root_nid = selected_node.identifier
    if current_root_nid != tree.root:
        current_root_nid = selected_node.bpointer

    tree = tree.subtree(current_root_nid)

    # Increase the level of printing until reaching limit of #lines
    max_depth = 1
    while max_depth >= 1 and max_depth > tree.depth(selected_node):
        nodes_in_current_depth = [node for node in tree.nodes if tree.level(node) <= max_depth]
        if len(nodes_in_current_depth) > max_nr_lines:
            max_depth -= 1
        else:
            break

    _tree = treelib.Tree()
    nodes_by_depth = [list() for depth in xrange(max_depth + 1)]
    for node in tree.nodes.values():
        depth = tree.depth(node)
        if depth <= max_depth:
            nodes_by_depth[depth].append(node)
    root = tree.get_node(current_root_nid)
    _tree.create_node(identifier=root.identifier, tag=root.tag, data=root.data)
    for depth in xrange(1, max_depth + 1):
        for node in nodes_by_depth[depth]:
            _tree.create_node(identifier=node.identifier,
                              tag=node.tag,
                              data=node.data,
                              parent=node.bpointer)
    tree = _tree
    return tree


def _add_id_to_end_of_tags_in_all_nodes(tree):
    for node in tree.nodes.values():
        node.tag = (_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + binascii.hexlify(node.tag) +
                    _UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME + binascii.hexlify(node.identifier))


def _decode_encoded_tree_line(tag):
    parts = tag.split(_UNIQUE_SEPERATOR_UNLIKELY_IN_FILENAME)
    encoded_tag = binascii.unhexlify(parts[1])
    encoded_nid = binascii.unhexlify(parts[2])
    return encoded_tag, encoded_nid


if __name__ == '__main__':
    tree = treelib.Tree()
    root_ = tree.create_node(identifier='rootnodeid', tag='rootnodetag', data='rootnodeval')
    a = tree.create_node('childnode1', 'childnode1', parent='rootnodeid', data='child1data')
    tree.create_node('grandson3', 'grandson3', parent='childnode1', data='grandson3data')
    tree.create_node('grandson4', 'grandson4', parent='childnode1', data='grandson4data')
    tree.create_node('grandson7', 'grandson7', parent='childnode1', data='grandson7data')
    tree.create_node('grandson8', 'grandson8', parent='childnode1', data='grandson8data')

    tree.create_node('grandgrandson1', 'grandgrandson1', parent='grandson7', data='grandgrand1data')
    tree.create_node('grandgrandson6', 'grandgrandson6', parent='grandson7', data='grandgrand6data')
    tree.create_node('grandgrandson9', 'grandgrandson8', parent='grandson7', data='grandgrand9data')

    tree.create_node('grandgrandson11', 'grandgrandson11', parent='grandson8', data='grandgrand11')
    tree.create_node('grandgrandson77', 'grandgrandson77', parent='grandson8', data='grandgrand77')
    tree.create_node('grandgrandson99', 'grandgrandson88', parent='grandson8', data='grandgrand99')

    b = tree.create_node('childnode2', 'childnode2', parent='rootnodeid', data='child2data')
    b = tree.create_node('childnode5', 'childnode5', parent='rootnodeid', data='child5data')
    print_tree(tree,
               selected_node=tree.nodes['grandson7'],
               picked_nodes=[tree.nodes['grandgrandson11'], tree.nodes['grandgrandson1']],
               max_nr_lines=20)
