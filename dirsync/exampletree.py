import treelib


tree = treelib.Tree()
root_ = tree.create_node(identifier='rootnodeid', tag='rootnodetag', data='rootnodeval')
for i in range(5) + range(10, 15):
    name = "childnode%s" % (i,)
    tree.create_node(name, name, parent='rootnodeid', data=name)
for i in xrange(3, 9):
    name = "grandson%d" % (i,)
    tree.create_node(name, name, parent='childnode4', data=name)
for i in xrange(7):
    name = "grandgrandson%d" % (i,)
    tree.create_node(name, name, parent='grandson7', data=name)
for i in [7, 8, 9]:
    name = "grandgrandson%d" % (i * 11,)
    tree.create_node(name, name, parent='grandson8', data=name)
