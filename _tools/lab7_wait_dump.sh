#!/bin/bash
# 用法： bash lab7_wait_dump.sh <日志文件> <结束标记>
# PowerShell 会把 $(seq ...) 当成本地命令展开，所以等待循环一律写在这里，
# 绝不写在 rsh.py run 的命令行里。
cd /mnt/smartssd/wlx/cssys || exit 1
LOG=${1:-out/lab7_dump.log}
TOK=${2:-DUMPDONE}
for i in $(seq 1 300); do
  if grep -q "$TOK" "$LOG" 2>/dev/null; then echo READY; exit 0; fi
  sleep 10
done
echo TIMEOUT
