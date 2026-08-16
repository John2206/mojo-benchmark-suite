import java.util.Arrays;
import java.util.Random;

public class Sort {
    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 2000000;
        Random rnd = new Random(42);
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = rnd.nextInt();

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
