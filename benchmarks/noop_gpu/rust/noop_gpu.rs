// Honest GPU-startup baseline: open a CUDA context and allocate/free one
// element, the same Driver API path mandelbrot_gpu/matmul_gpu use, minus the
// kernel launch. No CUDA crate in std -- FFI against the system's libcuda.so,
// same as every other GPU benchmark in this repo.
use std::env;
use std::ffi::c_void;
use std::os::raw::{c_int, c_uint};
use std::ptr;

type CUresult = c_int;
type CUdevice = c_int;
type CUcontext = *mut c_void;
type CUdeviceptr = u64;

#[link(name = "cuda")]
extern "C" {
    fn cuInit(flags: c_uint) -> CUresult;
    fn cuDeviceGet(device: *mut CUdevice, ordinal: c_int) -> CUresult;
    fn cuCtxCreate_v2(pctx: *mut CUcontext, flags: c_uint, dev: CUdevice) -> CUresult;
    fn cuMemAlloc_v2(dptr: *mut CUdeviceptr, bytesize: usize) -> CUresult;
    fn cuMemFree_v2(dptr: CUdeviceptr) -> CUresult;
    fn cuCtxDestroy_v2(ctx: CUcontext) -> CUresult;
}

fn check(result: CUresult, what: &str) {
    if result != 0 {
        panic!("CUDA driver error {} during {}", result, what);
    }
}

fn main() {
    let _n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(0);

    unsafe {
        check(cuInit(0), "cuInit");
        let mut device: CUdevice = 0;
        check(cuDeviceGet(&mut device, 0), "cuDeviceGet");
        let mut ctx: CUcontext = ptr::null_mut();
        check(cuCtxCreate_v2(&mut ctx, 0, device), "cuCtxCreate_v2");

        let mut d_ptr: CUdeviceptr = 0;
        check(cuMemAlloc_v2(&mut d_ptr, std::mem::size_of::<i32>()), "cuMemAlloc_v2");
        check(cuMemFree_v2(d_ptr), "cuMemFree_v2");

        check(cuCtxDestroy_v2(ctx), "cuCtxDestroy_v2");
    }

    println!("0");
}
