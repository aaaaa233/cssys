#!/bin/bash
# 任务 1 反面教材之二：TLB 补丁没打（MMIO 页没标 uncacheable）会怎样？
# 先把 tlb.cc 还原、重编、跑一次，再打回补丁、重编。
# 一共两次增量编译，服务器上大约 6 分钟。
set -e
cd /mnt/smartssd/wlx/cssys/gem5 || exit 1
G=build/RISCV/gem5.opt
OPT='8 0x01352505'

echo "=== 1) 还原 tlb.cc 并重编 ==="
git checkout -- src/arch/riscv/tlb.cc
python3 -m SCons $G -j 24 2>&1 | tail -2

cd /mnt/smartssd/wlx/cssys
for c in timing o3; do
  echo "===== 没打补丁 cpu=$c ====="
  timeout 900 gem5/build/RISCV/gem5.opt --outdir=out/lab6/nopatch_$c \
      framework/cssys_se.py --cmd bench/bin/riscv/qnn_accel --options "$OPT" \
      --cpu $c --accel l2bus --accel-pe 32 2>&1 \
    | grep -E 'checksum|panic|fatal|Assertion|Program aborted|hangs|Exiting' | head -5
  grep -E '^system.accel.(jobs|macs)' out/lab6/nopatch_$c/stats.txt | head -4
done

echo "=== 2) 打回补丁并重编 ==="
cd /mnt/smartssd/wlx/cssys
python3 _tools/apply_uncacheable.py
cd gem5 && python3 -m SCons build/RISCV/gem5.opt -j 24 2>&1 | tail -2
cd /mnt/smartssd/wlx/cssys
echo "=== 3) 复查：打了补丁应当恢复正确 ==="
timeout 900 gem5/build/RISCV/gem5.opt --outdir=out/lab6/repatch_o3 \
    framework/cssys_se.py --cmd bench/bin/riscv/qnn_accel --options "$OPT" \
    --cpu o3 --accel l2bus --accel-pe 32 2>&1 | grep -E 'checksum' | head -2
echo NOPATCHDONE
