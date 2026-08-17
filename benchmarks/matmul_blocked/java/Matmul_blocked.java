public class Matmul_blocked {
    static final int BLOCK = 32;

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 600;

        double[] a = new double[n * n];
        double[] b = new double[n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                a[i * n + j] = (i * 3 + j) % 13;
                b[i * n + j] = (i + j * 2) % 17;
            }
        }

        double[] c = new double[n * n];
        for (int ii = 0; ii < n; ii += BLOCK) {
            int iMax = Math.min(ii + BLOCK, n);
            for (int kk = 0; kk < n; kk += BLOCK) {
                int kMax = Math.min(kk + BLOCK, n);
                for (int jj = 0; jj < n; jj += BLOCK) {
                    int jMax = Math.min(jj + BLOCK, n);
                    for (int i = ii; i < iMax; i++) {
                        for (int k = kk; k < kMax; k++) {
                            double aik = a[i * n + k];
                            for (int j = jj; j < jMax; j++) {
                                c[i * n + j] += aik * b[k * n + j];
                            }
                        }
                    }
                }
            }
        }

        double expected = 0.0;
        for (int k = 0; k < n; k++) expected += a[k] * b[k * n];
        if (c[0] != expected) {
            System.err.println("self-check failed: c[0][0] mismatch");
            System.exit(1);
        }

        System.out.printf("%.2f%n", c[(n - 1) * n + (n - 1)]);
    }
}
