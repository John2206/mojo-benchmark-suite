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
    fn cuMemcpyHtoD_v2(dst: CUdeviceptr, src: *const c_void, byte_count: usize) -> CUresult;
    fn cuMemcpyDtoH_v2(dst: *mut c_void, src: CUdeviceptr, byte_count: usize) -> CUresult;
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

const BLOCK: u32 = 16;

fn ptx_path() -> PathBuf {
    let mut path = env::current_exe().expect("current_exe failed");
    path.set_file_name("matmul_gpu.ptx");
    path
}

fn main() {
    let n: i32 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2048);
    let nu = n as usize;

    let mut a = vec![0.0f64; nu * nu];
    let mut b = vec![0.0f64; nu * nu];
    for i in 0..nu {
        for j in 0..nu {
            a[i * nu + j] = ((i * 3 + j) % 13) as f64;
            b[i * nu + j] = ((i + j * 2) % 17) as f64;
        }
    }
    let bytes = nu * nu * std::mem::size_of::<f64>();

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

        let kernel_name = CString::new("matmul_kernel").unwrap();
        let mut func: CUfunction = ptr::null_mut();
        check(cuModuleGetFunction(&mut func, module, kernel_name.as_ptr()), "cuModuleGetFunction");

        let mut d_a: CUdeviceptr = 0;
        let mut d_b: CUdeviceptr = 0;
        let mut d_c: CUdeviceptr = 0;
        check(cuMemAlloc_v2(&mut d_a, bytes), "cuMemAlloc_v2(a)");
        check(cuMemAlloc_v2(&mut d_b, bytes), "cuMemAlloc_v2(b)");
        check(cuMemAlloc_v2(&mut d_c, bytes), "cuMemAlloc_v2(c)");
        check(cuMemcpyHtoD_v2(d_a, a.as_ptr() as *const c_void, bytes), "cuMemcpyHtoD_v2(a)");
        check(cuMemcpyHtoD_v2(d_b, b.as_ptr() as *const c_void, bytes), "cuMemcpyHtoD_v2(b)");

        let grid = ((n as u32 + BLOCK - 1) / BLOCK, (n as u32 + BLOCK - 1) / BLOCK);
        let mut n_arg = n;
        let mut params: [*mut c_void; 4] = [
            &mut d_a as *mut CUdeviceptr as *mut c_void,
            &mut d_b as *mut CUdeviceptr as *mut c_void,
            &mut d_c as *mut CUdeviceptr as *mut c_void,
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

        let mut c = vec![0.0f64; nu * nu];
        check(cuMemcpyDtoH_v2(c.as_mut_ptr() as *mut c_void, d_c, bytes), "cuMemcpyDtoH_v2");

        let expected: f64 = (0..nu).map(|k| a[k] * b[k * nu]).sum();
        assert_eq!(c[0], expected, "self-check failed: c[0][0] mismatch");
        println!("{:.2}", c[nu * nu - 1]);

        check(cuMemFree_v2(d_a), "cuMemFree_v2(a)");
        check(cuMemFree_v2(d_b), "cuMemFree_v2(b)");
        check(cuMemFree_v2(d_c), "cuMemFree_v2(c)");
        check(cuCtxDestroy_v2(ctx), "cuCtxDestroy_v2");
    }
}
