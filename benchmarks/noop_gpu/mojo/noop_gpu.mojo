from std.sys import argv, has_accelerator
from max.gpu.host import DeviceContext


def main() raises:
    comptime assert has_accelerator(), "Requires a GPU"

    var args = argv()
    var n = 0
    if len(args) > 1:
        n = atol(args[1])
    _ = n

    var ctx = DeviceContext()
    var buf = ctx.enqueue_create_buffer[DType.int32](1)
    ctx.synchronize()
    _ = buf^

    print(0)
