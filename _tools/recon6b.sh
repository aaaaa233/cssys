#!/bin/bash
G=/mnt/smartssd/wlx/cssys/gem5
cd $G || exit 1
echo "=== EmulationPageTable map flags ==="
sed -n '55,110p' src/mem/page_table.hh
echo "=== BasicPioDevice ==="
grep -n "class BasicPioDevice\|class PioDevice" -A 30 src/dev/io_device.hh | head -70
echo "=== Device.py params ==="
sed -n '1,80p' src/dev/Device.py | grep -n "class\|Param"
echo "=== Process map() ==="
grep -n "bool map\|void map" src/sim/process.hh
echo RECON2DONE
