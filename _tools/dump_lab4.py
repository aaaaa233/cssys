import csv, sys, os

WANT = {
    "lab4_width":   ["width", "insts", "cycles", "ipc", "iq_full_events", "lq_full_events", "sq_full_events", "rob_full_events", "squashed_insts", "l1d_mlp", "load_to_use", "rename_block_frac"],
    "lab4_rob":     ["rob", "cycles", "ipc", "rob_full_events", "iq_full_events", "lq_full_events", "sq_full_events", "l1d_mlp", "load_to_use", "l1d_misses"],
    "lab4_lq":      ["lq", "cycles", "ipc", "lq_full_events", "sq_full_events", "iq_full_events", "rob_full_events", "l1d_mlp", "load_to_use", "l1d_misses"],
    "lab4_iq":      ["iq", "cycles", "ipc", "iq_full_events", "rob_full_events", "lq_full_events", "sq_full_events", "l1d_mlp", "load_to_use", "l1d_misses"],
    "lab4_bp_qnn":  ["bp", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "bp_mpki", "squashed_insts"],
    "lab4_branchy": ["bp", "insts", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts", "l1d_mpki"],
    "lab4_branchy1":["bp", "insts", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts"],
    "lab4_branchy2":["bp", "insts", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts"],
    "lab4_wxbp":    ["width", "bp", "cycles", "ipc", "bp_mispredicts", "bp_miss_rate", "squashed_insts"],
    "lab4_btb":     ["btb-entries", "btb_entries", "cycles", "ipc", "bp_mispredicts", "bp_miss_rate", "bp_miss_predictor", "bp_miss_btb", "btb_hit_rate"],
    "lab4_allin":   ["label", "cycles", "ipc", "iq_full_events", "rob_full_events", "lq_full_events", "sq_full_events", "bp_mispredicts", "bp_miss_rate", "l1d_mlp", "load_to_use"],
    "lab4_lag":     ["width", "insts", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts", "squash_ratio"],
    "lab4_lag0":    ["width", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts"],
    "lab4_lagfine": ["width", "cycles", "ipc", "bp_committed", "bp_mispredicts", "bp_miss_rate", "squashed_insts", "squash_ratio"],
    "lab4_l3timing":["l1d-repl", "insts", "cycles", "ipc", "l1d_accesses", "l1d_misses", "l1d_mshr_misses", "l1d_mlp", "l1d_avg_miss_lat_cycles", "l1d_avg_mshr_lat_cycles"],
    "lab4_rob2":    ["rob", "cycles", "ipc", "rob_full_events", "iq_full_events", "lq_full_events", "sq_full_events", "l1d_mlp", "load_to_use"],
    "lab4_regs":    ["int-regs", "cycles", "ipc", "rob_full_events", "iq_full_events", "lq_full_events", "sq_full_events", "l1d_mlp", "load_to_use"],
    "lab4_allbp":   ["bp", "cycles", "ipc", "bp_mispredicts", "bp_miss_rate", "squashed_insts", "squash_ratio", "iq_full_events", "rob_full_events", "lq_full_events"],
    "lab4_btb2":    ["btb-entries", "cycles", "ipc", "bp_lookups", "bp_committed", "bp_mispredicts", "bp_miss_predictor", "bp_miss_btb", "btb_hit_rate"],
    "lab4_iq_nolq": ["iq", "cycles", "ipc", "iq_full_events", "lq_full_events", "rob_full_events", "sq_full_events", "l1d_mlp", "load_to_use"],
    "lab4_probe":   None,
}

def fmt(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f == int(f):
        return str(int(f))
    return "%.6f" % f

for name, cols in WANT.items():
    path = "results/%s.csv" % name
    if not os.path.exists(path):
        print("== %s : MISSING" % name)
        continue
    with open(path) as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("== %s : EMPTY" % name)
        continue
    if cols is None:
        cols = list(rows[0].keys())[:12]
    cols = [c for c in cols if c in rows[0]]
    print("== %s" % name)
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join(fmt(r[c]) for c in cols))
    print()
