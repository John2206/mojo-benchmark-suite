public class Matmul {
    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 400;

        double[][] a = new double[n][n];
        double[][] b = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                a[i][j] = (i * 3 + j) % 13;
                b[i][j] = (i + j * 2) % 17;
            }
        }

        double[][] c = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                double aik = a[i][k];
                for (int j = 0; j < n; j++) {
                    c[i][j] += aik * b[k][j];
                }
            }
        }

        double expected = 0.0;
        for (int k = 0; k < n; k++) expected += a[0][k] * b[k][0];
        if (c[0][0] != expected) {
            System.err.println("self-check failed: c[0][0] mismatch");
            System.exit(1);
        }

        System.out.printf("%.2f%n", c[n - 1][n - 1]);
    }
}
