#!/bin/bash
# 实验七 参考数据 C1：单点扫描（一次只动一个旋钮）
#
# 目的：给"每个旋钮值多少钱、买到多少性能"建一张权威表。
# 基线固定为 --cpu o3 的全部默认值，跑 qnn（纯软件）。
# 每个 sweep 都把基线值本身也扫进去，这样表格内部自洽，
# 不需要跨 sweep 拼接——跨 sweep 拼接是出错的主要来源。
cd /mnt/smartssd/wlx/cssys || exit 1

SEED="8 0x01352505"
BASE="--cpu o3"
J=8

run () {                      # run <名字> <vary 串>
  echo "### $1"
  python3 framework/sweep.py --name "lab7_$1" \
      --bench qnn --bench-args "$SEED" --base "$BASE" \
      --vary "$2" --jobs $J --timeout 3600
  echo
}

# —— 存储层次 ——
# L1I：假设它几乎不干活（ROI 里只有 6559 次访问），砍掉应该是免费的
run s_l1i  'l1i-size=2kB,4kB,8kB,16kB,32kB'
run s_l1d  'l1d-size=8kB,16kB,32kB,64kB'
run s_l2   'l2-size=64kB,128kB,256kB,512kB'

# —— 核 ——
run s_width 'width=2,4,6,8'
run s_rob   'rob=64,96,128,192'
run s_iq    'iq=16,32,64'
run s_regs  'int-regs=96,128,160,256'

echo LAB7SINGLEDONE
