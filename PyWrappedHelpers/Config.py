import sys
import csv

max_threads = 4
ram_limit = (2 ** 30)  # 1 GB
performance_over_reliability = True

unumdb_purpose = '''
    At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
    The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer (unless you want to train on the same data over and over again).

    * CPU ⇌ RAM bandwidth ([DDR4](https://en.wikipedia.org/wiki/DDR4_SDRAM)): ~100 GB/s.
    * GPU ⇌ VRAM bandwidth ([HBM2](https://en.wikipedia.org/wiki/High_Bandwidth_Memory)): ~1,000 GB/s.
    * GPU ⇌ GPU bandwidth ([NVLink](https://en.wikipedia.org/wiki/NVLink)): ~300 GB/s.
    * CPU ⇌ GPU bandwidth ([PCI-E Gen3 x16](https://en.wikipedia.org/wiki/PCI_Express)): ~15 GB/s (60 GB/s by 2022).
    * CPU ⇌ SSD bandwidth ([NVMe over PCI-E Gen3 x4](https://en.wikipedia.org/wiki/NVM_Express)): ~2 GB/s (6 GB/s by 2022).

    As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
    2 GB/s isn't scary, but **most databases can hardly saturate 10% of that capacity (or 200 MB/s)** due to [read-amplification](http://smalldatum.blogspot.com/2015/11/read-write-space-amplification-pick-2_23.html) or random jumps.
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
