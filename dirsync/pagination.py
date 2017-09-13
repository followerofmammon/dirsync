def paginate(items, selected_item, max_nr_items):
    nr_items_removed_at_the_beginning = 0
    nr_items_removed_at_the_end = 0

    # Remove after selected, if too long
    if len(items) > max_nr_items:

        index = items.index(selected_item)
        nr_items_removed_at_the_end = min(len(items) - index - 1, len(items) - max_nr_items)
        if nr_items_removed_at_the_end > 0:
            items = items[:-nr_items_removed_at_the_end]
        else:
            nr_items_removed_at_the_end = 0

        # Remove nodes before selected, if too long
        if len(items) > max_nr_items:
            nr_items_removed_at_the_beginning = index - max_nr_items + 2
            if nr_items_removed_at_the_end == 0:
                nr_items_removed_at_the_beginning -= 1
            items = items[nr_items_removed_at_the_beginning:]

    return items, nr_items_removed_at_the_beginning, nr_items_removed_at_the_end
