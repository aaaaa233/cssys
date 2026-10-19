#!/bin/bash
# 生成发给学生的任务 3 参考数据（28 个单旋钮扫描点）。
# 输出一个带 knob/value 两列的 CSV，学生拿到就能直接画图，不用自己跑 28 个点。
cd /mnt/smartssd/wlx/cssys || exit 1
OUT=out/lab7_single_ref.csv
python3 - <<'PY' > $OUT
import csv, glob, io, subprocess, os, re
order = [("l1i-size","lab7_s_l1i"), ("l1d-size","lab7_s_l1d"), ("l2-size","lab7_s_l2"),
         ("width","lab7_s_width"), ("rob","lab7_s_rob"), ("iq","lab7_s_iq"),
         ("int-regs","lab7_s_regs")]
w = csv.writer(io.TextIOWrapper(open(1,'wb',0), write_through=True), lineterminator="\n")
w.writerow(["knob","value","cycles","insts","area","energy","adp","edp","ed2p",
            "area_core","area_l1i","area_l1d","area_l2","outdir"])
for knob, sw in order:
    dirs = sorted(glob.glob(f"out/sweeps/{sw}/p*"))
    if not dirs:
        print(f"# MISSING {sw}", file=os.sys.stderr); continue
    txt = subprocess.run(["python3","framework/area.py"]+dirs+["--csv"],
                         capture_output=True, text=True).stdout
    for r in csv.DictReader(txt.splitlines()):
        base = os.path.basename(r["outdir"])
        m = re.match(r"p\d+_(.+)", base)
        val = m.group(1).split("-",1)[1] if m and "-" in m.group(1) else base
        # p000_width-2 -> "width-2" -> "2"; p000_l1i-size-2kB -> "l1i-size-2kB" -> "size-2kB"
        val = m.group(1)
        for pref in (knob+"-",):
            if val.startswith(pref): val = val[len(pref):]
        w.writerow([knob, val, r["cycles"], r["insts"], r["area"], r["energy"],
                    r["adp"], r["edp"], r["ed2p"], r["area_core"], r["area_l1i"],
                    r["area_l1d"], r["area_l2"], r["outdir"]])
PY
echo "--- 行数 ---"; wc -l < $OUT
cat $OUT
echo MKREFDONE
