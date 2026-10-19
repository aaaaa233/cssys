#!/bin/bash
G=/mnt/smartssd/wlx/cssys/gem5
cd $G || exit 1
echo "=== Process.py cxx_exports ==="
grep -n "cxx_exports" -A 8 src/sim/Process.py
echo "=== Process::map signature ==="
grep -n "map(Addr\|bool map" src/sim/process.hh src/sim/process.cc
echo "=== page table flags enum ==="
grep -n "Uncacheable\|enum MappingFlags" -A 8 src/mem/page_table.hh | head -30
echo "=== riscv tlb: uncacheable propagation ==="
grep -n "Uncacheable\|UNCACHEABLE" src/arch/riscv/tlb.cc src/arch/riscv/mmu.cc
echo "=== other arch SE uncacheable ==="
grep -rn "EmulationPageTable::Uncacheable" src/ | head
echo "=== riscv process mmap_end / stack ==="
grep -n "mmap_end\|stack_base\|0x400000" src/arch/riscv/process.cc | head
echo "=== translateSe in riscv ==="
grep -n "translateSe" -A 30 src/arch/riscv/tlb.cc | head -50
echo RECON4DONE
