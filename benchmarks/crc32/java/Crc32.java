public class Crc32 {
    static int[] buildTable() {
        int[] table = new int[256];
        for (int i = 0; i < 256; i++) {
            int crc = i;
            for (int j = 0; j < 8; j++) {
                if ((crc & 1) != 0) {
                    crc = (crc >>> 1) ^ 0xEDB88320;
                } else {
                    crc >>>= 1;
                }
            }
            table[i] = crc;
        }
        return table;
    }

    static int crc32Compute(int[] table, byte[] data) {
        int crc = 0xFFFFFFFF;
        for (byte b : data) {
            crc = table[(crc ^ b) & 0xFF] ^ (crc >>> 8);
        }
        return crc ^ 0xFFFFFFFF;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 50_000_000;

        int[] table = buildTable();

        if (crc32Compute(table, new byte[0]) != 0x00000000) {
            System.err.println("self-check failed: CRC32(\"\") mismatch");
            System.exit(1);
        }
        if (crc32Compute(table, "123456789".getBytes()) != 0xCBF43926) {
            System.err.println("self-check failed: CRC32(\"123456789\") mismatch");
            System.exit(1);
        }

        byte[] buf = new byte[n];
        for (int i = 0; i < n; i++) {
            buf[i] = (byte) ((i * 131 + 7) % 256);
        }

        int result = crc32Compute(table, buf);
        System.out.println(String.format("%08x", result));
    }
}
