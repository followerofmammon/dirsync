#ifndef __TREELIB_H
#define __TREELIB_H

#include <vector>
#include <string>

template <class T>
class Node
{
public:
    Node(std::string tag, std::string ID, T value);

    T value;
    std::string tag;
    std::string ID;

private:
    Node *parent_node;
    std::vector<Node*> children;
}

template <class T>
class Treelib
{
public:
    Treelib(void);

    Node<T>* create_node(std::string tag, std::string identifier, std::string parent, T value);

private:
    Node root;
}


template <class T>
Node<T>* Node<T>::create_node(T value) {

}

#endif
