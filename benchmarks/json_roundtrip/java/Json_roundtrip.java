public class Json_roundtrip {
    static long parseInt(String s, int[] pos) {
        long val = 0;
        while (pos[0] < s.length() && Character.isDigit(s.charAt(pos[0]))) {
            val = val * 10 + (s.charAt(pos[0]) - '0');
            pos[0]++;
        }
        return val;
    }

    static double parseDecimal1(String s, int[] pos) {
        long whole = parseInt(s, pos);
        pos[0]++; // '.'
        int frac = s.charAt(pos[0]) - '0';
        pos[0]++;
        return whole + frac / 10.0;
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 200_000;

        StringBuilder sb = new StringBuilder((int) (n * 48 + 16));
        sb.append('[');
        for (long i = 0; i < n; i++) {
            if (i > 0) sb.append(',');
            sb.append("{\"id\":").append(i)
              .append(",\"name\":\"item").append(i)
              .append("\",\"value\":").append(String.format("%.1f", i * 0.5))
              .append('}');
        }
        sb.append(']');
        String json = sb.toString();

        int[] pos = {1}; // skip '['
        long idSum = 0;
        long decodedCount = 0;
        while (json.charAt(pos[0]) != ']') {
            pos[0]++; // '{'
            pos[0] += "\"id\":".length();
            long id = parseInt(json, pos);
            pos[0] += ",\"name\":\"item".length();
            parseInt(json, pos); // skip digits in name, not re-checked
            pos[0] += "\",\"value\":".length();
            double value = parseDecimal1(json, pos);
            pos[0]++; // '}'
            if (pos[0] < json.length() && json.charAt(pos[0]) == ',') pos[0]++;

            if (value != id * 0.5) {
                System.err.println("self-check failed: decoded value mismatch for id " + id);
                System.exit(1);
            }
            idSum += id;
            decodedCount++;
        }

        long expectedSum = n * (n - 1) / 2;
        if (idSum != expectedSum || decodedCount != n) {
            System.err.println("self-check failed: id sum or count mismatch");
            System.exit(1);
        }

        System.out.println(idSum);
    }
}
