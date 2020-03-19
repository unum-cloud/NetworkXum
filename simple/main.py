from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl

print('Starting NumPy!')
as_cpu = np.random.rand(50000).astype(np.float32)
bs_cpu = np.random.rand(50000).astype(np.float32)
cs_cpu = (as_cpu + bs_cpu)
kernel_source = open('summation.cl', 'r').read()


def execute_kernel(ctx, prg):
    print('Starting OpenCL queue!')
    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags
    as_gpu = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=as_cpu)
    bs_gpu = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=bs_cpu)
    cs_gpu = cl.Buffer(ctx, mf.WRITE_ONLY, as_cpu.nbytes)

    print('Running!')
    prg.sum(queue, as_cpu.shape, None, as_gpu, bs_gpu, cs_gpu)
    cs_from_gpu = np.empty_like(as_cpu)
    cl.enqueue_copy(queue, cs_from_gpu, cs_gpu)

    # Check on CPU with Numpy:
    print('Validating!')
    print(cs_from_gpu - cs_cpu)
    print(np.linalg.norm(cs_from_gpu - cs_cpu))
    assert np.allclose(cs_from_gpu, cs_cpu)
    print('Passed validation!')


def print_device(device):
    context = cl.Context([device])
    program = cl.Program(context, kernel_source).build()

    print("Device: " + device.name +
          " (" + cl.device_type.to_string(device.type) + ")")
    print("\tGlobal memory: \t\t" + str(device.global_mem_size / 2**30) + " GB")
    print("\tGlobal cache: \t\t" + str(device.global_mem_cache_size / 2**10) +
          " KB (" + cl.device_mem_cache_type.to_string(device.global_mem_cache_type) + ")")
    print("\tGlobal cache line: \t" +
          str(device.global_mem_cacheline_size) + " B")
    print("\tLocal memory: \t\t" + str(device.local_mem_size / 2**10) +
          " KB (" + cl.device_local_mem_type.to_string(device.local_mem_type) + ")")
    print("\tConstant memory: \t" +
          str(device.max_constant_buffer_size / 2**10) + " KB")
    print("\tCompute units: \t\t" + str(device.max_compute_units))
    print("\tMax work-group size: \t" + str(device.max_work_group_size))
    print("\tMax work-item size: \t" + str(device.max_work_item_sizes))

    kernel = cl.Kernel(program, "sum")
    print("\tLockstep unit: \t\t" + str(kernel.get_work_group_info(
        cl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, device)))
    print()
    execute_kernel(context, program)


def print_devices():
    for platform in cl.get_platforms():
        for device in platform.get_devices():
            print("----Platform: " + platform.name + "\n\n")
            print_device(device)


if __name__ == '__main__':
    print('Hi! We are in main!')
    print_devices()
