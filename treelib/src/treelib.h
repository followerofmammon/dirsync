#ifndef __TREELIB_H
#define __TREELIB_H

#include <vector>
#include <string>
#include <map>
#include <iostream>

namespace treelib {

template <class T>
class Node
{
public:
    Node(std::string _tag, std::string _identifier, T _data, std::string parent);

    std::string tag;
    std::string identifier;
    std::string parent;
    T data;
    std::vector< Node<T> * > children;
    void add_child(Node<T> *node);

private:
    Node *parent_node;
};

template <class T>
class Tree
{
public:
    Tree(void) : root(nullptr) {

    }

    Node<T>* create_node(std::string tag, std::string identifier, T data) {
        if (nullptr != root) {
            std::cout << "A root node already exists.";
            throw "A root node already exists.";
        }
        return create_node(tag, identifier, "", data);
    }

    Node<T>* create_node(std::string tag, std::string identifier, std::string parent, T data) {
        if (node_map.count(identifier)) {
            std::cout << "Duplicate node";
            throw "Duplicate node";
        }
        Node<T> * node = new Node<T>(tag, identifier, data, "");
        node_map[identifier] = node;

        if (parent.length()) {
            Node<T> *parent_node = get_node(parent);
            parent_node->add_child(node);
        }
        return node;
    }

    Node<T>* get_node(std::string identifier) {
        if (node_map.count(identifier))
            return node_map[identifier];
        return nullptr;
    }

    std::vector< Node<T> * > & children(std::string identifier) {
        return node_map[identifier]->children;
    }

private:
    Node<T>* root;

    std::map<std::string, Node<T> * > node_map;
};

template <class T>
Node<T>::Node(std::string _tag, std::string _identifier, T _data, std::string _parent) {
    tag = _tag;
    identifier = _identifier;
    data = _data;
    parent = _parent;
}

template <class T>
void Node<T>::add_child(Node<T> *child) {
    children.insert(children.begin(), child);
}

} // namespace treelib

#endif
