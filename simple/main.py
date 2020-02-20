from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl

CODE = """
__kernel void sum(
    __global const float *a_g, __global const float *b_g, __global float *res_g)
{
  int gid = get_global_id(0);
  res_g[gid] = a_g[gid] + b_g[gid];
}
"""

def print_device(device):
  context = pyopencl.Context([device])
  program = pyopencl.Program(context, CODE).build()
  kernel = pyopencl.Kernel(program, "test")

  print("Platform: " + platform.name)
  print("Device: " + device.name + " (" + pyopencl.device_type.to_string(device.type) + ")")
  print("\tGlobal memory: \t\t" + str(device.global_mem_size / 2**30) + " GB")
  print("\tGlobal cache: \t\t" + str(device.global_mem_cache_size / 2**10) + " KB (" + pyopencl.device_mem_cache_type.to_string(device.global_mem_cache_type) + ")")
  print("\tGlobal cache line: \t" + str(device.global_mem_cacheline_size) + " B")
  print("\tLocal memory: \t\t" + str(device.local_mem_size / 2**10) + " KB (" + pyopencl.device_local_mem_type.to_string(device.local_mem_type) + ")")
  print("\tConstant memory: \t" + str(device.max_constant_buffer_size / 2**10) + " KB")
  print("\tCompute units: \t\t" + str(device.max_compute_units))
  print("\tMax work-group size: \t" + str(device.max_work_group_size))
  print("\tMax work-item size: \t" + str(device.max_work_item_sizes))
  print("\tLockstep unit: \t\t" + str(kernel.get_work_group_info(pyopencl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, device)))
  print()

def print_devices():
  for platform in pyopencl.get_platforms():
    for device in platform.get_devices():
      print_device(device)

print('Listing available devices!')
print_devices()

print('Starting NumPy!')
a_np = np.random.rand(50000).astype(np.float32)
b_np = np.random.rand(50000).astype(np.float32)

print('Starting OpenCL!')
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

print('Compiling Kernel!')
mf = cl.mem_flags
a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
prg = cl.Program(ctx, CODE).build()
res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

print('Running!')
prg.sum(queue, a_np.shape, None, a_g, b_g, res_g)
res_np = np.empty_like(a_np)
cl.enqueue_copy(queue, res_np, res_g)

# Check on CPU with Numpy:
print('Validating!')
print(res_np - (a_np + b_np))
print(np.linalg.norm(res_np - (a_np + b_np)))
assert np.allclose(res_np, a_np + b_np)
print('Passed validation!')

if __name__ == '__main__':
    print('Hi! We are in main!')