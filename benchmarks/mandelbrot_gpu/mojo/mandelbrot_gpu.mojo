from std.math import ceildiv
from std.sys import argv, has_accelerator
from max.gpu.host import DeviceContext
from std.gpu import global_idx
from layout import TileTensor, TensorLayout, row_major

comptime MAX_ITER = 1000
comptime BLOCK = 16


def escape_iters_host(cr: Float64, ci: Float64) -> Int:
    var zr: Float64 = 0.0
    var zi: Float64 = 0.0
    var i = 0
    while i < MAX_ITER:
        var zr2 = zr * zr
        var zi2 = zi * zi
        if zr2 + zi2 > 4.0:
            break
        var new_zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        zi = new_zi
        i += 1
    return i


def mandelbrot_kernel[LT: TensorLayout](
    output: TileTensor[DType.int32, LT, MutAnyOrigin],
    n32: Int32,
):
    comptime assert output.flat_rank == 2, "expected 2D tensor"
    var n = Int(n32)
    var row = global_idx.y
    var col = global_idx.x
    if row < n and col < n:
        var ci = -1.5 + 3.0 * Float64(row) / Float64(n)
        var cr = -2.0 + 3.0 * Float64(col) / Float64(n)
        var zr: Float64 = 0.0
        var zi: Float64 = 0.0
        var iters: Int32 = 0
        while iters < MAX_ITER:
            var zr2 = zr * zr
            var zi2 = zi * zi
            if zr2 + zi2 > 4.0:
                break
            var new_zi = 2.0 * zr * zi + ci
            zr = zr2 - zi2 + cr
            zi = new_zi
            iters += 1
        output[row, col] = rebind[output.ElementType](iters)


def main() raises:
    comptime assert has_accelerator(), "Requires a GPU"

    var args = argv()
    var n = 4096
    if len(args) > 1:
        n = atol(args[1])

    if escape_iters_host(0.0, 0.0) != MAX_ITER:
        raise Error("self-check failed: origin should never escape")
    if escape_iters_host(2.0, 2.0) >= MAX_ITER:
        raise Error("self-check failed: far point should escape quickly")

    var ctx = DeviceContext()
    var layout = row_major(n, n)
    var out_buf = ctx.enqueue_create_buffer[DType.int32](n * n)
    var out_tensor = TileTensor(out_buf, layout)

    comptime kernel = mandelbrot_kernel[type_of(layout)]
    ctx.enqueue_function[kernel](
        out_tensor, Int32(n),
        grid_dim=(ceildiv(n, BLOCK), ceildiv(n, BLOCK)),
        block_dim=(BLOCK, BLOCK),
    )
    ctx.synchronize()

    var count = 0
    with out_buf.map_to_host() as mapped:
        var host_tensor = TileTensor(mapped, layout)
        for row in range(n):
            for col in range(n):
                if Int(host_tensor[row, col]) == MAX_ITER:
                    count += 1

    print(count)
