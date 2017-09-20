def paginate(nr_items, selected_item_index, max_nr_items):
    nr_items_removed_at_the_beginning = 0
    nr_items_removed_at_the_end = 0

    # Remove after selected, if too long
    if nr_items > max_nr_items:
        nr_items_removed_at_the_end = min(nr_items - selected_item_index - 1, nr_items - max_nr_items)
        nr_items_removed_at_the_end = max(0, nr_items_removed_at_the_end)

        # Remove nodes before selected, if too long
        if nr_items > max_nr_items:
            nr_items_removed_at_the_beginning = selected_item_index - max_nr_items + 2
            if nr_items_removed_at_the_end == 0:
                nr_items_removed_at_the_beginning -= 1
            nr_items_removed_at_the_beginning = max(nr_items_removed_at_the_beginning, 0)
            if nr_items_removed_at_the_beginning == 1:
                nr_items_removed_at_the_beginning = 0
            if nr_items_removed_at_the_end == 1:
                nr_items_removed_at_the_end = 0

    return nr_items_removed_at_the_beginning, nr_items_removed_at_the_end
