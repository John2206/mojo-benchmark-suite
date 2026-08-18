#include <stdio.h>
#include <stdlib.h>

static unsigned int lcg_state;

static long lcg_next(void) {
    lcg_state = (lcg_state * 1103515245u + 12345u) & 0x7fffffffu;
    return (long)lcg_state;
}

typedef struct Node {
    long val;
    struct Node *left, *right;
} Node;

Node *make_node(long val) {
    Node *n = malloc(sizeof(Node));
    n->val = val;
    n->left = n->right = NULL;
    return n;
}

void insert(Node **root, long val) {
    Node **cur = root;
    while (*cur != NULL) {
        if (val < (*cur)->val) cur = &(*cur)->left;
        else cur = &(*cur)->right;
    }
    *cur = make_node(val);
}

void inorder(Node *node, long *prev, int *first, int *ok, long *max_val, long *count) {
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

    lcg_state = 42;
    Node *root = NULL;
    for (long i = 0; i < n; i++) {
        insert(&root, lcg_next());
    }

    long prev = 0, max_val = 0;
    int first = 1, ok = 1;
    long count = 0;
    inorder(root, &prev, &first, &ok, &max_val, &count);

    if (!ok || count != n) {
        fprintf(stderr, "self-check failed: in-order traversal not sorted or count mismatch\n");
        return 1;
    }

    printf("%ld\n", max_val);
    return 0;
}
