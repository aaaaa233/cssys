import m5
from m5.objects import *

u = SIMD_Unit()
names = [str(od.opClass) for od in u.opList]
print("count=", u.count)
print("n_ops=", len(names))
print(names[:6])
print("SimdMultAcc" in names)
