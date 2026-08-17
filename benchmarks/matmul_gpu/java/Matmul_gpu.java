public class Matmul_gpu {
    static {
        System.loadLibrary("matmul_gpu");
    }

    static native double runKernel(int n);

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 2048;
        System.out.printf("%.2f%n", runKernel(n));
    }
}
