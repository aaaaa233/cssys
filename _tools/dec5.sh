#!/bin/bash
D=/mnt/smartssd/wlx/cssys/gem5/src/arch/riscv/isa/decoder.isa
echo "===== 顶层结构（前 40 行） ====="
sed -n '1,40p' $D
echo "===== QUADRANT 0x3 下的一级 OPCODE5 分派 ====="
awk 'NR>1 && /^        0x[0-9a-f]+: /' $D | head -40
echo "===== 行数 ====="
wc -l $D
