#!/bin/bash
G=/mnt/smartssd/wlx/cssys/gem5
cd $G || exit 1
echo "=== PortProxy ctors ==="
grep -n "PortProxy(" src/mem/port_proxy.hh | head
echo "=== readBlob/writeBlob ==="
grep -n "void readBlob\|void writeBlob" src/mem/port_proxy.hh
echo "=== System threads / getRequestorId ==="
grep -n "threads;\|RequestorID getRequestorId\|getGlobalRequestorId" src/sim/system.hh | head
echo "=== ThreadContext getProcessPtr ==="
grep -n "getProcessPtr" src/cpu/thread_context.hh | head -3
echo "=== Request ctor ==="
grep -n "Request(Addr paddr, unsigned size" -A 6 src/mem/request.hh | head -20
echo "=== ClockedObject header ==="
grep -n "class ClockedObject" -A 6 src/sim/clocked_object.hh | head -12
echo "=== SConscript at src/ root: how subdirs are found ==="
grep -n "Dir\|SConscript" src/SConscript | head -20
echo RECON3DONE
