#!/bin/bash
# 量一下"改了 decoder.isa 之后增量重编译要多久"。学生机是 8 核，所以用 -j8。
# 这个数字直接决定实验五的课堂节奏，必须实测。
export PATH=/mnt/smartssd/wlx/.local/bin:$PATH
cd /mnt/smartssd/wlx/cssys || exit 1
cp gem5/src/arch/riscv/isa/decoder.isa.lab5bak gem5/src/arch/riscv/isa/decoder.isa
python3 _tools/apply_dotp8.py || exit 1
grep -n 'SimdMultAccOp\|IntMultOp' gem5/src/arch/riscv/isa/decoder.isa
cd gem5 || exit 1
echo "--- start $(date +%T)"
time scons build/RISCV/gem5.opt -j8 > /mnt/smartssd/wlx/cssys/_build_j8.log 2>&1
echo "EXIT=$? end $(date +%T)"
tail -2 /mnt/smartssd/wlx/cssys/_build_j8.log
