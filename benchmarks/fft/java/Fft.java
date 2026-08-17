public class Fft {
    static long nextPow2(long n) {
        long p = 1;
        while (p < n) p <<= 1;
        return p;
    }

    static void fft(double[] re, double[] im, boolean invert) {
        int n = re.length;
        int j = 0;
        for (int i = 1; i < n; i++) {
            int bit = n >> 1;
            while ((j & bit) != 0) {
                j ^= bit;
                bit >>= 1;
            }
            j ^= bit;
            if (i < j) {
                double tr = re[i]; re[i] = re[j]; re[j] = tr;
                double ti = im[i]; im[i] = im[j]; im[j] = ti;
            }
        }

        for (int length = 2; length <= n; length <<= 1) {
            double ang = 2.0 * Math.PI / length * (invert ? 1.0 : -1.0);
            double wlenRe = Math.cos(ang);
            double wlenIm = Math.sin(ang);
            for (int i = 0; i < n; i += length) {
                double wRe = 1.0, wIm = 0.0;
                for (int k = i; k < i + length / 2; k++) {
                    double uRe = re[k], uIm = im[k];
                    double vRe = re[k + length / 2] * wRe - im[k + length / 2] * wIm;
                    double vIm = re[k + length / 2] * wIm + im[k + length / 2] * wRe;
                    re[k] = uRe + vRe;
                    im[k] = uIm + vIm;
                    re[k + length / 2] = uRe - vRe;
                    im[k + length / 2] = uIm - vIm;
                    double nwRe = wRe * wlenRe - wIm * wlenIm;
                    double nwIm = wRe * wlenIm + wIm * wlenRe;
                    wRe = nwRe;
                    wIm = nwIm;
                }
            }
        }

        if (invert) {
            for (int i = 0; i < n; i++) {
                re[i] /= n;
                im[i] /= n;
            }
        }
    }

    public static void main(String[] args) {
        long requested = args.length > 0 ? Long.parseLong(args[0]) : 1_048_576L;
        int n = (int) nextPow2(requested);

        double[] re = new double[n];
        double[] im = new double[n];
        double[] orig = new double[n];
        for (int i = 0; i < n; i++) {
            double v = (i % 7) - 3.0;
            re[i] = v;
            orig[i] = v;
        }

        fft(re, im, false);
        fft(re, im, true);

        double maxErr = 0.0;
        for (int i = 0; i < n; i++) {
            double err = Math.max(Math.abs(re[i] - orig[i]), Math.abs(im[i]));
            if (err > maxErr) maxErr = err;
        }

        if (maxErr >= 1e-6) {
            System.err.println("self-check failed: roundtrip reconstruction error too large: " + maxErr);
            System.exit(1);
        }

        System.out.println(maxErr);
    }
}
