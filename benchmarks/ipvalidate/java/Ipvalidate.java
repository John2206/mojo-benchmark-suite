public class Ipvalidate {
    static int lcgState;

    static long lcgNext() {
        lcgState = (lcgState * 1103515245 + 12345) & 0x7fffffff;
        return lcgState;
    }

    static Integer parseGroup(String s) {
        if (s.isEmpty() || s.length() > 3) return null;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') return null;
        }
        int val = Integer.parseInt(s);
        return val <= 255 ? val : null;
    }

    static boolean isValidIp(String s) {
        int parts = 0;
        int start = 0;
        int len = s.length();
        for (int i = 0; i <= len; i++) {
            if (i == len || s.charAt(i) == '.') {
                String group = s.substring(start, i);
                if (parseGroup(group) == null) return false;
                parts++;
                start = i + 1;
            }
        }
        return parts == 4;
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 2_000_000;

        if (!isValidIp("192.168.1.1")) {
            System.err.println("self-check failed: known-valid IP rejected");
            System.exit(1);
        }
        if (isValidIp("999.1.1.1")) {
            System.err.println("self-check failed: known-invalid IP accepted");
            System.exit(1);
        }
        if (isValidIp("1.2.3")) {
            System.err.println("self-check failed: known-invalid IP accepted");
            System.exit(1);
        }

        lcgState = 42;
        long valid = 0;
        for (long i = 0; i < n; i++) {
            long maxVal = lcgNext() % 10 < 7 ? 255 : 999;
            long a = lcgNext() % (maxVal + 1);
            long b = lcgNext() % (maxVal + 1);
            long c = lcgNext() % (maxVal + 1);
            long d = lcgNext() % (maxVal + 1);
            String s = a + "." + b + "." + c + "." + d;
            if (isValidIp(s)) valid++;
        }

        System.out.println(valid);
    }
}
