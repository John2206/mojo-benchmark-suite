import java.util.Random;

public class Bst {
    static class Node {
        long val;
        Node left, right;
        Node(long val) { this.val = val; }
    }

    static void insert(Node root, long val) {
        Node cur = root;
        while (true) {
            if (val < cur.val) {
                if (cur.left == null) { cur.left = new Node(val); return; }
                cur = cur.left;
            } else {
                if (cur.right == null) { cur.right = new Node(val); return; }
                cur = cur.right;
            }
        }
    }

    static long prev;
    static boolean first = true;
    static boolean ok = true;
    static long maxVal;
    static long count = 0;

    static void inorder(Node node) {
        if (node == null) return;
        inorder(node.left);
        if (!first && node.val < prev) ok = false;
        first = false;
        prev = node.val;
        maxVal = node.val;
        count++;
        inorder(node.right);
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 300_000;

        Random rnd = new Random(42);
        Node root = new Node(rnd.nextLong() & Long.MAX_VALUE);
        for (long i = 1; i < n; i++) {
            insert(root, rnd.nextLong() & Long.MAX_VALUE);
        }

        inorder(root);

        if (!ok || count != n) {
            System.err.println("self-check failed: in-order traversal not sorted or count mismatch");
            System.exit(1);
        }

        System.out.println(maxVal);
    }
}
