public class Nbody {
    static final int STEPS = 100;
    static final double G = 1e-4;
    static final double DT = 1e-3;

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 300;

        double[] mass = new double[n];
        double[] px = new double[n], py = new double[n], pz = new double[n];
        double[] vx = new double[n], vy = new double[n], vz = new double[n];

        for (int i = 0; i < n; i++) {
            mass[i] = 1.0 + i;
            px[i] = i * 0.1;
            py[i] = i * 0.2;
            pz[i] = i * 0.3;
        }

        for (int s = 0; s < STEPS; s++) {
            for (int i = 0; i < n; i++) {
                for (int j = i + 1; j < n; j++) {
                    double dx = px[j] - px[i];
                    double dy = py[j] - py[i];
                    double dz = pz[j] - pz[i];
                    double dist2 = dx * dx + dy * dy + dz * dz + 1e-9;
                    double invDist3 = 1.0 / (dist2 * Math.sqrt(dist2));
                    double fx = G * dx * invDist3;
                    double fy = G * dy * invDist3;
                    double fz = G * dz * invDist3;
                    vx[i] += fx * mass[j] * DT;
                    vy[i] += fy * mass[j] * DT;
                    vz[i] += fz * mass[j] * DT;
                    vx[j] -= fx * mass[i] * DT;
                    vy[j] -= fy * mass[i] * DT;
                    vz[j] -= fz * mass[i] * DT;
                }
            }
            for (int i = 0; i < n; i++) {
                px[i] += vx[i] * DT;
                py[i] += vy[i] * DT;
                pz[i] += vz[i] * DT;
            }
        }

        double momentumX = 0.0;
        for (int i = 0; i < n; i++) momentumX += mass[i] * vx[i];
        if (Math.abs(momentumX) > 1e-6) {
            System.err.println("self-check failed: momentum not conserved (" + momentumX + ")");
            System.exit(1);
        }

        System.out.printf("%.6f %.6f %.6f%n", px[0], py[0], pz[0]);
    }
}
