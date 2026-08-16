import sys

STEPS = 100
G = 1e-4
DT = 1e-3


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300

    mass = [1.0 + i for i in range(n)]
    px = [i * 0.1 for i in range(n)]
    py = [i * 0.2 for i in range(n)]
    pz = [i * 0.3 for i in range(n)]
    vx = [0.0] * n
    vy = [0.0] * n
    vz = [0.0] * n

    for _ in range(STEPS):
        for i in range(n):
            for j in range(i + 1, n):
                dx = px[j] - px[i]
                dy = py[j] - py[i]
                dz = pz[j] - pz[i]
                dist2 = dx * dx + dy * dy + dz * dz + 1e-9
                inv_dist3 = 1.0 / (dist2 * dist2 ** 0.5)
                fx = G * dx * inv_dist3
                fy = G * dy * inv_dist3
                fz = G * dz * inv_dist3
                vx[i] += fx * mass[j] * DT
                vy[i] += fy * mass[j] * DT
                vz[i] += fz * mass[j] * DT
                vx[j] -= fx * mass[i] * DT
                vy[j] -= fy * mass[i] * DT
                vz[j] -= fz * mass[i] * DT
        for i in range(n):
            px[i] += vx[i] * DT
            py[i] += vy[i] * DT
            pz[i] += vz[i] * DT

    momentum_x = sum(mass[i] * vx[i] for i in range(n))
    assert abs(momentum_x) < 1e-6, f"self-check failed: momentum not conserved ({momentum_x})"

    print(f"{px[0]:.6f} {py[0]:.6f} {pz[0]:.6f}")


if __name__ == "__main__":
    main()
