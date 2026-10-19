#!/bin/bash
# 增量重编译 gem5。-j8 是为了跟机房 PC 的核数对齐，测出来的时间才有参考价值。
export PATH=/mnt/smartssd/wlx/.local/bin:$PATH
cd /mnt/smartssd/wlx/cssys/gem5 || exit 1
time scons build/RISCV/gem5.opt -j8
