#!/bin/bash
# ★★ 最后一道关：新的最优解必须对**每一个学生的种子**都成立，否则任务 4 没有标准答案。
#
# dump6 把设计空间彻底翻了个面：
#   - batch=4 把算术强度提到 3.86，Roofline 的拐点从 pe≈48 挪到 pe≈82；
#   - 600 A 的预算恰好买得起 pe=83（599.6 A），也就是**刚好买到拐点**；
#   - 最优解从 74,256（w6/pe48）变成 67,627（w6/pe83）。
# 现在要验证：这个排名在四个种子上是不是一样的。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/frontier
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"

r () { local tag=$1 bin=$2 sd=$3 w=$4 pe=$5
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $sd" --cpu o3 \
     --accel l2bus --accel-pe $pe $FREE $CUT --width $w \
     > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
b () { local tag=$1 sd=$2
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/qnn --options "8 $sd" --cpu o3 \
     > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}

echo "===== 帕累托前沿 7 点 × 4 个种子 ====="
for sd in 0x01352505 0x00001234 0x0000abcd 0x00003333; do
  t=${sd: -4}
  b   Z_${t}_base   "$sd"
  r   Z_${t}_w2p48  qnn_accel_b4 "$sd" 2 48
  r   Z_${t}_w4p48  qnn_accel_b4 "$sd" 4 48
  r   Z_${t}_w4p80  qnn_accel_b4 "$sd" 4 80
  r   Z_${t}_w4p96  qnn_accel_b4 "$sd" 4 96
  r   Z_${t}_w5p96  qnn_accel_b4 "$sd" 5 96
  r   Z_${t}_w6p48  qnn_accel_b4 "$sd" 6 48
  r   Z_${t}_w6p83  qnn_accel_b4 "$sd" 6 83
  r   Z_${t}_w6p96  qnn_accel_b4 "$sd" 6 96
done
python3 framework/area.py $OUT/Z_* --csv

echo
echo "===== 每个种子各自的六项冠军 ====="
python3 - <<'PY'
import csv, collections, subprocess, glob, os
rows = list(csv.DictReader(subprocess.run(
    ["python3","framework/area.py"]+sorted(glob.glob("out/lab7/frontier/Z_*"))+["--csv"],
    capture_output=True, text=True).stdout.splitlines()))
bys = collections.defaultdict(list)
for r in rows:
    tag = r["outdir"]; _, sd, cfg = tag.split("_", 2)
    bys[sd].append((cfg, r))
for m, key in [("T","cycles"),("A","area"),("E","energy"),
               ("ADP","adp"),("EDP","edp"),("ED2P","ed2p")]:
    line = []
    for sd in sorted(bys):
        w = min(bys[sd], key=lambda x: float(x[1][key]))
        line.append(f"{sd}:{w[0]}")
    print(f"  {m:5s} 冠军  " + "   ".join(line))
print()
print("  --- 预算内(<=600A)按 T 排名，每个种子一列 ---")
order = {}
for sd in sorted(bys):
    ok = [x for x in bys[sd] if float(x[1]["area"]) <= 600.0]
    order[sd] = [c for c, _ in sorted(ok, key=lambda x: int(x[1]["cycles"]))]
for i in range(len(next(iter(order.values())))):
    print(f"   #{i+1}  " + "   ".join(f"{sd}:{order[sd][i]}" for sd in sorted(order)))
same = len({tuple(v) for v in order.values()}) == 1
print()
print("  ★ 四个种子的预算内排名完全一致：", "是" if same else "否 —— 任务4不能这么出")
PY

echo
echo "===== checksum ====="
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo FRONTIERDONE
