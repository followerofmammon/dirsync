def populate_bindings(keybind):
    keybind.bind('j', 'next')
    keybind.bind('k', 'previous')
    keybind.bind('l', 'explore')
    keybind.bind('h', 'up')
    keybind.bind('q', 'quit')
    keybind.bind('G', 'last_node')
    keybind.bind('g', 'first_node')
    keybind.bind(chr(3), 'quit')  # Ctrl-c
    keybind.bind('/', 'start_interactive_search')
    keybind.bind(chr(16), 'start_interactive_search')  # Ctrl-p
    keybind.bind(chr(13), 'return_picked_nodes')  # Return
    keybind.bind(chr(31), 'start_search')  # Ctrl-/
    keybind.bind(chr(32), 'toggle')  # Space
    keybind.bind(chr(4), 'page_down')  # Ctrl-d
    keybind.bind(chr(21), 'page_up')  # Ctrl-u
    keybind.bind('u', 'page_up')
    keybind.bind('d', 'page_down')
    keybind.bind(chr(10), 'next_leaf')  # Ctrl-j
    keybind.bind(chr(11), 'prev_leaf')  # Ctrl-k


def register_actions(keybind, treepicker, tree_navigator):
    keybind.add_action('next', tree_navigator.next)
    keybind.add_action('previous', tree_navigator.previous)
    keybind.add_action('explore', tree_navigator.explore)
    keybind.add_action('up', tree_navigator.go_up)
    keybind.add_action('last_node', tree_navigator.last_node)
    keybind.add_action('first_node', tree_navigator.first_node)
    keybind.add_action('quit', treepicker.quit)
    keybind.add_action('start_search', treepicker.start_search)
    keybind.add_action('start_interactive_search', treepicker.start_interactive_search)
    keybind.add_action('return_picked_nodes', treepicker.return_picked_nodes)
    keybind.add_action('toggle', treepicker.toggle)
    keybind.add_action('page_up', tree_navigator.page_up)
    keybind.add_action('page_down', tree_navigator.page_down)
    keybind.add_action('next_leaf', tree_navigator.next_leaf)
    keybind.add_action('prev_leaf', tree_navigator.prev_leaf)
