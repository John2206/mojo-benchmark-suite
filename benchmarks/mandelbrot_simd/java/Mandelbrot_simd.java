import jdk.incubator.vector.DoubleVector;
import jdk.incubator.vector.LongVector;
import jdk.incubator.vector.VectorMask;
import jdk.incubator.vector.VectorOperators;
import jdk.incubator.vector.VectorSpecies;

public class Mandelbrot_simd {
    static final int MAX_ITER = 1000;
    static final VectorSpecies<Double> SPECIES_D = DoubleVector.SPECIES_256;
    static final VectorSpecies<Long> SPECIES_L = LongVector.SPECIES_256;
    static final int W = SPECIES_D.length();

    static long[] escapeCountsRow(double[] cr, double ci) {
        DoubleVector zr = DoubleVector.zero(SPECIES_D);
        DoubleVector zi = DoubleVector.zero(SPECIES_D);
        DoubleVector crVec = DoubleVector.fromArray(SPECIES_D, cr, 0);
        DoubleVector ciVec = DoubleVector.broadcast(SPECIES_D, ci);
        LongVector iters = LongVector.zero(SPECIES_L);
        VectorMask<Long> active = SPECIES_L.maskAll(true);

        for (int i = 0; i < MAX_ITER; i++) {
            DoubleVector zr2 = zr.mul(zr);
            DoubleVector zi2 = zi.mul(zi);
            DoubleVector mag2 = zr2.add(zi2);
            VectorMask<Double> cmpD = mag2.compare(VectorOperators.LE, 4.0);
            VectorMask<Long> still = cmpD.cast(SPECIES_L).and(active);

            if (!still.anyTrue()) break;

            DoubleVector newZi = zr.mul(zi).mul(2.0).add(ciVec);
            DoubleVector newZr = zr2.sub(zi2).add(crVec);
            VectorMask<Double> stillD = still.cast(SPECIES_D);
            zr = zr.blend(newZr, stillD);
            zi = zi.blend(newZi, stillD);

            iters = iters.add(1, still);
            active = still;
        }

        long[] out = new long[W];
        iters.intoArray(out, 0);
        return out;
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 800;

        long[] originIters = escapeCountsRow(new double[]{0.0, 0.0, 0.0, 0.0}, 0.0);
        for (long it : originIters) {
            if (it != MAX_ITER) {
                System.err.println("self-check failed: origin should never escape");
                System.exit(1);
            }
        }

        long[] farIters = escapeCountsRow(new double[]{2.0, 2.0, 2.0, 2.0}, 2.0);
        for (long it : farIters) {
            if (it >= MAX_ITER) {
                System.err.println("self-check failed: far point should escape quickly");
                System.exit(1);
            }
        }

        int groups = n / W;
        long count = 0;
        for (int py = 0; py < n; py++) {
            double ci = -1.5 + 3.0 * py / n;
            for (int gx = 0; gx < groups; gx++) {
                double[] cr = new double[W];
                for (int lane = 0; lane < W; lane++) {
                    int px = gx * W + lane;
                    cr[lane] = -2.0 + 3.0 * px / n;
                }
                long[] iters = escapeCountsRow(cr, ci);
                for (long it : iters) {
                    if (it == MAX_ITER) count++;
                }
            }
        }

        System.out.println(count);
    }
}
