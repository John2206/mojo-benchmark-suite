// No CUDA crate exists in std, and this repo keeps every Rust benchmark a
// single `rustc -O` compile with zero external dependencies -- so this talks
// to the CUDA Driver API directly via FFI against the system's libcuda.so.
use std::env;
use std::ffi::{c_void, CString};
use std::fs;
use std::os::raw::{c_char, c_int, c_uint};
use std::path::PathBuf;
use std::ptr;

type CUresult = c_int;
type CUdevice = c_int;
type CUcontext = *mut c_void;
type CUmodule = *mut c_void;
type CUfunction = *mut c_void;
type CUdeviceptr = u64;
type CUstream = *mut c_void;

#[link(name = "cuda")]
extern "C" {
    fn cuInit(flags: c_uint) -> CUresult;
    fn cuDeviceGet(device: *mut CUdevice, ordinal: c_int) -> CUresult;
    fn cuCtxCreate_v2(pctx: *mut CUcontext, flags: c_uint, dev: CUdevice) -> CUresult;
    fn cuModuleLoadData(module: *mut CUmodule, image: *const c_void) -> CUresult;
    fn cuModuleGetFunction(hfunc: *mut CUfunction, hmod: CUmodule, name: *const c_char) -> CUresult;
    fn cuMemAlloc_v2(dptr: *mut CUdeviceptr, bytesize: usize) -> CUresult;
    fn cuMemcpyDtoH_v2(dst: *mut c_void, src: CUdeviceptr, byte_count: usize) -> CUresult;
    #[allow(dead_code)]
    fn cuMemcpyHtoD_v2(dst: CUdeviceptr, src: *const c_void, byte_count: usize) -> CUresult;
    fn cuLaunchKernel(
        f: CUfunction,
        grid_dim_x: c_uint, grid_dim_y: c_uint, grid_dim_z: c_uint,
        block_dim_x: c_uint, block_dim_y: c_uint, block_dim_z: c_uint,
        shared_mem_bytes: c_uint,
        stream: CUstream,
        kernel_params: *mut *mut c_void,
        extra: *mut *mut c_void,
    ) -> CUresult;
    fn cuMemFree_v2(dptr: CUdeviceptr) -> CUresult;
    fn cuCtxDestroy_v2(ctx: CUcontext) -> CUresult;
}

fn check(result: CUresult, what: &str) {
    if result != 0 {
        panic!("CUDA driver error {} during {}", result, what);
    }
}

const MAX_ITER: u32 = 1000;
const BLOCK: u32 = 16;

fn escape_iters_host(cr: f64, ci: f64) -> u32 {
    let mut zr = 0.0f64;
    let mut zi = 0.0f64;
    let mut i = 0;
    while i < MAX_ITER {
        let zr2 = zr * zr;
        let zi2 = zi * zi;
        if zr2 + zi2 > 4.0 {
            break;
        }
        let new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
        i += 1;
    }
    i
}

fn ptx_path() -> PathBuf {
    let mut path = env::current_exe().expect("current_exe failed");
    path.set_file_name("mandelbrot_gpu.ptx");
    path
}

fn main() {
    let n: i32 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(4096);

    assert_eq!(escape_iters_host(0.0, 0.0), MAX_ITER, "self-check failed: origin should never escape");
    assert!(escape_iters_host(2.0, 2.0) < MAX_ITER, "self-check failed: far point should escape quickly");

    unsafe {
        check(cuInit(0), "cuInit");
        let mut device: CUdevice = 0;
        check(cuDeviceGet(&mut device, 0), "cuDeviceGet");
        let mut ctx: CUcontext = ptr::null_mut();
        check(cuCtxCreate_v2(&mut ctx, 0, device), "cuCtxCreate_v2");

        let ptx = fs::read_to_string(ptx_path()).expect("failed to read PTX file");
        let ptx_c = CString::new(ptx).expect("PTX contains NUL byte");
        let mut module: CUmodule = ptr::null_mut();
        check(cuModuleLoadData(&mut module, ptx_c.as_ptr() as *const c_void), "cuModuleLoadData");

        let kernel_name = CString::new("mandelbrot_kernel").unwrap();
        let mut func: CUfunction = ptr::null_mut();
        check(cuModuleGetFunction(&mut func, module, kernel_name.as_ptr()), "cuModuleGetFunction");

        let bytes = (n as usize) * (n as usize) * std::mem::size_of::<i32>();
        let mut d_output: CUdeviceptr = 0;
        check(cuMemAlloc_v2(&mut d_output, bytes), "cuMemAlloc_v2");

        let grid = ((n as u32 + BLOCK - 1) / BLOCK, (n as u32 + BLOCK - 1) / BLOCK);
        let mut n_arg = n;
        let mut params: [*mut c_void; 2] = [
            &mut d_output as *mut CUdeviceptr as *mut c_void,
            &mut n_arg as *mut i32 as *mut c_void,
        ];
        check(
            cuLaunchKernel(
                func,
                grid.0, grid.1, 1,
                BLOCK, BLOCK, 1,
                0,
                ptr::null_mut(),
                params.as_mut_ptr(),
                ptr::null_mut(),
            ),
            "cuLaunchKernel",
        );

        let mut output = vec![0i32; (n as usize) * (n as usize)];
        check(cuMemcpyDtoH_v2(output.as_mut_ptr() as *mut c_void, d_output, bytes), "cuMemcpyDtoH_v2");

        let count: i64 = output.iter().filter(|&&v| v as u32 == MAX_ITER).count() as i64;
        println!("{count}");

        check(cuMemFree_v2(d_output), "cuMemFree_v2");
        check(cuCtxDestroy_v2(ctx), "cuCtxDestroy_v2");
    }
}
