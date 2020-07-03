import sys
import csv

max_threads = 4
ram_limit = (2 ** 30)  # 1 GB
performance_over_reliability = True

unumdb_purpose = '''
    At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
    The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer (unless you want to train on the same data over and over again).

    * CPU ⇌ RAM bandwidth (DDR4): ~100 GB/s.
    * GPU ⇌ VRAM bandwidth (HBM2): ~1,000 GB/s.
    * CPU ⇌ GPU bandwidth (PCI-E Gen3 x16): ~15 GB/s.
    * GPU ⇌ GPU bandwidth (NVLink): ~300 GB/s.
    * CPU ⇌ SSD bandwidth (NVMe): ~2 GB/s.

    As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
    2 GB/s doesn't sound very scary, but the problem is that **most databases can hardly saturate 10% of that capacity (or 200 MB/s)!**
    When it comes to random (opposed to sequential) read operations the performance drops further to <1% of channel capacity.
    That's why it's crucial for us to store the data in the most capable database!
'''


def allow_big_csv_fields():
    """
        When dealing with big docs in ElasticSearch - 
        an error may occur when bulk-loading:
        >>> _csv.Error: field larger than field limit (131072)        
    """
    max_field_len = sys.maxsize
    while True:
        # decrease the max_field_len value by factor 10
        # as long as the OverflowError occurs.
        # https://stackoverflow.com/a/15063941/2766161
        try:
            csv.field_size_limit(max_field_len)
            break
        except OverflowError:
            max_field_len = int(max_field_len/10)
