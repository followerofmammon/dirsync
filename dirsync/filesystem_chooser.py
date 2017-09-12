import os

import dirtree
import printer
import argparse
import treepicker


class FilesystemPicker(object):
    def __init__(self, rootpath):
        self._filesystem_tree = dirtree.DirTree.factory_from_filesystem(rootpath)
        self._tree_picker = treepicker.TreePicker(self._filesystem_tree, min_nr_options=1, max_nr_options=1)

    def pick_one(self):
        return self._tree_picker.pick_one()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=".")
    parser.add_argument("-x", "--execute", default=None)
    return parser.parse_args()


picked_file = None
def pick_wrapper(picker):
    global picked_file
    picked_file = picker.pick_one()


def main():
    args = parse_args()
    picker = FilesystemPicker(args.dir)
    global picked_file
    if os.getenv('MODE') == 'nonstatic':
        picked_file = picker.pick_one()
    else:
        printer.wrapper(pick_wrapper, picker)
    if picked_file is not None:
        if args.execute is not None:
            command = [os.path.basename(args.execute), picked_file.full_filesystem_path()]
            os.execve(args.execute, command, {})
        else:
            printer.print_string(picked_file.full_filesystem_path())


if __name__ == "__main__":
    main()
