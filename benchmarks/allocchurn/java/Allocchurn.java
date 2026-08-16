public class Allocchurn {
    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 5_000_000;

        long total = 0;
        for (long i = 0; i < n; i++) {
            int[] arr = new int[64];
            for (int j = 0; j < 64; j++) arr[j] = j;
            long sum = 0;
            for (int j = 0; j < 64; j++) sum += arr[j];
            total += sum;
        }

        if (total != n * 2016L) {
            System.err.println("self-check failed: total mismatch");
            System.exit(1);
        }

        System.out.println(total);
    }
}
