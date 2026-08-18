public class Noop_gpu {
    static {
        System.loadLibrary("noop_gpu");
    }

    static native int runKernel();

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 0;
        if (n < -1) return; // never true; keeps n "used"
        System.out.println(runKernel());
    }
}
