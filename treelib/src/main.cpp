#include "treelib.h"

int main() {
    treelib::Tree<int> tree;
    tree.create_node("People", "people", 3);
    tree.create_node("Dumb people", "dumb", "people", 3);
    tree.create_node("Rich dumb people", "rich-dumb", "dumb", 6);
    tree.create_node("Poor dumb people", "poor-dumb", "dumb", 8);
    tree.create_node("Smart people", "smart", "people", 11);
    tree.create_node("Rich smart people", "rich-smart", "smart", 12);
    tree.create_node("Poor smart people", "poor-smart", "smart", 13);

    auto children = tree.children("dumb");
    std::cout << children[0]->data << std::endl;
    std::cout << children[1]->data << std::endl;
    return 0;
}
