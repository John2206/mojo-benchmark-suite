public class Base64 {
    static final String ENC_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    static String encode(byte[] data) {
        int len = data.length;
        StringBuilder out = new StringBuilder(((len + 2) / 3) * 4);
        int i = 0;
        while (i + 3 <= len) {
            int b0 = data[i] & 0xFF, b1 = data[i + 1] & 0xFF, b2 = data[i + 2] & 0xFF;
            out.append(ENC_TABLE.charAt(b0 >> 2));
            out.append(ENC_TABLE.charAt(((b0 & 0x03) << 4) | (b1 >> 4)));
            out.append(ENC_TABLE.charAt(((b1 & 0x0F) << 2) | (b2 >> 6)));
            out.append(ENC_TABLE.charAt(b2 & 0x3F));
            i += 3;
        }
        int rem = len - i;
        if (rem == 1) {
            int b0 = data[i] & 0xFF;
            out.append(ENC_TABLE.charAt(b0 >> 2));
            out.append(ENC_TABLE.charAt((b0 & 0x03) << 4));
            out.append("==");
        } else if (rem == 2) {
            int b0 = data[i] & 0xFF, b1 = data[i + 1] & 0xFF;
            out.append(ENC_TABLE.charAt(b0 >> 2));
            out.append(ENC_TABLE.charAt(((b0 & 0x03) << 4) | (b1 >> 4)));
            out.append(ENC_TABLE.charAt((b1 & 0x0F) << 2));
            out.append('=');
        }
        return out.toString();
    }

    static int decValue(char c) {
        if (c >= 'A' && c <= 'Z') return c - 'A';
        if (c >= 'a' && c <= 'z') return c - 'a' + 26;
        if (c >= '0' && c <= '9') return c - '0' + 52;
        if (c == '+') return 62;
        if (c == '/') return 63;
        return -1;
    }

    static byte[] decode(String enc) {
        byte[] out = new byte[(enc.length() / 4) * 3];
        int j = 0;
        for (int i = 0; i < enc.length(); i += 4) {
            int v0 = decValue(enc.charAt(i));
            int v1 = decValue(enc.charAt(i + 1));
            int v2 = enc.charAt(i + 2) == '=' ? -2 : decValue(enc.charAt(i + 2));
            int v3 = enc.charAt(i + 3) == '=' ? -2 : decValue(enc.charAt(i + 3));
            out[j++] = (byte) ((v0 << 2) | (v1 >> 4));
            if (v2 != -2) {
                out[j++] = (byte) (((v1 & 0x0F) << 4) | (v2 >> 2));
                if (v3 != -2) {
                    out[j++] = (byte) (((v2 & 0x03) << 6) | v3);
                }
            }
        }
        byte[] trimmed = new byte[j];
        System.arraycopy(out, 0, trimmed, 0, j);
        return trimmed;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 20_000_000;

        if (!encode(new byte[0]).equals("")) {
            System.err.println("self-check failed: base64(\"\") mismatch");
            System.exit(1);
        }
        if (!encode("f".getBytes()).equals("Zg==")) {
            System.err.println("self-check failed: base64(\"f\") mismatch");
            System.exit(1);
        }
        if (!encode("fo".getBytes()).equals("Zm8=")) {
            System.err.println("self-check failed: base64(\"fo\") mismatch");
            System.exit(1);
        }
        if (!encode("foo".getBytes()).equals("Zm9v")) {
            System.err.println("self-check failed: base64(\"foo\") mismatch");
            System.exit(1);
        }

        byte[] buf = new byte[n];
        for (int i = 0; i < n; i++) {
            buf[i] = (byte) ((i * 131 + 7) % 256);
        }

        String encoded = encode(buf);
        byte[] decoded = decode(encoded);
        if (decoded.length != n) {
            System.err.println("self-check failed: roundtrip mismatch");
            System.exit(1);
        }
        for (int i = 0; i < n; i++) {
            if (decoded[i] != buf[i]) {
                System.err.println("self-check failed: roundtrip mismatch");
                System.exit(1);
            }
        }

        long sum = 0;
        for (int i = 0; i < encoded.length(); i++) {
            sum += encoded.charAt(i);
        }
        System.out.println(sum);
    }
}
