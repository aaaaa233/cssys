#!/bin/bash
# 测"只改一个 .cc 文件"的增量编译时间——这是学生在任务 2b/3 里会反复付出的代价
export PATH=/mnt/smartssd/wlx/.local/bin:$PATH
cd /mnt/smartssd/wlx/cssys/gem5 || exit 1
echo '// touched for incremental build timing' >> src/mem/cache/replacement_policies/cssys_rp.cc
time scons build/RISCV/gem5.opt -j8
