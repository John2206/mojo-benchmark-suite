import java.util.Arrays;

public class Sort {
    static int lcgState;

    static long lcgNext() {
        lcgState = (lcgState * 1103515245 + 12345) & 0x7fffffff;
        return lcgState;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 2000000;
        lcgState = 42;
        long[] arr = new long[n];
        for (int i = 0; i < n; i++) arr[i] = lcgNext();

        Arrays.sort(arr);

        for (int i = 1; i < n; i++) {
            if (arr[i - 1] > arr[i]) {
                System.err.println("self-check failed: array not sorted");
                System.exit(1);
            }
        }
        System.out.println(arr[n - 1]);
    }
}
