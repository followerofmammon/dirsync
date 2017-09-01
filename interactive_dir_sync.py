import dirtree
import treepicker
import optionpicker


class InteractiveDiffSync(object):
    MAX_NR_LINES = 20

    _OPTION_COPY = "Copy selected files"
    _OPTION_REMOVE = "Remove selected files"
    _OPTION_NOTHING = "Do nothing"
    _OPTION_RESELECT = "Reselect files"

    def __init__(self, src, dst):
        self._src = dirtree.DirTree.factory_from_filesystem(src)
        self._dst = dirtree.DirTree.factory_from_filesystem(dst)
        self._selected = list()

    def sync(self):
        missing = self._dst.get_unknown_entries_in_given_dirtree(self._src)
        print "Files in %s, which are not in %s:" % (self._src, self._dst)
        self._tree_picker = treepicker.TreePicker(missing)
        while True:
            self._chooseFiles()
            if not self._selected:
                break
            print "%d files were chosen to copy so far." % (len(self._selected),)
            option = self._chooseWhatToDoWithFiles()
            if option == self._OPTION_NOTHING:
                break
            elif option == self._OPTION_COPY:
                self._copy()
                self._update_from_filesystem()
            elif option == self._OPTION_REMOVE:
                self._remove()
            elif option == self._OPTION_RESELECT:
                pass
            else:
                assert False, option

    def _chooseFiles(self):
        print 'To select a file, press Space. When finished, press Enter.'
        entries = self._tree_picker.pick(self.MAX_NR_LINES)
        files = [entry for entry in entries if isinstance(entry, dirtree.FileEntry)]
        self._selected = files

    def _chooseWhatToDoWithFiles(self):
        options = [self._OPTION_NOTHING, self._OPTION_RESELECT]
        if self._selected:
            options.extend([self._OPTION_COPY, self._OPTION_REMOVE])
        picker = optionpicker.OptionPickerByMenuTraverse(options)
        return picker.pick_one()

    def _update_from_filesystem(self):
        self._dst.update_from_filesystem()

    def _copy(self):
        _dirtree = dirtree.DirTree.factory_from_list_of_file_entries(self._selected,
                                                                     self._src.fullpath())
        self._dst.copy_inner_entries_from_dirtree(_dirtree)


if __name__ == "__main__":
    sync = InteractiveDiffSync('alpha', 'bravo')
    sync.sync()
