import printer
import treepicker
import treeprinter


class TreePickerShellOutput(object):
    def __init__(self, tree, header, max_nr_lines):
        self._header = header
        self._tree_printer = treeprinter.TreePrinter(tree)
        self._max_nr_lines = max_nr_lines

    def print_tree(self, selected_node, search_pattern, picked_nodes, mode):
        self._tree_printer.calculate_lines_to_print(selected_node, picked_nodes, self._max_nr_lines)
        printer.clear_screen()
        if self._header is not None:
            printer.print_string(self._header)
        self._tree_printer.print_tree()
        footer = ""
        is_search_pattern_being_edited = mode in (treepicker.TreePicker._MODE_SEARCH,
                                                  treepicker.TreePicker._MODE_INTERACTIVE_SEARCH)
        if is_search_pattern_being_edited:
            footer = '\nInsert Search filter: %s <<--' % (search_pattern.strip(),)
            color = "magenta"
        elif search_pattern:
            footer = '\nCurrent Search filter: %s' % (search_pattern.strip(),)
            color = "yellow"
        if footer:
            printer.print_string(footer, color)

    def set_tree(self, tree):
        self._tree_printer.set_tree(tree)
