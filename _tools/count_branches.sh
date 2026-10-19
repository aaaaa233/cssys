#!/bin/bash
# 数一数 qnn 的 ROI 里到底有几条静态分支/跳转指令。
# 用来给实验四任务 6 第 3 问（"用 BTB 拐点反推静态分支数"）一个可核对的标准答案。
cd /mnt/smartssd/wlx/cssys || exit 1
OD=riscv64-linux-gnu-objdump
BIN=bench/bin/riscv/qnn

for f in main infer dot_i8 requantize; do
  echo "----- $f -----"
  $OD -d --disassemble="$f" "$BIN" 2>/dev/null \
    | grep -E '^\s+[0-9a-f]+:' \
    | awk '{ for (i=3; i<=NF; i++) { if ($i ~ /^(beq|bne|blt|bge|bltu|bgeu|beqz|bnez|blez|bgez|bltz|bgtz|bgt|ble|bgtu|bleu|j|jal|jr|jalr|ret|c\.beqz|c\.bnez|c\.j|c\.jal|c\.jr|c\.jalr|tail|call)$/) { print $i; break } } }' \
    | sort | uniq -c | sort -rn
done

echo "===== 汇总：main/infer/dot_i8 三个函数里的分支类指令总数 ====="
for f in main infer dot_i8; do
  n=$($OD -d --disassemble="$f" "$BIN" 2>/dev/null \
      | grep -E '^\s+[0-9a-f]+:' \
      | grep -cE '\s(beq|bne|blt|bge|bltu|bgeu|beqz|bnez|blez|bgez|bltz|bgtz|bgt|ble|bgtu|bleu|j|jal|jr|jalr|ret|c\.beqz|c\.bnez|c\.j|c\.jal|c\.jr|c\.jalr|tail|call)\s')
  echo "$f : $n"
done
echo COUNTDONE
