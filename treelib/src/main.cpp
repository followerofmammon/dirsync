#include "treelib.h"

int main() {
    treelib::Tree<int> tree;
    tree.create_node("Dumb people", "dumb", 3);
    tree.create_node("Rich dumb people", "rich-dumb", "dumb", 6);
    tree.create_node("Poor dumb people", "poor-dumb", "dumb", 8);
    tree.create_node("Smart people", "dumb", 11);
    tree.create_node("Rich smart people", "rich-smart", "dumb", 12);
    tree.create_node("Poor smart people", "poor-smart", "dumb", 13);
    return 0;
}
