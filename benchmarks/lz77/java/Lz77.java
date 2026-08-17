import java.util.ArrayList;
import java.util.List;

public class Lz77 {
    static final int WINDOW = 4096;
    static final int MAX_MATCH = 255;
    static final int MIN_MATCH = 3;
    static final int HASH_SIZE = 8192;

    static class Token {
        boolean isMatch;
        int offset;
        int length;
        byte literal;
    }

    static int hash3(byte[] data, int i) {
        return (((data[i] & 0xFF) * 131 + (data[i + 1] & 0xFF)) * 131 + (data[i + 2] & 0xFF)) & (HASH_SIZE - 1);
    }

    static List<Token> encode(byte[] data) {
        int n = data.length;
        int[] hashTable = new int[HASH_SIZE];
        java.util.Arrays.fill(hashTable, -1);

        List<Token> tokens = new ArrayList<>();
        int i = 0;
        while (i < n) {
            int bestLen = 0;
            int bestCand = -1;
            if (i + 3 <= n) {
                int h = hash3(data, i);
                int cand = hashTable[h];
                if (cand != -1 && i - cand <= WINDOW) {
                    int matchLen = 0;
                    while (matchLen < MAX_MATCH && i + matchLen < n && data[cand + matchLen] == data[i + matchLen]) {
                        matchLen++;
                    }
                    if (matchLen >= MIN_MATCH) {
                        bestLen = matchLen;
                        bestCand = cand;
                    }
                }
                hashTable[h] = i;
            }
            Token t = new Token();
            if (bestLen >= MIN_MATCH) {
                t.isMatch = true;
                t.offset = i - bestCand;
                t.length = bestLen;
                tokens.add(t);
                i += bestLen;
            } else {
                t.isMatch = false;
                t.literal = data[i];
                tokens.add(t);
                i += 1;
            }
        }
        return tokens;
    }

    static byte[] decode(List<Token> tokens, int expectedLen) {
        byte[] out = new byte[expectedLen];
        int len = 0;
        for (Token t : tokens) {
            if (t.isMatch) {
                int start = len - t.offset;
                for (int k = 0; k < t.length; k++) {
                    out[len] = out[start + k];
                    len++;
                }
            } else {
                out[len] = t.literal;
                len++;
            }
        }
        return out;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 5_000_000;

        byte[] pattern = new byte[64];
        for (int i = 0; i < 64; i++) pattern[i] = (byte) ((i * 7 + 3) % 251);
        byte[] data = new byte[n];
        for (int i = 0; i < n; i++) {
            byte v = pattern[i % 64];
            if (i % 97 == 0) v = (byte) (((v & 0xFF) + 1) % 256);
            data[i] = v;
        }

        List<Token> tokens = encode(data);
        byte[] decoded = decode(tokens, n);

        if (decoded.length != n) {
            System.err.println("self-check failed: roundtrip length mismatch");
            System.exit(1);
        }
        for (int i = 0; i < n; i++) {
            if (decoded[i] != data[i]) {
                System.err.println("self-check failed: roundtrip byte mismatch at " + i);
                System.exit(1);
            }
        }

        long compressedBytes = 0;
        for (Token t : tokens) {
            compressedBytes += t.isMatch ? 4 : 2;
        }

        System.out.println(compressedBytes);
    }
}
