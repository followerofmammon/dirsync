import dirtree
import treepicker


class FilesystemPicker(object):
    MAX_NR_FILES = 25

    def __init__(self, rootpath):
        self._filesystem_tree = dirtree.DirTree.factory_from_filesystem(rootpath)
        self._tree_picker = treepicker.TreePicker(self._filesystem_tree)

    def pick(self):
        return self._tree_picker.pick(self.MAX_NR_FILES)


if __name__ == "__main__":
    picker = FilesystemPicker('alpha')
    print picker.pick()

