#!/bin/bash
# 打印 dot_i8 里那个"回边指向自己"的主循环的地址区间和字节数
cd /mnt/smartssd/wlx/cssys/bench || exit 1
for v in qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4; do
  riscv64-linux-gnu-objdump -d bin/riscv/$v | awk -v V="$v" '
    /<dot_i8>:/{f=1}
    f && /^ *1[0-9a-f]*:/{
      addr = strtonum("0x" substr($1, 1, length($1)-1))
      len = 2; if ($2 ~ /^[0-9a-f]{8}$/) len = 4
      line = $0
      if (line ~ /(bne|blt|bge|bltu|bgeu|beq)/ && line ~ /dot_i8\+/) {
        # 取回边目标
        match(line, /dot_i8\+0x[0-9a-f]+/)
        tgt = substr(line, RSTART+8, RLENGTH-8)
        t = strtonum(tgt)
        if (t < addr - 0x10000 + 0) {}
        printf "%-14s loop 0x%x..0x%x  %d bytes  %d fetch-blocks\n", V, base+t, addr+len, addr+len-(base+t), int((addr+len-1)/64) - int((base+t)/64) + 1
      }
    }
    f && /<dot_i8>:/{ base = strtonum("0x" $1) }
    f && /\tret/{ f=0 }
  '
done
