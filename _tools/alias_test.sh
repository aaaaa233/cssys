#!/bin/bash
cd /tmp || exit 1
CC=riscv64-linux-gnu-gcc
OD=riscv64-linux-gnu-objdump
F="-O2 -c -falign-functions=64 -falign-loops=64"
for m in WITH WITHOUT; do
  echo "########## $m may_alias ##########"
  if [ $m = WITH ]; then
    $CC $F -DUSE_MAY_ALIAS alias_test.c -o at.o
  else
    $CC $F alias_test.c -o at.o
  fi
  $OD -d --no-show-raw-insn at.o | sed -n '/<dot_i8>:/,/ret/p' | grep -v nop
done
echo "########## -fno-strict-aliasing, no attribute ##########"
$CC $F -fno-strict-aliasing alias_test.c -o at.o
$OD -d --no-show-raw-insn at.o | sed -n '/<dot_i8>:/,/ret/p' | grep -v nop
echo ALIASDONE
