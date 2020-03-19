
__kernel void sum(
    __global const float * as, 
    __global const float * bs, 
    __global float * cs) {

  int gid = get_global_id(0);
  cs[gid] = as[gid] + bs[gid];
}
