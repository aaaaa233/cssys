#!/bin/bash
G=/mnt/smartssd/wlx/cssys/gem5
grep -oP 'static const OpClass \K\w+' $G/src/cpu/op_class.hh | sed 's/Op$//' | sort -u > /tmp/all.txt
grep -oP 'opClass="\K\w+' $G/src/cpu/o3/FuncUnitConfig.py | sort -u > /tmp/inpool.txt
echo "--- OpClass 存在于枚举里、但 DefaultFUPool 没有任何单元提供："
comm -23 /tmp/all.txt /tmp/inpool.txt
