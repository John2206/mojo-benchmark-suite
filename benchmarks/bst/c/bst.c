#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node *left, *right;
} Node;

Node *make_node(int val) {
    Node *n = malloc(sizeof(Node));
    n->val = val;
    n->left = n->right = NULL;
    return n;
}

void insert(Node **root, int val) {
    Node **cur = root;
    while (*cur != NULL) {
        if (val < (*cur)->val) cur = &(*cur)->left;
        else cur = &(*cur)->right;
    }
    *cur = make_node(val);
}

void inorder(Node *node, int *prev, int *first, int *ok, int *max_val, long *count) {
    if (node == NULL) return;
    inorder(node->left, prev, first, ok, max_val, count);
    if (!*first && node->val < *prev) *ok = 0;
    *first = 0;
    *prev = node->val;
    *max_val = node->val;
    (*count)++;
    inorder(node->right, prev, first, ok, max_val, count);
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 300000;

    srand(42);
    Node *root = NULL;
    for (long i = 0; i < n; i++) {
        insert(&root, rand());
    }

    int prev = 0, first = 1, ok = 1, max_val = 0;
    long count = 0;
    inorder(root, &prev, &first, &ok, &max_val, &count);

    if (!ok || count != n) {
        fprintf(stderr, "self-check failed: in-order traversal not sorted or count mismatch\n");
        return 1;
    }

    printf("%d\n", max_val);
    return 0;
}
