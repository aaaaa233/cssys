#!/bin/bash
# 死锁影响面有多大？——这关系到实验六（已经定稿）能不能照常开。
# 学生用学号后四位当种子，所以真正要问的是：**随便挑一个 4 位十六进制种子，
# 撞上死锁的概率是多少**。
#
# 扫 64 个种子 × 两个二进制（实验六主用 qnn_accel，实验七主用 qnn_accel_b2），
# 都用各自实验里的标准配置。并行 12 路，每个点最多 60 秒。
cd /mnt/smartssd/wlx/cssys || exit 1
OUT=out/lab7/seedscan
mkdir -p $OUT/logs
rm -f $OUT/result.txt

one () {   # one <二进制> <种子>
  local bin=$1 sd=$2
  local tag=${bin}_${sd}
  timeout 60 gem5/build/RISCV/gem5.opt --outdir=$OUT/$tag \
      framework/cssys_se.py --cmd bench/bin/riscv/$bin \
      --options "8 $sd" --cpu o3 --accel l2bus --accel-pe 32 \
      > $OUT/logs/$tag.log 2>&1
  local rc=$?
  if [ $rc = 124 ]; then echo "HANG $bin $sd" >> $OUT/result.txt
  elif [ $rc != 0 ]; then echo "ERR$rc $bin $sd" >> $OUT/result.txt
  else echo "ok   $bin $sd" >> $OUT/result.txt; fi
  rm -rf $OUT/$tag        # 只要结论，不留 64×2 个目录占盘
}
export -f one
export OUT

# 64 个种子：0x0000..0xffff 里均匀取，外加几个已知的
for i in $(seq 0 63); do printf '0x0000%04x\n' $((i * 1024 + 273)); done > $OUT/seeds.txt
printf '0x00003333\n0x00005555\n0x00001234\n0x0000abcd\n0x01352505\n' >> $OUT/seeds.txt

for bin in qnn_accel qnn_accel_b2; do
  while read -r sd; do echo "$bin $sd"; done < $OUT/seeds.txt
done | xargs -P 12 -n 2 bash -c 'one "$0" "$1"'

echo "===== 汇总 ====="
sort $OUT/result.txt | awk '{print $1, $2}' | sort | uniq -c
echo
echo "===== 卡住的种子 ====="
grep '^HANG' $OUT/result.txt | sort
echo
echo "===== 出错的 ====="
grep '^ERR' $OUT/result.txt | sort | head
echo SEEDSCANDONE
