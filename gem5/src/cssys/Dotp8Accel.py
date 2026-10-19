"""实验六：dotp8 矩阵-向量加速器。

设计要点（讲课时要展开的三条）：

1. **它有自己的访存端口 `mem_side`。** 这就是"加速器"和实验五那条自定义指令
   最本质的区别：`dotp8` 指令的数据必须先被 CPU 用 load 搬进寄存器，
   而加速器自己去内存里取。**接在哪一级，是本次实验最重要的设计决策。**

2. **`pe` 是算力，`outstanding` 是访存并行度。** Roofline 的两个坐标轴。

3. **`cpu_side` 是一组 MMIO 寄存器。** CPU 通过写寄存器下命令、
   读 STATUS 等结果——那条 load 会一直挂着直到加速器算完，
   这就是最朴素的"同步"机制。
"""

from m5.params import *
from m5.proxy import *
from m5.objects.ClockedObject import ClockedObject


class Dotp8Accel(ClockedObject):
    type = "Dotp8Accel"
    cxx_header = "cssys/dotp8_accel.hh"
    cxx_class = "gem5::Dotp8Accel"

    # CPU 通过这个端口访问加速器的 MMIO 寄存器（下命令 / 等结果）
    cpu_side = ResponsePort("MMIO 寄存器端口，接 CPU 侧")
    # 加速器自己取数据的端口。接在 l2bus 还是 membus，是本次实验的核心问题
    mem_side = RequestPort("加速器自己的访存端口(DMA)")

    pio_addr = Param.Addr(0x10000000, "MMIO 寄存器基地址(物理)")
    pio_size = Param.Addr(0x1000, "MMIO 区域大小")

    pe = Param.Unsigned(8, "每周期能做多少次 int8 乘加(算力)")
    outstanding = Param.Unsigned(8, "最多允许多少个访存请求同时在路上")
    start_latency = Param.Cycles(10, "收到 GO 到发出第一个访存请求的固定开销")

    system = Param.System(Parent.any, "所属的 System")
