from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl

print('Starting NumPy!')
a_np = np.random.rand(50000).astype(np.float32)
b_np = np.random.rand(50000).astype(np.float32)
c_np = (a_np + b_np)

CODE = """
__kernel void sum(
    __global const float *a_g, __global const float *b_g, __global float *res_g)
{
  int gid = get_global_id(0);
  res_g[gid] = a_g[gid] + b_g[gid];
}
"""

def execute_kernel(ctx, prg):
  print('Starting OpenCL queue!') 
  queue = cl.CommandQueue(ctx)

  mf = cl.mem_flags
  a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
  b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
  res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

  print('Running!')
  prg.sum(queue, a_np.shape, None, a_g, b_g, res_g)
  res_np = np.empty_like(a_np)
  cl.enqueue_copy(queue, res_np, res_g)

  # Check on CPU with Numpy:
  print('Validating!')
  print(res_np - c_np)
  print(np.linalg.norm(res_np - c_np))
  assert np.allclose(res_np, c_np)
  print('Passed validation!')

def print_device(device):
  context = cl.Context([device])
  program = cl.Program(context, CODE).build()

  print("Platform: " + platform.name)
  print("Device: " + device.name + " (" + cl.device_type.to_string(device.type) + ")")
  print("\tGlobal memory: \t\t" + str(device.global_mem_size / 2**30) + " GB")
  print("\tGlobal cache: \t\t" + str(device.global_mem_cache_size / 2**10) + " KB (" + cl.device_mem_cache_type.to_string(device.global_mem_cache_type) + ")")
  print("\tGlobal cache line: \t" + str(device.global_mem_cacheline_size) + " B")
  print("\tLocal memory: \t\t" + str(device.local_mem_size / 2**10) + " KB (" + cl.device_local_mem_type.to_string(device.local_mem_type) + ")")
  print("\tConstant memory: \t" + str(device.max_constant_buffer_size / 2**10) + " KB")
  print("\tCompute units: \t\t" + str(device.max_compute_units))
  print("\tMax work-group size: \t" + str(device.max_work_group_size))
  print("\tMax work-item size: \t" + str(device.max_work_item_sizes))

  kernel = cl.Kernel(program, "sum")
  print("\tLockstep unit: \t\t" + str(kernel.get_work_group_info(cl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, device)))
  print()
  execute_kernel(context, program)

def print_devices():
  for platform in cl.get_platforms():
    for device in platform.get_devices():
      print_device(device)

print('Listing available devices!')
print_devices()


if __name__ == '__main__':
    print('Hi! We are in main!')