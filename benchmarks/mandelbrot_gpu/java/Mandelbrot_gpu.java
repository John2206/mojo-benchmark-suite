public class Mandelbrot_gpu {
    static {
        System.loadLibrary("mandelbrot_gpu");
    }

    static native long runKernel(int n);

    static final int MAX_ITER = 1000;

    static int escapeIters(double cr, double ci) {
        double zr = 0.0, zi = 0.0;
        int i = 0;
        while (i < MAX_ITER) {
            double zr2 = zr * zr, zi2 = zi * zi;
            if (zr2 + zi2 > 4.0) break;
            double newZi = 2.0 * zr * zi + ci;
            zr = zr2 - zi2 + cr;
            zi = newZi;
            i++;
        }
        return i;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 4096;

        if (escapeIters(0.0, 0.0) != MAX_ITER) {
            System.err.println("self-check failed: origin should never escape");
            System.exit(1);
        }
        if (escapeIters(2.0, 2.0) >= MAX_ITER) {
            System.err.println("self-check failed: far point should escape quickly");
            System.exit(1);
        }

        System.out.println(runKernel(n));
    }
}
