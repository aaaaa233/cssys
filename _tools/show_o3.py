"""打印 stats.py 新增的乱序核字段，用于验证解析是否正确。"""
import json
import subprocess
import sys

KEYS = ("rob_full", "iq_full", "lq_full", "sq_full", "rename_block",
        "squash", "bp_", "btb_", "icache_stall", "fetch_cache_lines",
        "load_to_use", "mem_order", "lsq_full", "cycles", "ipc", "insts")

path = sys.argv[1]
out = subprocess.run([sys.executable, "framework/stats.py", path],
                     capture_output=True, text=True, check=True).stdout
d = json.loads(out)
for k, v in d.items():
    if any(t in k for t in KEYS):
        print(f"{k:28s} {v}")
