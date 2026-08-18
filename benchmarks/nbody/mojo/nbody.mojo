from std.sys import argv
from std.math import abs, sqrt

comptime STEPS = 100
comptime G: Float64 = 1e-4
comptime DT: Float64 = 1e-3


def format6(value: Float64) -> String:
    var sign = "-" if value < 0.0 else ""
    var scaled = Int(abs(value) * 1000000.0 + 0.5)
    var whole = scaled // 1000000
    var frac = scaled % 1000000
    var frac_str = String(frac)
    while frac_str.byte_length() < 6:
        frac_str = "0" + frac_str
    return sign + String(whole) + "." + frac_str


def main() raises:
    var args = argv()
    var n = 300
    if len(args) > 1:
        n = atol(args[1])

    var mass = List[Float64](length=n, fill=0.0)
    var px = List[Float64](length=n, fill=0.0)
    var py = List[Float64](length=n, fill=0.0)
    var pz = List[Float64](length=n, fill=0.0)
    var vx = List[Float64](length=n, fill=0.0)
    var vy = List[Float64](length=n, fill=0.0)
    var vz = List[Float64](length=n, fill=0.0)

    for i in range(n):
        mass[i] = 1.0 + Float64(i)
        px[i] = Float64(i) * 0.1
        py[i] = Float64(i) * 0.2
        pz[i] = Float64(i) * 0.3

    for _ in range(STEPS):
        for i in range(n):
            for j in range(i + 1, n):
                var dx = px[j] - px[i]
                var dy = py[j] - py[i]
                var dz = pz[j] - pz[i]
                var dist2 = dx * dx + dy * dy + dz * dz + 1e-9
                var inv_dist3 = 1.0 / (dist2 * sqrt(dist2))
                var fx = G * dx * inv_dist3
                var fy = G * dy * inv_dist3
                var fz = G * dz * inv_dist3
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

    var momentum_x: Float64 = 0.0
    for i in range(n):
        momentum_x += mass[i] * vx[i]
    if abs(momentum_x) > 1e-6:
        raise Error("self-check failed: momentum not conserved")

    print(format6(px[0]) + " " + format6(py[0]) + " " + format6(pz[0]))
