public class Sha256 {
    static final int[] K = {
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    };

    static byte[] sha256(byte[] msg) {
        int[] h = {
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
        };

        long bitLen = (long) msg.length * 8;
        int paddedLen = ((msg.length + 9 + 63) / 64) * 64;
        byte[] msg2 = new byte[paddedLen];
        System.arraycopy(msg, 0, msg2, 0, msg.length);
        msg2[msg.length] = (byte) 0x80;
        for (int i = 0; i < 8; i++) {
            msg2[paddedLen - 1 - i] = (byte) (bitLen >>> (8 * i));
        }

        int[] w = new int[64];
        for (int chunk = 0; chunk < paddedLen; chunk += 64) {
            for (int i = 0; i < 16; i++) {
                int base = chunk + i * 4;
                w[i] = ((msg2[base] & 0xFF) << 24) | ((msg2[base + 1] & 0xFF) << 16)
                    | ((msg2[base + 2] & 0xFF) << 8) | (msg2[base + 3] & 0xFF);
            }
            for (int i = 16; i < 64; i++) {
                int s0 = Integer.rotateRight(w[i - 15], 7) ^ Integer.rotateRight(w[i - 15], 18) ^ (w[i - 15] >>> 3);
                int s1 = Integer.rotateRight(w[i - 2], 17) ^ Integer.rotateRight(w[i - 2], 19) ^ (w[i - 2] >>> 10);
                w[i] = w[i - 16] + s0 + w[i - 7] + s1;
            }

            int a = h[0], b = h[1], c = h[2], d = h[3];
            int e = h[4], f = h[5], g = h[6], hh = h[7];

            for (int i = 0; i < 64; i++) {
                int s1 = Integer.rotateRight(e, 6) ^ Integer.rotateRight(e, 11) ^ Integer.rotateRight(e, 25);
                int ch = (e & f) ^ (~e & g);
                int temp1 = hh + s1 + ch + K[i] + w[i];
                int s0 = Integer.rotateRight(a, 2) ^ Integer.rotateRight(a, 13) ^ Integer.rotateRight(a, 22);
                int maj = (a & b) ^ (a & c) ^ (b & c);
                int temp2 = s0 + maj;
                hh = g; g = f; f = e; e = d + temp1;
                d = c; c = b; b = a; a = temp1 + temp2;
            }

            h[0] += a; h[1] += b; h[2] += c; h[3] += d;
            h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
        }

        byte[] out = new byte[32];
        for (int i = 0; i < 8; i++) {
            out[i * 4] = (byte) (h[i] >>> 24);
            out[i * 4 + 1] = (byte) (h[i] >>> 16);
            out[i * 4 + 2] = (byte) (h[i] >>> 8);
            out[i * 4 + 3] = (byte) h[i];
        }
        return out;
    }

    static String toHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 2_000_000;

        String emptyHash = toHex(sha256(new byte[0]));
        if (!emptyHash.equals("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")) {
            System.err.println("self-check failed: SHA256(\"\") mismatch: got " + emptyHash);
            System.exit(1);
        }

        String abcHash = toHex(sha256("abc".getBytes()));
        if (!abcHash.equals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")) {
            System.err.println("self-check failed: SHA256(\"abc\") mismatch: got " + abcHash);
            System.exit(1);
        }

        byte[] buf = new byte[n];
        for (int i = 0; i < n; i++) {
            buf[i] = (byte) ((i * 131 + 7) % 256);
        }

        System.out.println(toHex(sha256(buf)));
    }
}
