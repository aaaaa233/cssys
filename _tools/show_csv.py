"""_tools/show_csv.py —— 把 sweep 出来的 CSV 挑几列打成一张对齐的表

用法：
    python _tools/show_csv.py results/lab6_where_pe.csv col1 col2 ...
不给列名时打印全部列名，方便先看有哪些列可选。
"""
import csv
import sys


def main():
    path = sys.argv[1]
    cols = sys.argv[2:]
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("(空表)")
        return
    if not cols:
        print("\n".join(rows[0].keys()))
        return

    def fmt(v):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return str(v)
        if f == int(f) and abs(f) < 1e15:
            return str(int(f))
        return "%.4g" % f

    table = [cols] + [[fmt(r.get(c, "")) for c in cols] for r in rows]
    w = [max(len(r[i]) for r in table) for i in range(len(cols))]
    for i, r in enumerate(table):
        print("  ".join(c.rjust(w[j]) for j, c in enumerate(r)))
        if i == 0:
            print("  ".join("-" * w[j] for j in range(len(cols))))


if __name__ == "__main__":
    main()
