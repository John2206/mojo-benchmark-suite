import java.util.HashMap;
import java.util.Map;

public class Wordcount {
    static final String[] VOCAB = {
        "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
        "he", "was", "for", "on", "are", "as", "with", "his", "they", "at"
    };
    static int lcgState;

    static long lcgNext() {
        lcgState = (lcgState * 1103515245 + 12345) & 0x7fffffff;
        return lcgState;
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 2_000_000;

        lcgState = 42;
        Map<String, Long> counts = new HashMap<>();
        for (long k = 0; k < n; k++) {
            String word = VOCAB[(int) (lcgNext() % VOCAB.length)];
            counts.merge(word, 1L, Long::sum);
        }

        long total = 0;
        for (long c : counts.values()) total += c;
        if (total != n) {
            System.err.println("self-check failed: counts do not sum to n");
            System.exit(1);
        }

        System.out.println(counts.size());
    }
}
