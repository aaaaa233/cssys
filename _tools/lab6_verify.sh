#!/bin/bash
# 出厂检查：完全按学生指导书 §2.2 的三条命令走一遍，确认发给学生的脚本真的能用。
# 不重编译——只检查脚本是幂等的、且服务器上的源码和发给学生的一模一样。
cd /mnt/smartssd/wlx/cssys || exit 1

echo "=== 1) 学生用的安装脚本（应当幂等，重复执行只是覆盖）==="
python3 labs/lab6/src/install_dotp8_accel.py gem5 labs/lab6/src | head -6

echo
echo "=== 2) 学生用的 TLB 补丁脚本（应当报 already patched v2）==="
python3 labs/lab6/src/patch_riscv_tlb.py gem5

echo
echo "=== 3) 服务器上的 gem5/src/cssys 与发给学生的源文件是否逐字节相同 ==="
for f in Dotp8Accel.py dotp8_accel.hh dotp8_accel.cc SConscript; do
  if diff -q labs/lab6/src/$f gem5/src/cssys/$f >/dev/null 2>&1; then
    echo "  OK   $f"
  else
    echo "  DIFF $f   <<<<<< 不一致！"
  fi
done

echo
echo "=== 4) tlb.cc 里两个标志都在吗 ==="
grep -n 'UNCACHEABLE\|STRICT_ORDER' gem5/src/arch/riscv/tlb.cc

echo
echo "=== 5) 基线二进制没被碰过吗（必须是 f2825f24ce6bb3941f732bfb77cf2dbe）==="
md5sum bench/bin/riscv/qnn bench/bin/riscv/qnn_accel bench/bin/riscv/qnn_accel_nofence

echo
echo "=== 6) 五个 accel 版本都在吗 ==="
ls -la bench/bin/riscv/ | grep accel

echo
echo "=== 7) 现在的 gem5.opt 跑一次，checksum 必须是 0x1989da45 ==="
timeout 900 gem5/build/RISCV/gem5.opt --outdir=out/lab6/verify \
    framework/cssys_se.py --cmd bench/bin/riscv/qnn_accel \
    --options '8 0x01352505' --cpu o3 --accel l2bus --accel-pe 32 2>&1 \
  | grep -E 'checksum|panic|fatal'
grep -E '^system\.accel\.(jobs|macs) ' out/lab6/verify/stats.txt | head -4

echo VERIFYDONE
