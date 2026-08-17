public class Montecarlo {
    static final double PI = 3.14159265358979323846;
    static int lcgState;

    static double lcgNext() {
        lcgState = (lcgState * 1103515245 + 12345) & 0x7fffffff;
        return lcgState / 2147483648.0;
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 50_000_000L;

        lcgState = 1;
        long inside = 0;
        for (long i = 0; i < n; i++) {
            double x = lcgNext();
            double y = lcgNext();
            if (x * x + y * y <= 1.0) inside++;
        }

        double piEstimate = 4.0 * inside / (double) n;
        double tolerance = 10.0 / Math.sqrt((double) n);

        if (Math.abs(piEstimate - PI) >= tolerance) {
            System.err.println("self-check failed: pi estimate out of tolerance: " + piEstimate);
            System.exit(1);
        }

        System.out.printf("%.6f%n", piEstimate);
    }
}
