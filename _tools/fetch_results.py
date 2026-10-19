"""把服务器上 results/ 里的 CSV 全部拉回本地。"""
import os
import subprocess
import sys

NAMES = [
    "lab1_cpu_models", "lab1_fidelity",
    "lab2_l1d_size", "lab2_assoc", "lab2_line", "lab2_l2", "lab2_mshr",
]
if len(sys.argv) > 1:
    NAMES = sys.argv[1:]

HERE = os.path.dirname(os.path.abspath(__file__))
RSH = os.path.join(HERE, "rsh.py")
os.makedirs("results", exist_ok=True)
for n in NAMES:
    subprocess.run([sys.executable, RSH, "get",
                    f"/mnt/smartssd/wlx/cssys/results/{n}.csv",
                    f"results/{n}.csv"], check=False)
    print("got", n)
