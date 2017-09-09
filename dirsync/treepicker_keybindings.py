def populate_bindings(keybind):
    keybind.bind('j', 'next')
    keybind.bind('k', 'previous')
    keybind.bind('l', 'explore')
    keybind.bind('h', 'up')
    keybind.bind('q', 'quit')
    keybind.bind('G', 'last_node')
    keybind.bind('g', 'first_node')
    keybind.bind(chr(3), 'quit')  # Ctrl-C
    keybind.bind('/', 'start_search')
    keybind.bind(chr(16), 'start_interactive_search')  # Ctrl-P
    keybind.bind(chr(13), 'return_picked_nodes')  # Return
    keybind.bind(chr(32), 'toggle')  # Space
    keybind.bind(chr(4), 'page_down')  # Ctrl-D
    keybind.bind(chr(21), 'page_up')  # Ctrl-U
    keybind.bind('u', 'page_up')
    keybind.bind('d', 'page_down')
