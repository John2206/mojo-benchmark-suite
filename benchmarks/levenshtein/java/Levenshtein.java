public class Levenshtein {
    static int editDistance(byte[] s1, byte[] s2) {
        int len1 = s1.length, len2 = s2.length;
        int[] prev = new int[len2 + 1];
        int[] cur = new int[len2 + 1];
        for (int j = 0; j <= len2; j++) prev[j] = j;

        for (int i = 1; i <= len1; i++) {
            cur[0] = i;
            for (int j = 1; j <= len2; j++) {
                int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
                int del = prev[j] + 1;
                int ins = cur[j - 1] + 1;
                int sub = prev[j - 1] + cost;
                cur[j] = Math.min(del, Math.min(ins, sub));
            }
            int[] tmp = prev; prev = cur; cur = tmp;
        }

        return prev[len2];
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 5000;

        if (editDistance("kitten".getBytes(), "sitting".getBytes()) != 3) {
            System.err.println("self-check failed: edit_distance(kitten,sitting) mismatch");
            System.exit(1);
        }

        byte[] alphabet = "ACGT".getBytes();
        byte[] s1 = new byte[n];
        byte[] s2 = new byte[n];
        for (int i = 0; i < n; i++) {
            int base = (i * 7 + 3) % 4;
            s1[i] = alphabet[base];
            s2[i] = (i % 5 == 4) ? alphabet[(base + 1) % 4] : alphabet[base];
        }

        System.out.println(editDistance(s1, s2));
    }
}
