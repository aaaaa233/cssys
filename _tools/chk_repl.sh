#!/bin/bash
# 确认替换策略真的被应用了（排除"扫描根本没生效"这种低级可能）
cd /mnt/smartssd/wlx/cssys || exit 1
for d in out/sweeps/lab3_probe_repl/*/; do
  echo "=== $d"
  grep -E '^\[system\.cpu\.dcache\.replacement_policy\]' -A4 "$d/config.ini" | head -6
done
