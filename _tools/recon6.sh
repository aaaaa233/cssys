#!/bin/bash
G=/mnt/smartssd/wlx/cssys/gem5
cd $G || exit 1
echo "=== learning_gem5 part2 files ==="
ls src/learning_gem5/part2/ 2>/dev/null
echo "=== SimObject::find ==="
grep -n "find(const char" src/sim/sim_object.hh
echo "=== ThreadContext suspend/activate ==="
grep -n "virtual void suspend\|virtual void activate\|quiesce" src/cpu/thread_context.hh | head
echo "=== SE page table translate ==="
grep -n "bool translate" src/mem/page_table.hh
echo "=== Process pTable ==="
grep -n "pTable" src/sim/process.hh | head
echo "=== existing cssys dirs in gem5 ==="
ls src/mem/cache/replacement_policies/ | grep -i cssys
echo "=== decoder.isa dotp8 ==="
grep -n "dotp8" -A 12 -B 4 src/arch/riscv/isa/decoder.isa | head -60
echo "=== SConscript style (learning_gem5 part2) ==="
cat src/learning_gem5/part2/SConscript 2>/dev/null
echo RECONDONE
