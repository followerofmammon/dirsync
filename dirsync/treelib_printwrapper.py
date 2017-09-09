import treelib


def get_tree_output(tree, nid=None, level=treelib.Tree.ROOT, idhidden=True, filter=None,
                    key=None, reverse=False, line_type='ascii-ex', data_property=None):
    """This is used instead of str(tree) and tree.show(), since tree.show prints
    only to stdout, and str(tree) does not have the ability to sort by key.
    So both of the these abilities are done in this method.
    """
    tree.reader = ""

    def write(line):
        tree.reader += line.decode('utf-8') + "\n"

    try:
        tree._Tree__print_backend(nid, level, idhidden, filter,
                                  key, reverse, line_type, data_property, func=write)
    except treelib.tree.NodeIDAbsentError:
        print('Tree is empty')

    return tree.reader.encode('utf-8')
