#!/bin/bash
export PATH=/mnt/smartssd/wlx/.local/bin:$PATH
cd /mnt/smartssd/wlx/cssys/gem5 || exit 1
scons build/RISCV/gem5.opt -j56 > /mnt/smartssd/wlx/cssys/_build_lab5.log 2>&1
echo "EXIT=$?" >> /mnt/smartssd/wlx/cssys/_build_lab5.log
