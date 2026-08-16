public class Fib {
    static long fib(long n) {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 32;
        if (fib(10) != 55) {
            System.err.println("self-check failed: fib(10) != 55");
            System.exit(1);
        }
        System.out.println(fib(n));
    }
}
