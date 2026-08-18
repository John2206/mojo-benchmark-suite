from std.math import abs, ceildiv
from std.sys import argv, has_accelerator
from max.gpu.host import DeviceContext
from std.gpu import global_idx
from layout import TileTensor, TensorLayout, row_major

comptime BLOCK = 16


def format2(value: Float64) -> String:
    """Matches C's "%.2f" so all five languages print the same bytes."""
    var sign = "-" if value < 0.0 else ""
    var scaled = Int(abs(value) * 100.0 + 0.5)
    var whole = scaled // 100
    var frac = scaled % 100
    var frac_str = String(frac)
    while frac_str.byte_length() < 2:
        frac_str = "0" + frac_str
    return sign + String(whole) + "." + frac_str


def matmul_kernel[LT: TensorLayout](
    a: TileTensor[DType.float64, LT, MutAnyOrigin],
    b: TileTensor[DType.float64, LT, MutAnyOrigin],
    c: TileTensor[DType.float64, LT, MutAnyOrigin],
    n32: Int32,
):
    comptime assert a.flat_rank == 2, "expected 2D tensor"
    var n = Int(n32)
    var row = global_idx.y
    var col = global_idx.x
    if row < n and col < n:
        var acc: c.ElementType = 0.0
        for k in range(n):
            acc += a[row, k] * b[k, col]
        c[row, col] = acc


def main() raises:
    comptime assert has_accelerator(), "Requires a GPU"

    var args = argv()
    var n = 2048
    if len(args) > 1:
        n = atol(args[1])

    var ctx = DeviceContext()
    var layout = row_major(n, n)
    var a_buf = ctx.enqueue_create_buffer[DType.float64](n * n)
    var b_buf = ctx.enqueue_create_buffer[DType.float64](n * n)
    var c_buf = ctx.enqueue_create_buffer[DType.float64](n * n)

    with a_buf.map_to_host() as mapped_a:
        var a_host = TileTensor(mapped_a, layout)
        for i in range(n):
            for j in range(n):
                a_host[i, j] = rebind[a_host.ElementType](Float64((i * 3 + j) % 13))
    with b_buf.map_to_host() as mapped_b:
        var b_host = TileTensor(mapped_b, layout)
        for i in range(n):
            for j in range(n):
                b_host[i, j] = rebind[b_host.ElementType](Float64((i + j * 2) % 17))

    var a_tensor = TileTensor(a_buf, layout)
    var b_tensor = TileTensor(b_buf, layout)
    var c_tensor = TileTensor(c_buf, layout)

    comptime kernel = matmul_kernel[type_of(layout)]
    ctx.enqueue_function[kernel](
        a_tensor, b_tensor, c_tensor, Int32(n),
        grid_dim=(ceildiv(n, BLOCK), ceildiv(n, BLOCK)),
        block_dim=(BLOCK, BLOCK),
    )
    ctx.synchronize()

    var expected: Float64 = 0.0
    for k in range(n):
        expected += Float64(k % 13) * Float64(k % 17)

    with c_buf.map_to_host() as mapped_c:
        var c_host = TileTensor(mapped_c, layout)
        if Float64(c_host[0, 0]) != expected:
            raise Error("self-check failed: c[0][0] mismatch")
        print(format2(Float64(c_host[n - 1, n - 1])))
