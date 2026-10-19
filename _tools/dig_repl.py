#!/usr/bin/env python3
"""挖某一级 Cache 的原始计数器。

关键比值 hit/ins = overallHits / overallMshrMisses
  = 一个块从被装进来到被踢走，平均被 touch() 了多少次。
这个数决定了"插入位置类"策略（LIP/BIP/RRIP）能不能起作用：
它一大，插入时下的注就会被自己后续的命中立刻抵消。

用法: python3 dig_repl.py <sweep目录> [l1d|l2]
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "framework"))
from stats import parse_blocks

root = sys.argv[1]
level = sys.argv[2] if len(sys.argv) > 2 else "l1d"
PREFIX = {"l1d": "system.cpu.dcache", "l1i": "system.cpu.icache",
          "l2": "system.l2cache"}[level]

print(f"[{level}]  {'point':32s} {'acc':>9s} {'hit':>9s} {'miss':>9s} "
      f"{'mshrHit':>8s} {'mshrMiss':>8s} {'repl':>7s} {'hit/ins':>8s}")
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d, "stats.txt")
    if not os.path.exists(p):
        continue
    blocks = parse_blocks(p)
    s = blocks[1] if len(blocks) > 1 else blocks[0]
    g = lambda k: s.get(PREFIX + "." + k, 0.0)
    ins = g("overallMshrMisses::total") or 1.0
    print(f"       {d:32s} {g('overallAccesses::total'):9.0f} "
          f"{g('overallHits::total'):9.0f} {g('overallMisses::total'):9.0f} "
          f"{g('overallMshrHits::total'):8.0f} {g('overallMshrMisses::total'):8.0f} "
          f"{g('replacements'):7.0f} {g('overallHits::total')/ins:8.3f}")
