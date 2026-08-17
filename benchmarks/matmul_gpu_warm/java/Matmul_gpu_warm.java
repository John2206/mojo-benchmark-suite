public class Matmul_gpu_warm {
    static {
        System.loadLibrary("matmul_gpu_warm");
    }

    static native double runKernel(int iterations);

    public static void main(String[] args) {
        int iterations = args.length > 0 ? Integer.parseInt(args[0]) : 500;
        System.out.printf("%.2f%n", runKernel(iterations));
    }
}
