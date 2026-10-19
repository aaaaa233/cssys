# -*- coding: utf-8 -*-
"""实验七《综合设计与答辩》讲课用 PPT。

    python _tools/ppt/lab7.py            → labs/lab7/幻灯片.pptx

所有数字来自 labs/lab7/参考解答.md 与 labs/lab7/参考数据/lab7_single.csv，
改数据请同步改这两处。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme as T
from theme import (INK, INK_SOFT, PAPER, PAPER_DIM, RED, RED_DIM,
                   GREEN, GREEN_DIM, GOLD, WHITE_DIM, M, CONTENT_W,
                   SLIDE_W, SLIDE_H)
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "labs", "lab7", "幻灯片.pptx")

ACC = T.LAB_ACCENT[7]          # 朱砂
FOOT = "实验七　综合设计与答辩"


# ------------------------------------------------------------------ 散点图
def scatter(slide, x, y, w, h, points, xlim, ylim,
            xlabel="面积 A", ylabel="周期数 T", budget=None,
            xticks=(), yticks=(), dot_d=Inches(0.17), frontier=(),
            better=True):
    """(A, T) 散点。points = [(A, T, 标签, 颜色, 标签方位[, (dx, dy)]), ...]

    标签方位 ∈ {"r","l","u","d"}；(dx, dy) 是标签的额外微移，点密时用；
    budget 画一条朱砂竖虚线；frontier 是要连成折线的点下标序列；
    better 在左下角标注「越靠左下越好」。
    """
    x0, x1 = xlim
    y0, y1 = ylim

    def px(v):
        return x + int(w * (v - x0) / (x1 - x0))

    def py(v):
        return y + h - int(h * (v - y0) / (y1 - y0))

    # 坐标轴（细石墨线，不是装饰色条）
    T.rect(slide, x, y + h, w, Emu(9525), INK_SOFT)
    T.rect(slide, x, y, Emu(9525), h, INK_SOFT)

    for v, lab in xticks:
        T.rect(slide, px(v), y + h, Emu(9525), Inches(0.07), INK_SOFT)
        T.txt(slide, px(v) - Inches(0.45), y + h + Inches(0.13), Inches(0.9),
              Inches(0.26), [(lab, 11, False, INK_SOFT, True)],
              align=PP_ALIGN.CENTER)
    for v, lab in yticks:
        T.rect(slide, x - Inches(0.07), py(v), Inches(0.07), Emu(9525), INK_SOFT)
        T.txt(slide, x - Inches(1.12), py(v) - Inches(0.13), Inches(0.98),
              Inches(0.26), [(lab, 11, False, INK_SOFT, True)],
              align=PP_ALIGN.RIGHT)

    if budget is not None:
        bx = px(budget)
        for k in range(int(h / Inches(0.16))):
            T.rect(slide, bx, y + Inches(0.16) * k, Emu(19050), Inches(0.09), RED)
        T.txt(slide, bx - Inches(0.9), y - Inches(0.36), Inches(1.8), Inches(0.28),
              [("预算 600 A", 12, True, RED)], align=PP_ALIGN.CENTER)

    # 前沿折线（先画，压在点下面）
    for k in range(len(frontier) - 1):
        a1, t1 = points[frontier[k]][0], points[frontier[k]][1]
        a2, t2 = points[frontier[k + 1]][0], points[frontier[k + 1]][1]
        T.line(slide, px(a1), py(t1), px(a2), py(t2), GREEN, 1.25)

    if better:
        T.txt(slide, x + Inches(0.16), y + h - Inches(0.5), Inches(2.4),
              Inches(0.3), [("↙ 越靠左下越好", 11.5, True, INK_SOFT)])

    for pt in points:
        a, t, lab, color, pos = pt[:5]
        dx, dy = pt[5] if len(pt) > 5 else (0, 0)
        cx, cy = px(a), py(t)
        T.rect(slide, cx - dot_d // 2, cy - dot_d // 2, dot_d, dot_d,
               color, MSO_SHAPE.OVAL)
        if not lab:
            continue
        lw = Inches(2.0)
        if pos == "r":
            lx, ly, al = cx + Inches(0.16), cy - Inches(0.135), PP_ALIGN.LEFT
        elif pos == "l":
            lx, ly, al = cx - lw - Inches(0.16), cy - Inches(0.135), PP_ALIGN.RIGHT
        elif pos == "u":
            lx, ly, al = cx - lw / 2, cy - Inches(0.44), PP_ALIGN.CENTER
        else:
            lx, ly, al = cx - lw / 2, cy + Inches(0.15), PP_ALIGN.CENTER
        T.txt(slide, lx + dx, ly + dy, lw, Inches(0.28),
              [(lab, 11.5, True, color)], align=al)

    T.txt(slide, x + w - Inches(2.6), y + h + Inches(0.42), Inches(2.6),
          Inches(0.28), [(xlabel, 12.5, True, INK)], align=PP_ALIGN.RIGHT)
    T.txt(slide, x - Inches(0.06), y - Inches(0.42), Inches(3.0), Inches(0.28),
          [(ylabel, 12.5, True, INK)])


def build():
    prs = T.new_deck()

    # ======================================================== 00 封面
    T.cover(prs, 7,
            "综合设计与答辩",
            "核心问题：给定 600 A 的面积预算，整机怎么配最优\n"
            "一次没有标准答案、但有标准判据的设计——四条约束，六项指标",
            "计算机系统综合设计实验　·　4 学时　·　gem5 v25.0.0.1 / RISC-V SE")

    # ======================================================== 01 立题
    T.punch(prs,
            [("前六次实验只问一件事：", False),
             ("「快了多少」。", False),
             ("这一次先问：代价是多少。", True)],
            sub="性能不是目标，性能/成本才是。前六次实验中被搁置的成本一栏，"
                "今天成为硬约束。")

    s = T.blank(prs)
    y = T.head(s, "今天只有一道题", kicker="任务", accent=ACC)
    T.txt(s, M, y, Inches(7.6), Inches(1.5),
          [[("总面积 ", 24, False, INK), ("A ≤ 600", 24, True, RED, True),
            ("，把 ", 24, False, INK), ("qnn", 24, True, INK, True),
            (" 的推理周期数跑到最小。", 24, False, INK)]], spacing=1.3)
    T.bullets(s, M, y + Inches(1.15), Inches(7.5), [
        [("软件、指令、加速器、Cache、核宽——", 15.5, False, INK),
         ("六次实验的所有旋钮全部开放", 15.5, True, INK)],
        [("但只允许跑 ", 15.5, False, INK),
         ("20 个配置点", 15.5, True, RED, True),
         ("（含无效点），必须事前写明为什么这样扫", 15.5, False, INK)],
        [("交付：一页设计定案 + 5 分钟答辩", 15.5, False, INK)],
    ], gap=Inches(0.6), marker=(RED, RED, INK_SOFT))

    T.txt(s, M, y + Inches(2.92), Inches(7.5), Inches(0.32),
          [("默认配置与今天的预算，相差这么多：", 14, True, INK)])
    T.area_blocks(s, M, y + Inches(3.37), Inches(7.5), Inches(0.82), [
        ("预算内 600.0 A", 600.0, INK, PAPER),
        ("超出 236.0", 236.0, RED, PAPER),
    ], label_size=13)
    T.txt(s, M, y + Inches(4.37), Inches(7.5), Inches(0.32),
          [("先削减到预算线以内，才谈得上重新分配。", 13, False, INK_SOFT)])

    T.stat(s, Inches(8.9), y - Inches(0.1), Inches(3.7), "836.0",
           "默认配置的面积", color=INK, size=62,
           sub="实验一到六一直在用的那台机器")
    T.stat(s, Inches(8.9), y + Inches(2.1), Inches(3.7), "+39.3%",
           "超预算", color=RED, size=62,
           sub="所以第一步不是增配，而是削减")
    T.foot(s, FOOT)

    # ======================================================== 02 §1 补课
    T.section(prs, "01", "先统一度量",
              "面积、能量：这两个单位的确切含义", accent=ACC)

    # --- 1.1 两个单位
    s = T.blank(prs)
    y = T.head(s, "只有两个基本单位", kicker="§1.1　量纲", accent=ACC)
    y += Inches(0.5)                      # 两张卡 + 一条注，整体居中
    T.card(s, M, y, Inches(5.72), Inches(2.35))
    T.txt(s, M + Inches(0.42), y + Inches(0.36), Inches(4.9), Inches(1.6),
          [[("1 A", 46, True, INK, True)],
           [("= 1 KB SRAM 数据阵列的面积", 16, False, INK)]], spacing=1.25)
    T.txt(s, M + Inches(0.42), y + Inches(1.62), Inches(4.9), Inches(0.6),
          [("所有部件都折算成「相当于几 KB SRAM」", 12.5, False, INK_SOFT)])

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.35))
    T.txt(s, M + Inches(6.53), y + Inches(0.36), Inches(4.9), Inches(1.6),
          [[("1 E", 46, True, INK, True)],
           [("= 访问 1 KB SRAM 一次的能量", 16, False, INK)]], spacing=1.25)
    T.txt(s, M + Inches(6.53), y + Inches(1.62), Inches(4.9), Inches(0.6),
          [("动态能量 + 泄漏能量，都折算成「相当于几次访问」", 12.5, False, INK_SOFT)])

    T.note(s, M, y + Inches(2.75), CONTENT_W,
           "这是相对量纲：它不给出芯片的绝对面积，"
           "但足以回答「这 32 A 是否值得投入」——今天要回答的正是后者。",
           color=INK, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # --- 1.2 Cache 面积
    s = T.blank(prs)
    y = T.head(s, "一个 Cache 的面积构成", kicker="§1.2　面积模型", accent=ACC)
    T.table(s, M, y, Inches(7.35), [
        ["部件", "怎么算", "32 kB L1D"],
        ["数据阵列", "容量 / 1 KB", "32.0"],
        ["标签阵列", "≈ 数据的 6%", "1.9"],
        ["状态位 / LRU", "每路每组几比特", "0.6"],
        ["MSHR", "每条 1.5 A", "6.0"],
        ["控制逻辑", "固定", "2.7"],
        ["合计", "", "43.2"],
    ], [1.5, 2.0, 1.3], mono_cols=(2,), hi_rows=(6,), hi_fill=PAPER_DIM,
        row_h=Inches(0.45))

    T.txt(s, Inches(9.0), y + Inches(0.05), Inches(3.6), Inches(2.6),
          [[("MSHR", 26, True, RED, True)], [("是最容易被忽略的一项", 15, False, INK)],
           [("4 条 → 16 条：容量没变，", 14.5, False, INK)],
           [("面积多 18 A。", 14.5, True, RED)]], spacing=1.35)
    T.note(s, Inches(9.0), y + Inches(2.35), Inches(3.6),
           "它提供的是并发度而非容量：多少次缺失可同时在途。",
           color=GREEN, fill=GREEN_DIM, size=13.5, icon="→")
    T.foot(s, FOOT)

    # --- 1.3 核心超线性
    s = T.blank(prs)
    y = T.head(s, "核宽的面积代价是超线性的", kicker="§1.3　面积模型", accent=ACC)
    T.txt(s, M, y, Inches(6.4), Inches(0.9),
          [[("旁路网络要在每两条流水线之间连线 →", 16, False, INK)],
           [("A", 26, True, INK, True),
            ("issue", 14, True, INK, True, "sub"),
            (" = 3.0 · w", 26, True, INK, True),
            ("1.8", 16, True, RED, True, "sup")]],
          spacing=1.45)
    T.table(s, M, y + Inches(1.35), Inches(6.4), [
        ["发射宽度 w", "发射/旁路网络", "比 w=2 多"],
        ["2", "10.4 A", "—"],
        ["4", "36.2 A", "3.5×"],
        ["6", "75.4 A", "7.3×"],
        ["8", "126.7 A", "12.2×"],
    ], [1.3, 1.5, 1.1], mono_cols=(1, 2), hi_rows=(4,))

    T.txt(s, Inches(8.15), y - Inches(0.05), Inches(4.4), Inches(0.5),
          [("宽度翻两番，这一项增大 12 倍", 15.5, True, INK)])
    T.area_blocks(s, Inches(8.15), y + Inches(0.55), Inches(4.4), Inches(2.8), [
        ("w=8　126.7", 126.7, RED, PAPER),
        ("w=6　75.4", 75.4, "D66A6F", PAPER),
        ("w=4　36.2", 36.2, "E9A9AC", INK),
        ("", 10.4, RED_DIM, INK),
    ], vertical=True, label_size=13)
    T.txt(s, Inches(8.15), y + Inches(3.48), Inches(4.4), Inches(0.32),
          [("↑ 最下方细线即 w=2 的 10.4 A", 12.5, True, INK)])
    T.txt(s, Inches(8.15), y + Inches(3.95), Inches(4.4), Inches(0.5),
          [("而性能最多线性增长，通常还达不到。", 13, False, INK_SOFT)])
    T.foot(s, FOOT)

    # --- 1.4 能量与 race-to-sleep
    s = T.blank(prs)
    y = T.head(s, "能量分为两部分", kicker="§1.4　能量模型", accent=ACC)
    T.card(s, M, y, Inches(5.72), Inches(2.0))
    T.txt(s, M + Inches(0.42), y + Inches(0.34), Inches(4.9), Inches(1.3),
          [[("动态", 21, True, INK)],
           [("cycles × 3.0 × w", 22, True, INK, True)],
           [("有指令执行才产生，越宽越大", 14, False, INK_SOFT)]], spacing=1.35)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.0), RED_DIM)
    T.txt(s, M + Inches(6.53), y + Inches(0.34), Inches(4.9), Inches(1.3),
          [[("泄漏", 21, True, RED)],
           [("0.008 × A × T", 22, True, RED, True)],
           [("空闲时同样产生，正比于面积×时间", 14, False, INK_SOFT)]], spacing=1.35)

    T.txt(s, M, y + Inches(2.45), CONTENT_W, Inches(0.5),
          [[("泄漏项里 ", 19, False, INK), ("T", 19, True, RED, True),
            (" 是一个乘数，于是有了 ", 19, False, INK),
            ("race-to-sleep", 19, True, RED, True), ("：", 19, False, INK)]])
    T.bullets(s, M, y + Inches(3.15), Inches(11.6), [
        [("一个宽而功耗高的核，如果", 16, False, INK),
         ("足够快", 16, True, GREEN), ("，总能量可能反而更低", 16, False, INK)],
        [("本次实验中 w=8 在 6 项指标里胜过 w=6 五项——包括", 16, False, INK),
         ("能量", 16, True, GREEN)],
    ], gap=Inches(0.55), marker=GREEN)
    T.foot(s, FOOT)

    # --- 1.5 只有三个数
    T.punch(prs,
            [("整张表只有三个独立的数：", False),
             ("T、A、E。", True),
             ("其余全是它们的乘积。", False)],
            sub="ADP = A·T　　EDP = E·T　　ED²P = E·T²　　"
                "「性能/面积」= 1/(A·T) = 1/ADP", accent=ACC)

    # --- 1.6 性能/面积 = 1/ADP
    s = T.blank(prs)
    y = T.head(s, "「性能/面积」不是新指标", kicker="§1.5　最常见的报告错误",
               accent=ACC)
    T.code(s, M, y, Inches(7.5), [
        "性能        = 1 / T",
        "性能 / 面积 = (1/T) / A = 1 / (A·T) = 1 / ADP",
    ], size=17)
    T.txt(s, M, y + Inches(1.5), Inches(7.5), Inches(1.4),
          [[("所以把「性能/面积」和「ADP」并列成两栏对比，", 16.5, False, INK)],
           [("等于把同一个数写了两遍。", 20, True, RED)]], spacing=1.4)
    T.note(s, M, y + Inches(2.9), Inches(7.5),
           "评分表：报告里这两项并列出现 → 任务 6 该题记 0 分。",
           color=RED, fill=RED_DIM, size=15)

    T.stat(s, Inches(9.05), y + Inches(0.15), Inches(3.5), "3",
           "独立的量", color=ACC, size=76,
           sub="T　A　E")
    T.stat(s, Inches(9.05), y + Inches(2.35), Inches(3.5), "1",
           "个可选权重", color=INK, size=76,
           sub="唯一的自由度：T 取几次方")
    T.foot(s, FOOT)

    # --- 1.7 帕累托前沿概念
    s = T.blank(prs)
    y = T.head(s, "帕累托前沿：谁被谁「支配」", kicker="§1.6　怎么读一张 (A,T) 图",
               accent=ACC)
    scatter(s, Inches(1.55), y + Inches(0.42), Inches(6.5), Inches(3.6),
            [(2.0, 8.4, "A", GREEN, "u"), (3.4, 5.0, "B", GREEN, "u"),
             (5.6, 3.3, "C", GREEN, "u"), (8.2, 2.6, "D", GREEN, "u"),
             (5.0, 6.6, "E　被 B 完全支配", RED, "r"),
             (7.4, 5.4, "F　被 C 完全支配", RED, "r")],
            (0, 10), (0, 10), xlabel="面积 A →", ylabel="T ↑",
            frontier=(0, 1, 2, 3))
    T.bullets(s, Inches(8.7), y + Inches(0.5), Inches(3.9), [
        [("被支配", 16, True, RED), ("：存在一个点，", 16, False, INK),
         ("面积更小且时间更短", 16, True, INK)],
        [("在前沿上", 16, True, GREEN), ("：不存在两个轴上同时更优的点",
                                        16, False, INK)],
    ], gap=Inches(1.05), marker=(RED, GREEN))
    T.note(s, Inches(8.7), y + Inches(2.65), Inches(3.9),
           "「在前沿上」是很弱的条件——它不等于值得选。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # --- 1.8 在前沿上 ≠ 可以买
    s = T.blank(prs)
    y = T.head(s, "在前沿上 ≠ 值得选", kicker="§1.6　一个教科书级反例", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["w", "T", "A", "E", "ADP", "EDP", "ED²P"],
        ["2", "3,342,245", "694.4", "48,116,013", "2320.95", "160,815", "537,485"],
        ["4", "1,711,502", "728.8", "40,021,342", "1247.37", "68,497", "117,232"],
        ["6", "1,703,819", "776.4", "50,755,412", "1322.80", "86,478", "147,343"],
        ["8", "1,099,949", "836.0", "43,270,020", "919.59", "47,595", "52,352"],
    ], [0.55, 1.45, 0.95, 1.6, 1.15, 1.25, 1.25], mono_cols=(0, 1, 2, 3, 4, 5, 6),
        hi_rows=(3,), row_h=Inches(0.46))

    T.txt(s, M, y + Inches(2.75), Inches(6.7), Inches(1.6),
          [[("w=6 比 w=4：", 18, True, INK)],
           [("快 0.449%，多花 47.6 A，多烧 26.8% 的电。", 17, False, INK)],
           [("六个指标里它只赢一项，输掉五项。", 17, True, RED)]], spacing=1.4)
    T.txt(s, Inches(7.9), y + Inches(2.75), Inches(4.7), Inches(1.6),
          [[("它没有被 w=4 支配——", 17, False, INK)],
           [("两个点都在帕累托前沿上。", 17, True, GREEN)],
           [("但它是全表最不该选的点。", 17, True, RED)]], spacing=1.4)
    T.foot(s, FOOT)

    # --- 1.9 秤的诚实边界
    s = T.blank(prs)
    y = T.head(s, "这个模型不能回答什么", kicker="§1.7　模型的诚实边界", accent=ACC)
    T.bullets(s, M, y, Inches(11.6), [
        [("没有布线、没有时钟树、没有 PHY", 17, True, INK),
         ("——真实芯片里它们能占三成以上", 17, False, INK_SOFT)],
        [("泄漏不含温度和电压", 17, True, INK),
         ("——真实泄漏对温度指数敏感，会偏向「小而慢」", 17, False, INK_SOFT)],
        [("面积可加、频率不变", 17, True, INK),
         ("——真实设计里越大的核越难跑到同一个频率", 17, False, INK_SOFT)],
        [("SRAM 之外的工艺细节一概没有", 17, True, INK),
           ("——所以数字只在本课程内部可比", 17, False, INK_SOFT)],
    ], gap=Inches(0.72), marker=INK_SOFT)
    T.note(s, M, y + Inches(2.95), CONTENT_W,
           "所以任务 7 第 4 问是：哪一条系数错 2 倍会使结论反转"
           "——认清模型边界，比报出最优值更重要。", color=ACC, fill=RED_DIM,
           size=15.5)
    T.foot(s, FOOT)

    # ======================================================== 03 任务 1
    T.section(prs, "02", "先核算上一次的改动",
              "任务 1：实验六的「把 PE 翻倍」，面积代价与收益各是多少", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "32 A 换来 8 个周期", kicker="任务 1　给一句话装上单位",
               accent=ACC)
    T.table(s, M, y, Inches(7.9), [
        ["--accel-pe", "A", "T", "bytes/拍", "stallCycles"],
        ["8", "876.0", "157,871", "8.026", "344"],
        ["16", "884.0", "107,067", "15.955", "376"],
        ["24", "892.0", "94,371", "20.998", "13,072"],
        ["32", "900.0", "94,363", "21.003", "13,080"],
        ["64", "932.0", "94,355", "21.007", "25,784"],
        ["128", "996.0", "94,355", "21.007", "38,464"],
    ], [1.1, 0.9, 1.3, 1.1, 1.25], mono_cols=(0, 1, 2, 3, 4), hi_rows=(4, 5),
        row_h=Inches(0.44))

    T.stat(s, Inches(9.15), y + Inches(0.1), Inches(3.4), "0.008%",
           "pe 32 → 64 换来的加速", color=RED, size=52,
           sub="多付 32 A，T 从 94,363 降到 94,355")
    T.stat(s, Inches(9.15), y + Inches(2.3), Inches(3.4), "0.1%",
           "本次实验的噪声地板", color=INK, size=52,
           sub="比噪声小 12 倍 —— 这不是收益很小，\n而是没有证据表明它更快")
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "面积加不动，是因为触到了屋顶", kicker="任务 1　三个判据",
               accent=ACC)
    T.bullets(s, M, y, Inches(7.4), [
        [("bytesPerCycle 从 pe=24 起钉死在 21.19", 16.5, True, INK, True)],
        [("macsPerCycle 同时钉死在 21.0", 16.5, True, INK, True)],
        [("stallCycles 从 376 跳到 13,072（35 倍）", 16.5, True, RED, True)],
    ], gap=Inches(0.62), marker=(INK_SOFT, INK_SOFT, RED))
    T.txt(s, M, y + Inches(2.05), Inches(7.4), Inches(0.5),
          [("新增的 PE 全部在等数据。这一列是判断「卡在哪个屋顶」的唯一依据。",
            14.5, False, INK_SOFT)])

    T.card(s, M, y + Inches(2.75), Inches(7.4), Inches(1.55))
    T.txt(s, M + Inches(0.42), y + Inches(3.0), Inches(6.6), Inches(1.1),
          [[("非加速器时间 = 55,651 拍，从 pe=16 起纹丝不动", 16, True, INK)],
           [("Amdahl 上界 = 94,355 / 55,651 = 1.695×", 18, True, RED, True)]],
          spacing=1.4)

    T.txt(s, Inches(8.85), y - Inches(0.05), Inches(3.75), Inches(3.4),
          [[("加速器再快、面积再小，", 16.5, False, INK)],
           [("也只能再快 1.695 倍。", 19, True, RED)],
           [("", 8, False, INK)],
           [("真正的瓶颈是那", 16.5, False, INK)],
           [("55,651 个未被卸载的周期——", 16.5, True, INK)],
           [("它们是 CPU 侧的数据搬运。", 16.5, False, INK)],
           [("加硬件无效，必须改软件。", 17, True, GREEN)]], spacing=1.35)
    T.foot(s, FOOT)

    # ======================================================== 04 任务 2
    s = T.blank(prs)
    y = T.head(s, "836 A 的构成", kicker="任务 2　给基线称重", accent=ACC)
    T.area_blocks(s, M, y, CONTENT_W, Inches(1.25), [
        ("核心　390.5 A　46.7%", 390.5, INK, PAPER),
        ("L2　359.2 A　43.0%", 359.2, "4A5568", PAPER),
        ("L1I+L1D　86.4", 86.4, "A7B0BC", INK),
    ], label_size=14)
    # 爆炸引导线：把「核心」那一块放大成下面整条
    core_w = int(CONTENT_W * 390.5 / 836.0)
    T.line(s, M, y + Inches(1.25), M, y + Inches(1.95), INK_SOFT, 0.9, "dash")
    T.line(s, M + core_w, y + Inches(1.25), M + CONTENT_W, y + Inches(1.95),
           INK_SOFT, 0.9, "dash")
    T.txt(s, M + Inches(0.16), y + Inches(1.42), Inches(4.0), Inches(0.32),
          [("把「核心」这一块放大 →", 12.5, True, INK_SOFT)])
    T.area_blocks(s, M, y + Inches(1.95), CONTENT_W, Inches(1.1), [
        ("发射/旁路 126.7", 126.7, RED, PAPER),
        ("固定开销 120.0", 120.0, INK_SOFT, PAPER),
        ("BTB 46.1", 46.1, "8B95A1", PAPER),
        ("ROB 31.1", 31.1, "AAB2BC", INK),
        ("寄存器 23", 23.0, "C3C9D1", INK),
        ("其它 43.6", 43.6, "DDE1E6", INK),
    ], label_size=11.5)
    T.note(s, M, y + Inches(3.4), CONTENT_W,
           "核心里最大的一块不是 ROB、不是寄存器堆，是发射/旁路网络 126.7 A（占核心 32.4%）"
           "——这正是前面那条超线性曲线的代价。",
           color=RED, fill=RED_DIM, size=15)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "面积占 43%，能量占 0.47%", kicker="任务 2　最不匹配的部件",
               accent=ACC)
    T.table(s, M, y, Inches(7.3), [
        ["部件", "面积占比", "能量占比", "失配"],
        ["L2", "42.97%", "0.47%", "91×"],
        ["L1I", "5.17%", "0.086%", "60×"],
        ["L1D", "5.17%", "21.4%", "—"],
        ["核心", "46.71%", "61.0%", "—"],
    ], [1.1, 1.2, 1.2, 0.8], mono_cols=(1, 2, 3), hi_rows=(1,), row_h=Inches(0.46))
    T.code(s, M, y + Inches(2.6), Inches(7.3), [
        "icache.overallAccesses::total        6,549",
        "dcache.overallAccesses::total    1,638,987   ← 250 倍",
    ], size=13.5, hi=(1,))

    T.txt(s, Inches(8.75), y - Inches(0.05), Inches(3.85), Inches(3.6),
          [[("热循环小到能整个放进取指缓冲：", 15.5, False, INK)],
           [("580 万条指令只产生 6,549 次访问。", 15.5, True, INK)],
           [("", 8, False, INK)],
           [("L2 更极端——它占了 43% 的芯片，", 15.5, False, INK)],
           [("却几乎不耗电。", 15.5, False, INK)]], spacing=1.4)
    T.note(s, Inches(8.75), y + Inches(2.7), Inches(3.85),
           "这是第一笔可无损回收的面积：199.5 A，占基线 23.9%。",
           color=GREEN, fill=GREEN_DIM, size=14.5, icon="→")
    T.foot(s, FOOT)

    # ======================================================== 05 任务 3
    T.section(prs, "03", "先回收无损的面积",
              "任务 3：五个旋钮往回调，既省面积又不降性能", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "三个反而更快，两个无损", kicker="任务 3　单旋钮扫描",
               accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["旋钮", "往回拧", "ΔT", "ΔA", "判定"],
        ["l1d-size", "32 → 8 kB", "−4.543%", "−27.9", "真的更快"],
        ["l2-size", "256 → 128 kB", "−2.195%", "−164.6", "真的更快"],
        ["l1i-size", "32 → 2 kB", "−0.321%", "−34.8", "真的更快"],
        ["rob", "192 → 128", "−13 拍", "−10.3", "无损（噪声内）"],
        ["int-regs", "256 → 160", "+7 拍", "−8.6", "无损（噪声内）"],
    ], [1.3, 1.5, 1.2, 1.0, 1.6], mono_cols=(1, 2, 3),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.LEFT], row_h=Inches(0.46))

    T.stat(s, M, y + Inches(3.1), Inches(3.6), "246.2",
           "五个旋钮单独省的面积之和", color=GREEN, size=52)
    T.stat(s, M + Inches(4.1), y + Inches(3.1), Inches(3.6), "246.3",
           "五个一起拧实测省的面积", color=GREEN, size=52)
    T.txt(s, Inches(9.3), y + Inches(3.35), Inches(3.3), Inches(1.4),
          [[("面积可加。", 22, True, GREEN)],
           [("时间不可加——", 20, True, RED)],
           [("这就是任务 5。", 17, False, INK)]], spacing=1.35)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "唯一的悬崖：L2 装不下权重了", kicker="任务 3　L2 扫描",
               accent=ACC)
    T.table(s, M, y, Inches(7.6), [
        ["l2-size", "T", "相对基线", "A"],
        ["512 kB", "1,124,653", "+2.2%", "1165.2"],
        ["256 kB", "1,099,949", "—", "836.0"],
        ["128 kB", "1,075,802", "−2.2%", "671.4"],
        ["64 kB", "2,359,562", "+114.5%", "589.1"],
    ], [1.2, 1.5, 1.3, 1.1], mono_cols=(0, 1, 2, 3), hi_rows=(4,),
        row_h=Inches(0.46))
    T.txt(s, M, y + Inches(2.65), Inches(7.6), Inches(1.2),
          [[("256 → 128：还在变快。128 → 64：慢了一倍多。", 17, False, INK)],
           [("越过边界之前，周期数没有任何征兆。", 18, True, RED)]], spacing=1.4)

    T.txt(s, Inches(9.05), y - Inches(0.05), Inches(3.55), Inches(2.6),
          [[("判据不是周期数，是", 16, False, INK)],
           [("mem_ctrls.bytesRead", 15, True, RED, True)],
           [("有没有跳一个数量级。", 16, False, INK)]], spacing=1.4)
    T.note(s, Inches(9.05), y + Inches(1.55), Inches(3.55),
           "L2 的硬下限：128 kB。",
           color=RED, fill=RED_DIM, size=14)
    T.note(s, Inches(9.05), y + Inches(2.85), Inches(3.55),
           "64 kB 的 DRAM 读字节数 ≈ 实验六量到的 820,352 B。跨实验对上了。",
           color=GREEN, fill=GREEN_DIM, size=14, icon="✓")
    T.foot(s, FOOT)

    # ======================================================== 06 任务 4
    T.section(prs, "04", "再决定面积投向哪里",
              "任务 4：600 A 的预算，三条路线，天花板差 15 倍", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "三条路线，天花板差 15 倍", kicker="任务 4　路线选择", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["路线", "配置", "T", "A", "加速比"],
        ["一、纯软件", "qnn + FREE + btb512", "1,020,074", "553.9", "1.078×"],
        ["二、自定义指令", "qnn_dotp8x4c + FREE + dotp8-lat 3", "203,773",
         "585.9", "5.398×"],
        ["三、加速器", "qnn_accel_b4 + FREE + CUT + pe 83 + w6", "67,627",
         "599.6", "16.265×"],
    ], [1.35, 3.5, 1.35, 0.9, 1.0], mono_cols=(1, 2, 3, 4),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT], hi_rows=(3,), row_h=Inches(0.52))

    T.txt(s, M, y + Inches(2.5), Inches(5.9), Inches(1.6),
          [[("同样是 600 A。", 18, True, INK)],
           [("只调硬件参数的，最好也只有 1.08×；", 16.5, False, INK)],
           [("改变软件结构的，16 倍。", 18, True, RED)]], spacing=1.4)
    T.code(s, Inches(7.2), y + Inches(2.5), Inches(5.4), [
        "FREE = --l2-size 128kB --l1i-size 2kB",
        "       --l1d-size 8kB --rob 128",
        "       --int-regs 160",
        "CUT  = --btb-entries 512 --lq 16 --sq 16",
    ], size=12.5)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "20 个点，必须事前写完再跑", kicker="任务 4　纪律", accent=ACC)
    T.txt(s, M, y, Inches(6.6), Inches(1.9),
          [[("开始实验前先填满 20 行：", 17, True, INK)],
           [("每一行写明「本点验证哪一个假设」，", 16, False, INK)],
           [("以及「若结果为 X，下一步做什么」。", 16, False, INK)]], spacing=1.45)
    T.note(s, M, y + Inches(1.65), Inches(6.6),
           "事后补填的，任务 4 记 0 分，全卷封顶 85。无效点同样必须列出。",
           color=RED, fill=RED_DIM, size=15)

    T.card(s, M, y + Inches(2.85), Inches(6.6), Inches(1.55))
    T.txt(s, M + Inches(0.42), y + Inches(3.1), Inches(5.8), Inches(1.1),
          [[("为什么只给 20 个点？", 16.5, True, INK)],
           [("一是机器：8 核的实验机，总仿真时间要压在 30 分钟内。",
             15, False, INK)],
           [("二是更重要的——不限次数的尝试会退化为穷举。", 15, True, RED)]],
          spacing=1.4)

    T.txt(s, Inches(7.85), y - Inches(0.1), Inches(4.75), Inches(0.4),
          [("20 个点的基本框架：", 15, True, INK)])
    T.table(s, Inches(7.85), y + Inches(0.4), Inches(4.75), [
        ["#", "用途"],
        ["1–5", "回收无损面积（任务 3 已有结论）"],
        ["6–9", "试三条路线的入口，判断哪条值得深入"],
        ["10–14", "在选定路线上顶到预算线"],
        ["15–19", "补帕累托前沿（任务 6 要用）"],
        ["20", "复核最优解，测定本次噪声地板"],
    ], [0.7, 3.4], aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT], mono_cols=(0,),
        row_h=Inches(0.44), size=12.5)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "如何判断该在哪里停下", kicker="任务 4　最难的一问", accent=ACC)
    T.txt(s, M, y, Inches(7.5), Inches(0.45),
          [("最优解 599.6 A，预算裕量 0.4 A。若再增加 50 A，结果会怎样？",
            17, False, INK)])
    steps = [
        ("1", "量屋顶", [("bytesPerCycle 收敛到 ", 15.5, False, INK),
                        ("21.2", 15.5, True, RED, True),
                        (" 字节/拍", 15.5, False, INK)],
         "这是 L2 总线的属性，与配置多少 MAC 无关"),
        ("2", "量算术强度", [("b4 上 I = macs/bytes = ", 15.5, False, INK),
                          ("3.861", 15.5, True, RED, True)],
         "batch 把它从 0.991 提到 3.861，屋顶不动而斜边变陡"),
        ("3", "算拐点", [("pe* = 21.2 × 3.861 / 0.97 ≈ ", 15.5, True, RED, True),
                       ("84", 22, True, RED, True)],
         "预算只支持到 83，差一个。"),
    ]
    for k, (no, name, runs, sub) in enumerate(steps):
        yy = y + Inches(0.68) + Inches(0.93) * k
        T.txt(s, M, yy - Inches(0.04), Inches(0.4), Inches(0.4),
              [(no, 22, True, RED, True)])
        T.txt(s, M + Inches(0.5), yy, Inches(7.0), Inches(0.34),
              [[(name + "　", 16, True, INK)] + runs])
        T.txt(s, M + Inches(0.5), yy + Inches(0.36), Inches(7.0), Inches(0.3),
              [(sub, 13, False, INK_SOFT)])
    T.note(s, M, y + Inches(3.55), Inches(7.5),
           "必须是事前推理。「试过 pe=96，不行」不计分——那不是设计，是穷举。",
           color=RED, fill=RED_DIM, size=15)

    T.txt(s, Inches(8.9), y - Inches(0.1), Inches(3.7), Inches(0.4),
          [("事后验证这个预测：", 15, True, INK)])
    T.table(s, Inches(8.9), y + Inches(0.35), Inches(3.7), [
        ["pe", "A", "T"],
        ["83", "599.6", "67,627"],
        ["96", "612.6", "67,293"],
        ["128", "644.6", "67,293"],
        ["256", "772.6", "67,291"],
    ], [0.8, 1.1, 1.3], mono_cols=(0, 1, 2), hi_rows=(1,), row_h=Inches(0.44),
        size=12.5)
    T.note(s, Inches(8.9), y + Inches(2.72), Inches(3.7),
           "再增 173 A 只换来 0.50%——预算线正落在屋顶的转角上",
           color=INK, fill=PAPER_DIM, size=14, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 07 任务 5
    T.section(prs, "05", "为什么不能逐项独立评估",
              "任务 5：同一个硬件改动，两种代价，差 20.8 倍", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "同一个改动，两种代价", kicker="任务 5　X1–X4 对照",
               accent=ACC)
    T.txt(s, M, y - Inches(0.08), CONTENT_W, Inches(0.4),
          [[("四个点用完全相同的硬件改动：", 15.5, False, INK),
            ("--width 8 → 4，省 103.0 A", 15.5, True, RED, True),
            ("。区别只在跑什么程序。", 15.5, False, INK)]])
    T.table(s, M, y + Inches(0.5), Inches(8.15), [
        ["", "二进制", "核", "T", "A", "E"],
        ["X1", "qnn", "8 发射", "1,020,074", "589.7", "34,086,584"],
        ["X2", "qnn", "4 发射", "1,699,273", "486.7", "31,793,520"],
        ["X3", "qnn_accel_b2", "8 发射", "80,397", "653.7", "2,494,569"],
        ["X4", "qnn_accel_b2", "4 发射", "82,971", "550.7", "1,503,409"],
    ], [0.45, 1.6, 0.85, 1.35, 0.85, 1.5], mono_cols=(0, 3, 4, 5),
        row_h=Inches(0.46))

    T.stat(s, Inches(9.35), y + Inches(0.28), Inches(3.25), "+66.58%",
           "纯软件下削减核宽的代价", color=RED, size=44)
    T.stat(s, Inches(9.35), y + Inches(1.82), Inches(3.25), "+3.20%",
           "加速器下削减核宽的代价", color=GREEN, size=44)
    T.stat(s, Inches(9.35), y + Inches(3.36), Inches(3.25), "20.8×",
           "同一改动，代价相差的倍数", color=INK, size=44)

    T.card(s, M, y + Inches(3.1), Inches(8.15), Inches(1.4), RED_DIM)
    T.txt(s, M + Inches(0.42), y + Inches(3.32), Inches(7.35), Inches(1.0),
          [[("用 X3 预测 X4：80,397 × 1.6658 = 133,925，实测 82,971，误差 +61.4%",
             14.5, True, RED)],
           [("同一套预测方法，在免费旋钮上误差只有 +0.34%。差 180 倍。",
             14.5, False, INK)]], spacing=1.4)
    T.foot(s, FOOT)

    T.punch(prs,
            [("一个硬件改动值不值，", False),
             ("取决于运行什么软件。", True)],
            sub="qnn 有 5,801,400 条 ROI 指令，qnn_accel_b2 只有 84,824 条——差 68.4 倍。"
                "核宽服务于指令流；指令流被卸载之后，核宽也就失去了用途。",
            accent=ACC)

    # ======================================================== 08 任务 6
    T.section(prs, "06", "换一个指标，换一个冠军",
              "任务 6：六项指标，四个不同的赢家", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "预算内的帕累托前沿", kicker="任务 6　前沿上的八个点", accent=ACC)
    scatter(s, Inches(1.85), y + Inches(0.36), Inches(7.1), Inches(3.3),
            [(486.9, 81425, "w2/pe48　A·E·EDP 冠军", GREEN, "r"),
             (519.2, 76326, "w4/pe48", INK_SOFT, "r"),
             (551.2, 69556, "w4/pe80　ADP 冠军", GOLD, "u"),
             (567.2, 68922, "w4/pe96　ED²P 冠军", "6B4E9B", "d"),
             (588.3, 68214, "w5/pe96", INK_SOFT, "u", (0, -Inches(0.28))),
             (564.6, 74256, "w6/pe48", INK_SOFT, "u"),
             (599.6, 67627, "w6/pe83", RED, "u", (-Inches(0.72), 0)),
             (612.6, 67293, "w6/pe96", RED, "r")],
            (478, 634), (66200, 83200),
            xlabel="面积 A →", ylabel="T ↑", budget=600,
            frontier=(0, 1, 2, 3, 4, 6, 7),
            xticks=[(500, "500"), (550, "550"), (600, "600")],
            yticks=[(70000, "70,000"), (75000, "75,000"), (80000, "80,000")])
    T.txt(s, Inches(1.85), y + Inches(4.08), Inches(4.4), Inches(0.28),
          [("基线 836.0 A / 1,099,934 拍在图外——右上方十六倍处。",
            12, False, INK_SOFT)])
    T.txt(s, Inches(9.55), y + Inches(0.4), Inches(3.05), Inches(3.6),
          [[("六项指标", 19, True, INK)], [("四个冠军", 34, True, RED)],
           [("", 10, False, INK)],
           [("T → w6/pe96（超预算）", 13.5, False, INK)],
           [("A / E / EDP → w2/pe48", 13.5, False, INK)],
           [("ADP → w4/pe80", 13.5, False, INK)],
           [("ED²P → w4/pe96", 13.5, False, INK)],
           [("", 8, False, INK)],
           [("四个种子逐一复核，完全一致。", 12.5, True, GREEN)]], spacing=1.35)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "任务 4 交付的配置，按 EDP 排在倒数第二", kicker="任务 6　排名反转",
               accent=ACC)
    T.table(s, M, y, Inches(8.4), [
        ["配置", "T", "A", "E", "EDP"],
        ["w6/pe83（任务 4 的交付）", "67,627", "599.6", "1,653,246", "111.80"],
        ["w2/pe48", "81,425", "486.9", "914,606", "74.47"],
    ], [2.6, 1.2, 0.9, 1.5, 1.1], mono_cols=(1, 2, 3, 4), hi_rows=(1,),
        row_h=Inches(0.52))
    T.txt(s, M, y + Inches(1.85), Inches(8.4), Inches(1.0),
          [[("按 T：w6/pe83 赢 20.4%。　按 EDP：它输 50.1%。", 18, True, INK)],
           [("而 w2/pe48 只用 486.9 A——比预算少 113 A。", 16.5, False, INK)]],
          spacing=1.45)
    T.txt(s, M, y + Inches(3.1), Inches(8.4), Inches(0.9),
          [[("原因在能量的账本里：核心动态能量 ∝ T × w。", 16, False, INK)],
           [("w6/pe83 的 3×6×67,627 = 1,217,286，占它总能量的 73.6%。",
             16, True, RED, True)]], spacing=1.4)

    T.stat(s, Inches(9.6), y + Inches(0.1), Inches(3.0), "6",
           "个指标", color=INK, size=64)
    T.stat(s, Inches(9.6), y + Inches(1.75), Inches(3.0), "4",
           "个不同的赢家", color=RED, size=64,
           sub="「最优」这个词，\n没有指标就没有意义。")
    T.foot(s, FOOT)

    # ======================================================== 09 任务 7
    T.section(prs, "07", "把结论讲给非专业读者",
              "任务 7：五分钟答辩 + 一页设计定案", accent=ACC)

    s = T.blank(prs)
    y = T.head(s, "答辩四问", kicker="任务 7　每组 5 分钟，一页 slide", accent=ACC)
    T.bullets(s, M, y, Inches(7.6), [
        [("交付的配置是什么？", 17, True, INK), ("　一行命令 + A / T / E",
                                              16, False, INK_SOFT)],
        [("为什么这样配置？", 17, True, INK),
         ("　最关键的两个决定，各用一个数字支撑", 16, False, INK_SOFT)],
        [("放弃了哪些方案？", 17, True, INK),
         ("　一个认真考虑过但没选的方案 + 定量理由", 16, False, INK_SOFT)],
        [("结论最可能在哪里失效？", 17, True, RED),
         ("　哪条系数错 2 倍会反转结论", 16, False, RED)],
    ], gap=Inches(0.68), marker=(INK_SOFT, INK_SOFT, INK_SOFT, RED))
    T.note(s, M, y + Inches(3.05), Inches(7.6),
           "第 4 问占答辩分的一半。答不出的，前三问再完整也只能得一半。",
           color=RED, fill=RED_DIM, size=15)

    T.card(s, Inches(8.85), y - Inches(0.1), Inches(3.75), Inches(4.05))
    T.txt(s, Inches(9.2), y + Inches(0.2), Inches(3.1), Inches(3.6),
          [[("一页设计定案", 20, True, INK)],
           [("读者是未修过本课程的项目经理。", 14, False, INK_SOFT)],
           [("", 8, False, INK)],
           [("决策", 15, True, INK)],
           [("依据（≤3 个数字）", 15, True, INK)],
           [("放弃了什么", 15, True, INK)],
           [("风险：哪条假设最可能失效", 15, True, RED)],
           [("", 8, False, INK)],
           [("术语只许用「周期数」和「ADP」。", 13.5, False, INK_SOFT)]],
          spacing=1.4)
    T.foot(s, FOOT)

    s = T.blank(prs)
    y = T.head(s, "第 4 问的范例：accel_mac", kicker="任务 7　结论如何失效",
               accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["accel_mac", "pe=83 的加速器面积", "最优解总面积", "结论"],
        ["2.0（代价翻倍）", "198.0", "682.6　超预算 13.8%", "退到 pe≈41，598.6 A"],
        ["1.0（当前）", "115.0", "599.6", "w6/pe83，67,627"],
        ["0.5（代价减半）", "73.5", "可支持 pe=166", "屋顶仍在 82，不受影响"],
    ], [1.5, 1.9, 2.2, 2.4], mono_cols=(1,), hi_rows=(2,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        row_h=Inches(0.52))
    T.txt(s, M, y + Inches(2.6), CONTENT_W, Inches(1.3),
          [[("这条系数只在一个方向上危险：变贵会迫使配置回退，变便宜则毫无影响——"
             "因为屋顶不由加速器决定。", 16.5, False, INK)],
           [("而且它改变的是「配多少」，不是「选哪一类」。三条路线的排序不变。",
             17.5, True, RED)]], spacing=1.45)
    T.note(s, M, y + Inches(3.7), CONTENT_W,
           "一个完整的回答要说清三件事：哪一条、往哪个方向错、结论变成什么。",
           color=INK, fill=PAPER_DIM, size=15.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 10 判分
    s = T.blank(prs)
    y = T.head(s, "判分的三条硬纪律", kicker="怎么给分", accent=ACC)
    T.card(s, M, y, Inches(3.75), Inches(3.1))
    T.txt(s, M + Inches(0.36), y + Inches(0.32), Inches(3.1), Inches(2.5),
          [[("0.1%", 40, True, RED, True)], [("噪声地板", 17, True, INK)],
           [("", 8, False, INK)],
           [("差异小于它，应写「没有变化」", 14.5, False, INK)],
           [("写成「有微小提升」要扣分——", 14.5, False, INK)],
           [("扣的是把噪声当结论。", 14.5, True, RED)]], spacing=1.35)

    T.card(s, M + Inches(4.04), y, Inches(3.75), Inches(3.1))
    T.txt(s, M + Inches(4.40), y + Inches(0.32), Inches(3.1), Inches(2.5),
          [[("20", 40, True, RED, True)], [("个配置点，事前写完", 17, True, INK)],
           [("", 8, False, INK)],
           [("无效点也要列出。", 14.5, False, INK)],
           [("事后补填的：任务 4 记 0，", 14.5, False, INK)],
           [("全卷封顶 85。", 14.5, True, RED)]], spacing=1.35)

    T.card(s, M + Inches(8.08), y, Inches(3.75), Inches(3.1))
    T.txt(s, M + Inches(8.44), y + Inches(0.32), Inches(3.1), Inches(2.5),
          [[("checksum", 34, True, RED, True)], [("必须逐位相同", 17, True, INK)],
           [("", 8, False, INK)],
           [("所有配置跑出的校验和，", 14.5, False, INK)],
           [("无论软件如何换、硬件如何改，", 14.5, False, INK)],
           [("必须完全一致。", 14.5, True, RED)]], spacing=1.35)

    T.note(s, M, y + Inches(3.35), CONTENT_W,
           "交出 74,256（次优解）但讲清屋顶成因的报告，"
           "高于凭反复尝试得到 67,627 却说不出为何在 83 停下的报告。",
           color=ACC, fill=RED_DIM, size=16)
    T.foot(s, FOOT)

    # ======================================================== 11 收束
    s = T.blank(prs, dark=True)
    T.txt(s, M, Inches(1.0), CONTENT_W, Inches(0.4),
          [("七次实验，一条线", 14, True, ACC)])
    T.txt(s, M, Inches(1.62), Inches(11.0), Inches(0.7),
          [("每消除一个瓶颈，剩下的部分就更难优化一分", 32, True, PAPER)])
    T.table(s, M, Inches(2.85), CONTENT_W, [
        ["", "剩余「无法卸载」的时间", "从这里往前的 Amdahl 上界"],
        ["实验六结束时（任务 1）", "55,651 拍，占 T 的 59%", "1.695×"],
        ["实验七结束时（任务 4）", "57,429 拍，占 T 的 84.9%", "1.178×"],
    ], [2.6, 2.6, 2.8], mono_cols=(2,), head_fill="3A424C", head_fg=PAPER,
        hi_rows=(2,), hi_fill=RED_DIM, row_h=Inches(0.56), zebra=False)
    T.txt(s, M, Inches(4.95), Inches(11.2), Inches(1.2),
          [[("加速比从 1× 到 16.26×，靠的不是更快的硬件，",
             19, False, WHITE_DIM)],
           [("而是每一次都把资源投在当时真正的瓶颈上。", 22, True, PAPER)]],
          spacing=1.45)
    T.foot(s, FOOT, dark=True)

    T.punch(prs,
            [("最优，", False),
             ("是相对某个指标、某条预算线说的。", False),
             ("离开这两样，这个词没有意义。", True)],
            sub="——《计算机系统综合设计实验》全课程结束", accent=ACC)

    prs.save(os.path.abspath(OUT))
    print("wrote %s  (%d slides)" % (os.path.abspath(OUT), len(prs.slides._sldIdLst)))


if __name__ == "__main__":
    build()
