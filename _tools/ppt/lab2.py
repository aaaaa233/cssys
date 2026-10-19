# -*- coding: utf-8 -*-
"""实验二《存储层次设计空间探索》讲课用 PPT。

    python _tools/ppt/lab2.py            → labs/lab2/幻灯片.pptx

所有数字来自 labs/lab2/参考解答.md，改数据请同步改那一处。
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
                   "..", "..", "labs", "lab2", "幻灯片.pptx")

ACC = T.LAB_ACCENT[2]          # 青
FOOT = "实验二　存储层次设计空间探索"


# ------------------------------------------------------------------ 水平条形图
def hbars(slide, x, y, w, rows, bar_h=Inches(0.4), gap=Inches(0.24),
          label_w=Inches(1.6), val_w=Inches(1.85), maxv=None,
          label_size=14, value_size=13):
    """并排水平条：rows = [(标签, 数值, 颜色, 数值文字), ...]，按最大值归一化。"""
    mx = maxv or max(r[1] for r in rows)
    track = w - label_w - val_w
    for k, (lab, val, color, vtxt) in enumerate(rows):
        yy = y + (bar_h + gap) * k
        T.txt(slide, x, yy, label_w - Inches(0.18), bar_h,
              [(lab, label_size, True, INK)], anchor=MSO_ANCHOR.MIDDLE)
        seg = max(int(track * val / mx), Inches(0.03))
        T.rect(slide, x + label_w, yy, seg, bar_h, color)
        T.txt(slide, x + label_w + seg + Inches(0.16), yy, val_w, bar_h,
              [(vtxt, value_size, True, color, True)],
              anchor=MSO_ANCHOR.MIDDLE)
    return y + (bar_h + gap) * len(rows) - gap


def build():
    prs = T.new_deck()

    # ======================================================== 00 封面
    T.cover(prs, 2,
            "存储层次设计空间探索",
            "核心问题：给定面积预算，容量、相联度、块大小怎么分配\n"
            "同样一块硅片，四个花法——交一份配置提案，并说明为什么不是另外三个",
            "计算机系统综合设计实验　·　4 学时　·　负载 qnn（100.7 KB 工作集）")

    # ======================================================== 01 立题
    T.punch(prs,
            [("Cache 的收益不是渐进的。", False),
             ("它是一个阶跃。", True),
             ("你得先知道台阶在哪，", False),
             ("才知道钱花下去有没有响。", True)],
            sub="本次实验会给你四条曲线，其中三条的第一直觉都是错的。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "今天要你做出的决策", kicker="任务", accent=ACC)
    T.txt(s, M, y, Inches(7.7), Inches(1.3),
          [[("你有一份固定的", 22, False, INK),
            ("硅片面积预算", 22, True, ACC),
            ("。", 22, False, INK)],
           [("它该花在哪一个方向？", 22, False, INK)]], spacing=1.35)

    T.bullets(s, M, y + Inches(1.62), Inches(7.6), [
        [("L1D ", 15.5, True, INK, True), ("更大", 15.5, True, INK),
         ("　—— 容量，任务 1", 15.5, False, INK_SOFT)],
        [("相联度", 15.5, True, INK), ("更高", 15.5, True, INK),
         ("　—— 冲突，任务 2", 15.5, False, INK_SOFT)],
        [("块", 15.5, True, INK), ("更大", 15.5, True, INK),
         ("　—— 空间局部性，任务 3", 15.5, False, INK_SOFT)],
        [("面积挪给 ", 15.5, True, INK), ("L2", 15.5, True, INK, True),
         ("　—— 层次结构，任务 5", 15.5, False, INK_SOFT)],
    ], gap=Inches(0.55), marker=(ACC, ACC, ACC, INK_SOFT))

    T.note(s, M, y + Inches(3.72), Inches(7.6),
           "交付物是一份配置提案，要回答「为什么不是另外三个」。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.stat(s, Inches(9.1), y + Inches(0.1), Inches(3.5), "23.3%",
           "换对方向能拿到的加速", color=GREEN, size=54,
           sub="32kB → 128kB，一步到位")
    T.stat(s, Inches(9.1), y + Inches(2.3), Inches(3.5), "9.3%",
           "换错方向亏掉的性能", color=RED, size=54,
           sub="L2 从 128kB 加到 2MB")
    T.foot(s, FOOT)

    # ======================================================== 03 一条主线
    s = T.blank(prs)
    y = T.head(s, "先算一个数，再跑第一次仿真",
               kicker="§0　动手之前", accent=ACC)

    T.table(s, M, y, Inches(6.5), [
        ["数组", "尺寸", "字节数"],
        ["w1[128][784]", "128 × 784 × 1B", "100,352"],
        ["w2[10][128]", "10 × 128 × 1B", "1,280"],
        ["b1[128]", "128 × 4B", "512"],
        ["xbuf[784]", "784 × 1B", "784"],
        ["其余", "", "~208"],
        ["合计", "", "≈ 100.7 KB"],
    ], col_w=[2.3, 2.4, 1.8], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(0,), hi_rows=(6,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(3.33), Inches(6.5), Inches(0.5),
          [[("其中 ", 15, False, INK), ("98 KB 是 w1", 15, True, RED),
            ("，每个样本要完整扫两遍。", 15, False, INK)]])

    T.card(s, Inches(7.75), y - Inches(0.05), Inches(4.85), Inches(3.72))
    T.txt(s, Inches(8.1), y + Inches(0.3), Inches(4.2), Inches(3.1),
          [[("本次实验几乎", 17, True, INK)],
           [("每一条曲线的形状", 26, True, ACC)],
           [("都由这一个数决定", 17, True, INK)],
           [("", 8, False, INK)],
           [("8~64kB 越大越慢：都装不下", 14, False, INK)],
           [("128kB 突变：装下了", 14, False, INK)],
           [("64kB 时 LRU 输给随机：颠簸", 14, False, INK)],
           [("块越大越好：连续扫描", 14, False, INK)]], spacing=1.32)
    T.foot(s, FOOT)

    # ======================================================== 04 §01 节间
    T.section(prs, "01", "Cache 在解决什么问题",
              "只补三样东西：3C、MSHR、以及「越大越好」为什么是错的",
              accent=ACC)

    # ======================================================== 05 存储墙
    s = T.blank(prs)
    y = T.head(s, "Cache 是一场关于局部性的赌博",
               kicker="§1.1　存储墙", accent=ACC)

    T.card(s, M, y, Inches(5.72), Inches(2.45))
    T.txt(s, M + Inches(0.4), y + Inches(0.3), Inches(4.9), Inches(1.9),
          [[("时间局部性", 20, True, INK)],
           [("", 7, False, INK)],
           [("刚用过的，很可能马上还要用。", 14.5, False, INK)],
           [("循环变量、栈上的局部变量。", 14.5, False, INK)],
           [("靠", 14.5, False, INK), ("容量", 14.5, True, ACC),
            ("兑现。", 14.5, False, INK)]], spacing=1.32)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.45))
    T.txt(s, M + Inches(6.51), y + Inches(0.3), Inches(4.9), Inches(1.9),
          [[("空间局部性", 20, True, INK)],
           [("", 7, False, INK)],
           [("用了 a[i]，很可能马上用 a[i+1]。", 14.5, False, INK)],
           [("Cache 按块搬，一块 64 字节。", 14.5, False, INK)],
           [("靠", 14.5, False, INK), ("块大小", 14.5, True, ACC),
            ("兑现。", 14.5, False, INK)]], spacing=1.32)

    T.txt(s, M, y + Inches(2.85), CONTENT_W, Inches(0.5),
          [[("一次失效就把整块搬进来 —— ", 17, False, INK),
            ("这是在赌下一个字节你也要用。", 17, True, INK)]])

    T.note(s, M, y + Inches(3.55), CONTENT_W,
           "赌对了叫空间局部性，赌错了叫浪费带宽。任务 3 会让你在两个负载上各看一次。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 06 3C
    s = T.blank(prs)
    y = T.head(s, "三种失效，三种对策", kicker="§1.2　3C 模型", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["失效类型", "什么时候发生", "唯一的对策", "本次实验"],
        ["强制失效  compulsory", "这个块第一次被访问", "更大的块 / 预取", "任务 3"],
        ["容量失效  capacity", "装不下工作集，被挤出去", "更大的容量", "任务 1"],
        ["冲突失效  conflict", "容量够，几个块争同一组", "更高的相联度", "任务 2"],
    ], col_w=[3.0, 3.6, 2.7, 1.5], size=15, head_size=13,
        row_h=Inches(0.68),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(2.98), CONTENT_W, Inches(0.9),
          [[("测出失效变多变少时，第一件事是判断", 17, False, INK),
            ("变的是哪一个 C", 17, True, RED),
            ("。", 17, False, INK)],
           [("三个 C 的对策完全不同，判错了就会把面积花在错误的地方。",
             15, False, INK_SOFT)]], spacing=1.45)

    T.note(s, M, y + Inches(3.88), CONTENT_W,
           "任务 2 会给你一个 3C 解释不了的结果。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 07 MSHR
    s = T.blank(prs)
    y = T.head(s, "本次实验的第一条纪律",
               kicker="§1.4　MSHR 与 MLP", accent=ACC)

    T.txt(s, M, y, Inches(8.0), Inches(0.6),
          [[("失效次数", 20, True, INK), ("  =  ", 20, False, INK_SOFT),
            ("被 MSHR 合并的", 20, True, INK_SOFT), ("  +  ", 20, False, INK_SOFT),
            ("真正下到 L2 的", 20, True, RED)]])
    T.txt(s, M, y + Inches(0.52), Inches(8.0), Inches(0.5),
          [[("misses", 14, False, INK_SOFT, True),
            ("            mshr_hits", 14, False, INK_SOFT, True),
            ("           mshr_misses", 14, True, RED, True)]])

    T.bullets(s, M, y + Inches(1.42), Inches(7.8), [
        [("看 ", 16, False, INK), ("l1d_mshr_mpki", 16, True, RED, True),
         ("：真实访存流量，只随程序和 Cache 配置变", 16, False, INK)],
        [("不看 ", 16, False, INK), ("l1d_miss_rate", 16, True, INK_SOFT, True),
         ("：被乱序核的重复访问严重放大", 16, False, INK)],
        [("MLP = misses / mshr_misses：平均有几个失效同时在飞",
          16, False, INK)],
    ], gap=Inches(0.6), marker=(RED, INK_SOFT, ACC))

    T.note(s, M, y + Inches(3.42), Inches(7.8),
           "凡是用 miss_rate 论证「Cache 不够大」的，本次实验直接扣机制分。",
           color=RED, fill=RED_DIM, size=14.5, icon="★")

    T.card(s, Inches(9.05), y - Inches(0.05), Inches(3.55), Inches(4.12))
    T.txt(s, Inches(9.4), y + Inches(0.3), Inches(2.9), Inches(3.5),
          [[("任务 4 会证明", 17, True, INK)],
           [("失效率", 26, True, ACC)],
           [("不是程序的属性", 17, True, INK)],
           [("", 6, False, INK)],
           [("程序没变，数据没变，", 14, False, INK)],
           [("Cache 配置也没变。", 14, False, INK)],
           [("", 6, False, INK)],
           [("只把一个队列从 1 加到 2，", 14, False, INK)],
           [("失效率变了 15 倍。", 14, True, RED)]], spacing=1.32)
    T.foot(s, FOOT)

    # ======================================================== 08 越大越好是错的
    s = T.blank(prs)
    y = T.head(s, "「越大越好」为什么是错的",
               kicker="§1.5　真正的权衡", accent=ACC)

    T.txt(s, M, y, Inches(7.9), Inches(0.6),
          [[("AMAT  =  ", 20, True, INK, True),
            ("命中延迟", 20, True, RED),
            ("  +  ", 20, False, INK_SOFT),
            ("失效率", 20, True, GREEN),
            ("  ×  失效代价", 20, False, INK)]])
    T.txt(s, M, y + Inches(0.55), Inches(7.9), Inches(0.4),
          [[("                 随容量 ↑", 13.5, True, RED),
            ("        随容量 ↓", 13.5, True, GREEN)]])

    T.code(s, M, y + Inches(1.2), Inches(7.9), [
        "# framework/cssys_se.py：以 32kB / 3 周期为基准",
        "l1_latency = base + log2(size / 32kB)   # 每翻一番 +1 周期",
    ], size=13.5, hi=(1,))

    T.txt(s, M, y + Inches(2.42), Inches(7.9), Inches(0.9),
          [[("物理原因：容量大 → 字线位线更长 → 寄生电容更大 → 充放电更慢。",
             15, False, INK)],
           [("真实芯片里不存在免费变大的 Cache。", 15, True, INK)]],
          spacing=1.45)

    T.note(s, M, y + Inches(3.62), Inches(7.9),
           "两项一升一降，最优点在中间某处 —— 这就是今天要找的东西。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.card(s, Inches(9.1), y - Inches(0.05), Inches(3.5), Inches(4.12))
    T.txt(s, Inches(9.45), y + Inches(0.3), Inches(2.85), Inches(3.5),
          [[("任务 1 有个开关", 17, True, INK)],
           [("关掉延迟", 26, True, ACC)],
           [("--auto-latency off", 13, True, INK_SOFT, True)],
           [("", 6, False, INK)],
           [("关掉之后曲线变成", 14, False, INK)],
           [("干净的「越大越好」。", 14, False, INK)],
           [("", 6, False, INK)],
           [("那是一个因为模型缺失", 14, False, INK)],
           [("而产生的假结论。", 14, True, RED)]], spacing=1.32)
    T.foot(s, FOOT)

    # ======================================================== 09 §02 节间
    T.section(prs, "02", "容量：找到那个拐点",
              "任务 1　·　六个容量，两条曲线，一个反直觉的中段",
              accent=ACC)

    # ======================================================== 10 容量扫描
    s = T.blank(prs)
    y = T.head(s, "越大越慢，直到突然变快",
               kicker="任务 1　实测", accent=ACC)
    T.table(s, M, y, Inches(8.3), [
        ["L1D 容量", "周期数", "IPC", "miss_rate", "mshr_mpki"],
        ["8kB", "1,049,689", "5.527", "11.44%", "2.210"],
        ["16kB", "1,074,577", "5.399", "12.20%", "2.210"],
        ["32kB（基线）", "1,099,658", "5.276", "12.20%", "2.210"],
        ["64kB", "1,137,187", "5.102", "12.20%", "2.209"],
        ["128kB", "891,719", "6.506", "0.01%", "0.002"],
        ["256kB", "1,013,040", "5.727", "0.01%", "0.038"],
    ], col_w=[2.0, 1.9, 1.2, 1.5, 1.7], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(1, 2, 3, 4), hi_rows=(5,))

    T.txt(s, M, y + Inches(3.30), Inches(8.3), Inches(0.5),
          [[("8kB → 64kB 一路变慢，", 16, False, INK),
            ("128kB 一步快 23.3%", 16, True, GREEN),
            ("，256kB 又慢回去。", 16, False, INK)]])

    T.note(s, M, y + Inches(3.86), Inches(8.3),
           "最后一列全程 2.210 —— 那才是这张表真正要你看的。",
           color=RED, fill=RED_DIM, size=14.5, icon="★")

    T.stat(s, Inches(9.35), y + Inches(0.35), Inches(3.3), "128kB",
           "最优容量", color=GREEN, size=44,
           sub="比基线快 1.233 倍")
    T.stat(s, Inches(9.35), y + Inches(2.35), Inches(3.3), "13.6%",
           "256kB 相对它慢了", color=RED, size=44,
           sub="装下之后再大只剩延迟")
    T.foot(s, FOOT)

    # ======================================================== 11 punch
    T.punch(prs,
            [("从 8kB 到 64kB，", False),
             ("真正下到 L2 的流量", False),
             ("一个字节都没变。", True)],
            sub="容量增大一点收益都没产生，却实打实付了三个周期的命中延迟。",
            accent=ACC)

    # ======================================================== 12 阶跃
    s = T.blank(prs)
    y = T.head(s, "收益是阶跃的，代价是渐进的",
               kicker="任务 1　问题 2、3", accent=ACC)

    hbars(s, M, y + Inches(0.05), Inches(8.3), [
        ("8kB", 2.210, INK_SOFT, "mshr_mpki 2.210"),
        ("16kB", 2.210, INK_SOFT, "2.210"),
        ("32kB", 2.210, INK_SOFT, "2.210"),
        ("64kB", 2.209, INK_SOFT, "2.209"),
        ("128kB", 0.002, GREEN, "0.002　降 1000 倍"),
        ("256kB", 0.002, GREEN, "0.002"),
    ], bar_h=Inches(0.30), gap=Inches(0.15), label_w=Inches(1.3),
        val_w=Inches(2.6), label_size=13.5, value_size=12.5)

    T.txt(s, M, y + Inches(3.00), Inches(8.3), Inches(0.9),
          [[("工作集 98 KB。8kB 装不下，64kB 也装不下 —— ",
             15.5, False, INK),
            ("搬运次数只由「工作集 ÷ 块大小」决定，和 Cache 多大无关。",
             15.5, True, INK)]], spacing=1.45)

    T.note(s, M, y + Inches(3.86), Inches(8.3),
           "装下之前收益严格为零，装下那一刻一次性全部兑现。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.card(s, Inches(9.35), y - Inches(0.05), Inches(3.25), Inches(4.28))
    T.txt(s, Inches(9.7), y + Inches(0.32), Inches(2.6), Inches(3.6),
          [[("所以最优点", 16, True, INK)],
           [("必然出现在", 26, True, ACC)],
           [("刚好装下", 26, True, ACC)],
           [("的那个容量", 16, True, INK)],
           [("", 8, False, INK)],
           [("再往上，只剩延迟。", 13.5, False, INK_SOFT)],
           [("再往下，一点不省。", 13.5, False, INK_SOFT)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 13 关掉延迟
    s = T.blank(prs)
    y = T.head(s, "把延迟模型关掉，曲线变好看了",
               kicker="任务 1　问题 5~7", accent=ACC)
    T.table(s, M, y, Inches(7.4), [
        ["L1D 容量", "延迟模型 开", "延迟模型 关"],
        ["8kB", "1,049,689", "1,099,658"],
        ["16kB", "1,074,577", "1,099,658"],
        ["32kB", "1,099,658", "1,099,658"],
        ["64kB", "1,137,187", "1,099,658"],
        ["128kB", "891,719", "890,617"],
        ["256kB", "1,013,040", "890,617"],
    ], col_w=[2.2, 2.6, 2.6], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(1, 2))

    T.txt(s, M, y + Inches(3.42), Inches(7.4), Inches(0.9),
          [[("关掉之后只剩两个值：曲线变成", 15.5, False, INK),
            ("纯粹的阶梯函数", 15.5, True, RED),
            ("，单调不增。", 15.5, False, INK)],
           [("只看这一条，结论是「越大越好，选 256kB」。",
             15.5, False, INK_SOFT)]], spacing=1.45)

    T.card(s, Inches(8.55), y - Inches(0.05), Inches(4.05), Inches(4.28))
    T.txt(s, Inches(8.9), y + Inches(0.32), Inches(3.4), Inches(3.6),
          [[("和实验一连起来看", 16, True, INK)],
           [("", 6, False, INK)],
           [("实验一：模型", 14.5, False, INK),
            ("多建了", 14.5, True, RED), ("串行化", 14.5, False, INK)],
           [("→ 结论方向错", 14.5, False, INK_SOFT)],
           [("", 8, False, INK)],
           [("实验二：模型", 14.5, False, INK),
            ("少建了", 14.5, True, RED), ("延迟代价", 14.5, False, INK)],
           [("→ 结论方向也错", 14.5, False, INK_SOFT)],
           [("", 8, False, INK)],
           [("两次都错，", 16, True, INK)],
           [("而且都不会报错。", 16, True, RED)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 14 punch
    T.punch(prs,
            [("模型没建模的东西，", False),
             ("不会以「缺失」的形式出现，", False),
             ("而会以一个干净漂亮", False),
             ("但错误的结论的形式出现。", True)],
            sub="关掉延迟之后曲线更好看了 —— 危险恰恰在这里。",
            accent=ACC)

    # ======================================================== 15 §03 节间
    T.section(prs, "03", "相联度：课本在这里失灵",
              "任务 2　·　直接映射打赢 8 路组相联，而且不是噪声",
              accent=ACC)

    # ======================================================== 16 相联度
    s = T.blank(prs)
    y = T.head(s, "64kB 时，直接映射反而更好",
               kicker="任务 2　问题 1", accent=ACC)

    T.txt(s, M, y, Inches(8.3), Inches(0.34),
          [("l1d_mshr_mpki（真实访存流量）", 13.5, True, INK_SOFT)])
    T.table(s, M, y + Inches(0.38), Inches(8.3), [
        ["容量", "1 路", "2 路", "4 路", "8 路"],
        ["32kB", "2.271", "2.210", "2.210", "2.210"],
        ["64kB", "1.630", "2.209", "2.208", "2.208"],
        ["128kB", "0.002", "0.002", "0.002", "0.002"],
    ], col_w=[1.8, 1.6, 1.6, 1.6, 1.6], size=14, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(1, 2, 3, 4), hi_rows=(2,))

    T.txt(s, M, y + Inches(2.36), Inches(8.3), Inches(0.34),
          [("周期数", 13.5, True, INK_SOFT)])
    T.table(s, M, y + Inches(2.74), Inches(8.3), [
        ["容量", "1 路", "2 路", "4 路", "8 路"],
        ["64kB", "1,072,919", "1,137,187", "1,137,187", "1,137,187"],
    ], col_w=[1.8, 1.6, 1.6, 1.6, 1.6], size=14, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(1, 2, 3, 4), hi_rows=(1,))

    T.note(s, M, y + Inches(3.92), Inches(8.3),
           "流量少 26%，周期少 5.6%。这与课本直接矛盾。",
           color=RED, fill=RED_DIM, size=15, icon="★")

    T.card(s, Inches(9.35), y - Inches(0.05), Inches(3.25), Inches(4.35))
    T.txt(s, Inches(9.7), y + Inches(0.32), Inches(2.6), Inches(3.7),
          [[("课本说", 16, True, INK)],
           [("相联度越高", 24, True, INK_SOFT)],
           [("失效越少", 24, True, INK_SOFT)],
           [("", 8, False, INK)],
           [("这里", 16, True, INK)],
           [("反了", 34, True, RED)],
           [("", 6, False, INK)],
           [("而且差 26%，", 13.5, False, INK)],
           [("远超噪声地板。", 13.5, False, INK)]], spacing=1.28)
    T.foot(s, FOOT)

    # ======================================================== 17 3C 的前提
    s = T.blank(prs)
    y = T.head(s, "不是课本错了，是它有前提",
               kicker="任务 2　问题 2", accent=ACC)

    T.card(s, M, y, Inches(5.72), Inches(2.6), RED_DIM)
    T.txt(s, M + Inches(0.4), y + Inches(0.32), Inches(4.9), Inches(2.0),
          [[("✗　不给分的答案", 17, True, RED)],
           [("", 8, False, INK)],
           [("「3C 模型是错的」", 16, False, INK)],
           [("", 6, False, INK)],
           [("一个用了四十年的模型，", 14, False, INK_SOFT)],
           [("不会因为你跑了一次就错了。", 14, False, INK_SOFT)]],
          spacing=1.3)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.6), GREEN_DIM)
    T.txt(s, M + Inches(6.51), y + Inches(0.32), Inches(4.9), Inches(2.0),
          [[("✓　满分答案", 17, True, GREEN)],
           [("", 8, False, INK)],
           [("「3C 模型假设替换策略合理」", 16, False, INK)],
           [("", 6, False, INK)],
           [("冲突失效的定义本身，", 14, False, INK_SOFT)],
           [("就把替换策略当成了良性的。", 14, False, INK_SOFT)]],
          spacing=1.3)

    T.txt(s, M, y + Inches(2.92), CONTENT_W, Inches(0.9),
          [[("一旦替换策略在某个访问模式下退化，", 17, False, INK),
            ("提高相联度反而会放大它的错误。", 17, True, RED)],
           [("直接映射没有这个问题 —— 它根本没有「选择」，也就无从选错。",
             16, False, INK)]], spacing=1.5)

    T.note(s, M, y + Inches(3.84), CONTENT_W,
           "这一问要的不是「课本错了」，是「课本的适用条件是什么」。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 18 LRU vs Random
    s = T.blank(prs)
    y = T.head(s, "换成随机替换，课本就回来了",
               kicker="任务 2(b)　64kB", accent=ACC)
    T.table(s, M, y, Inches(8.3), [
        ["相联度", "LRU mshr_mpki", "LRU 周期", "Random mshr_mpki", "Random 周期"],
        ["1 路", "1.630", "1,072,919", "1.630", "1,072,919"],
        ["2 路", "2.209", "1,137,187", "1.586", "1,075,846"],
        ["4 路", "2.208", "1,137,187", "1.489", "1,066,383"],
        ["8 路", "2.208", "1,137,187", "1.457", "1,064,135"],
    ], col_w=[1.4, 1.9, 1.7, 2.0, 1.7], size=13.5, head_size=11.5,
        row_h=Inches(0.46), mono_cols=(1, 2, 3, 4), hi_rows=(1,))

    T.txt(s, M, y + Inches(2.68), Inches(8.3), Inches(0.9),
          [[("Random：1.630 → 1.457，", 15.5, False, INK),
            ("单调下降，符合课本。", 15.5, True, GREEN)],
           [("LRU：1.630 → 2.209，", 15.5, False, INK),
            ("1 路到 2 路不降反升 35%。", 15.5, True, RED)]], spacing=1.5)

    T.note(s, M, y + Inches(3.88), Inches(8.3),
           "第一行两边逐位相同 —— 这不是巧合，是你的实验自检。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.card(s, Inches(9.35), y - Inches(0.05), Inches(3.25), Inches(4.35))
    T.txt(s, Inches(9.7), y + Inches(0.32), Inches(2.6), Inches(3.7),
          [[("1 路时两种策略", 15.5, True, INK)],
           [("必须相同", 26, True, ACC)],
           [("", 8, False, INK)],
           [("每组只有一个位置，", 14, False, INK)],
           [("没有可供选择的余地，", 14, False, INK)],
           [("策略根本不被调用。", 14, False, INK)],
           [("", 8, False, INK)],
           [("没做这个自检就报结论，", 13.5, False, INK_SOFT)],
           [("扣方法学分。", 13.5, True, RED)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 19 LRU 为什么输
    s = T.blank(prs)
    y = T.head(s, "LRU 在这里是最坏策略",
               kicker="任务 2　问题 5　★核心", accent=ACC)

    T.txt(s, M, y, Inches(8.4), Inches(0.34),
          [("w1 数组 98 KB，Cache 只有 64 KB", 14, True, INK_SOFT)])
    T.area_blocks(s, M, y + Inches(0.42), Inches(8.4), Inches(0.72), [
        ("开头 34 KB　马上要用", 34, RED, PAPER),
        ("末尾 64 KB　LRU 留着的", 64, INK_SOFT, PAPER),
    ], label_size=13)

    T.bullets(s, M, y + Inches(1.5), Inches(8.4), [
        [("每个样本把 w1 从头扫到尾，下个样本再扫一遍 —— ", 15, False, INK),
         ("周期性循环扫描", 15, True, INK)],
        [("扫到末尾要回到 w1[0] 时，LRU 保留的是", 15, False, INK),
         ("刚用过的末尾", 15, True, INK_SOFT)],
        [("而马上要用的是开头 —— ", 15, False, INK),
         ("恰恰是 LRU 刚刚淘汰掉的", 15, True, RED)],
        [("于是每一次访问都失效，命中率趋近于 0", 15, True, RED)],
    ], gap=Inches(0.55), marker=(INK_SOFT, INK_SOFT, RED, RED))

    T.note(s, M, y + Inches(3.76), Inches(8.4),
           "扫描型访问下，LRU 的核心假设系统性地反向失效。",
           color=RED, fill=RED_DIM, size=14, icon="★")

    T.card(s, Inches(9.45), y + Inches(0.42), Inches(3.15), Inches(3.5))
    T.txt(s, Inches(9.78), y + Inches(0.76), Inches(2.5), Inches(2.9),
          [[("随机替换", 15.5, True, INK)],
           [("期望命中率", 15.5, True, INK)],
           [("", 6, False, INK)],
           [("1 − C / W", 24, True, ACC, True)],
           [("", 6, False, INK)],
           [("1 − 64/98 ≈ 35%", 15, True, INK, True)],
           [("", 6, False, INK)],
           [("实测流量降 34%", 15, True, GREEN)],
           [("2.209 → 1.457", 13.5, False, INK_SOFT, True)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 20 punch
    T.punch(prs,
            [("先算出 35%，", False),
             ("再跑出 34%。", True),
             ("这才叫做实验。", False)],
            sub="理论预测 → 实测验证，本次实验最漂亮的一次闭环。让学生自己算一遍。",
            accent=ACC)

    # ======================================================== 21 RRIP
    s = T.blank(prs)
    y = T.head(s, "抗颠簸策略没兑现承诺",
               kicker="思考题 3　·　64kB / 4 路", accent=ACC)
    T.table(s, M, y, Inches(7.0), [
        ["替换策略", "mshr_mpki", "周期数", "相对 LRU"],
        ["lru", "2.208", "1,137,187", "—"],
        ["fifo", "2.237", "1,138,287", "+0.1%"],
        ["nru", "2.203", "1,136,742", "−0.04%"],
        ["rrip", "2.205", "1,136,991", "−0.02%"],
        ["brrip", "2.203", "1,136,808", "−0.03%"],
        ["random", "1.489", "1,066,383", "−6.2%"],
    ], col_w=[1.8, 1.7, 1.9, 1.6], size=13.5, head_size=12.5,
        row_h=Inches(0.40), mono_cols=(0, 1, 2, 3), hi_rows=(6,))

    T.txt(s, M, y + Inches(2.96), Inches(7.0), Inches(0.6),
          [[("RRIP 和 BRRIP 号称抗颠簸，实测和 LRU 没有任何区别。",
             15, False, INK)],
           [("只有 random 逃出了病态。", 15, True, RED)]], spacing=1.45)

    T.card(s, Inches(8.15), y - Inches(0.05), Inches(4.45), Inches(4.32))
    T.txt(s, Inches(8.5), y + Inches(0.32), Inches(3.8), Inches(3.7),
          [[("这不是 bug，是实测结果", 16, True, INK)],
           [("", 8, False, INK)],
           [("✗　「因此 RRIP 没用」", 14.5, True, RED)],
           [("　　一次实现的一次测量，", 13.5, False, INK_SOFT)],
           [("　　不能判决一个算法", 13.5, False, INK_SOFT)],
           [("", 7, False, INK)],
           [("✗　无视实测，照抄论文", 14.5, True, RED)],
           [("", 7, False, INK)],
           [("✓　报告结果 + 承认不符", 14.5, True, GREEN)],
           [("　　+ 两条可能原因", 14.5, True, GREEN)],
           [("　　+ 怎么进一步验证", 14.5, True, GREEN)]], spacing=1.26)

    T.note(s, M, y + Inches(3.86), Inches(7.0),
           "论文里的算法、模拟器里的实现、实现的默认参数，是三样不同的东西。",
           color=ACC, fill=PAPER_DIM, size=13.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 22 §04 节间
    T.section(prs, "04", "块大小：三股力量在拔河",
              "任务 3　·　先预测再验证，然后解释一次 5 倍的崩塌",
              accent=ACC)

    # ======================================================== 23 预测
    s = T.blank(prs)
    y = T.head(s, "跑之前就能算出失效次数",
               kicker="任务 3(a)　预测与验证", accent=ACC)

    T.txt(s, M, y, Inches(8.4), Inches(0.5),
          [[("每样本失效数  ≈  ", 18, False, INK),
            ("100.7 KB", 18, True, ACC, True),
            ("  ÷  ", 18, False, INK_SOFT),
            ("块大小", 18, True, INK, True)]])

    T.table(s, M, y + Inches(0.72), Inches(8.4), [
        ["块大小", "预测每样本失效", "预测 mshr_mpki", "实测 mshr_mpki", "误差"],
        ["16B", "6,446", "8.89", "8.838", "−0.6%"],
        ["32B", "3,223", "4.45", "4.421", "−0.6%"],
        ["64B", "1,611", "2.22", "2.210", "−0.5%"],
        ["128B", "806", "1.11", "1.104", "−0.5%"],
        ["256B", "403", "0.56", "0.552", "−0.5%"],
    ], col_w=[1.4, 2.0, 1.9, 1.9, 1.2], size=13.5, head_size=11.5,
        row_h=Inches(0.42), mono_cols=(1, 2, 3, 4))

    T.txt(s, M, y + Inches(3.32), Inches(8.4), Inches(0.6),
          [[("块大小翻倍，mshr_mpki ", 15.5, False, INK),
            ("严格减半", 15.5, True, GREEN),
            (" —— 搬运的总字节数完全不变。", 15.5, False, INK)]])

    T.note(s, M, y + Inches(3.84), Inches(8.4),
           "分子由算法决定，分母由硬件决定。这就是软硬件协同的算式形式。",
           color=ACC, fill=PAPER_DIM, size=14, icon="※")

    T.stat(s, Inches(9.5), y + Inches(0.9), Inches(3.1), "0.6%",
           "五个块大小的预测误差", color=GREEN, size=52,
           sub="而且五次误差完全一致")
    T.foot(s, FOOT)

    # ======================================================== 24 punch
    T.punch(prs,
            [("能预测的实验才叫实验，", False),
             ("否则只是在采集数据。", True)],
            sub="用源码里的数组尺寸，在没跑任何仿真之前就算出失效次数，误差 0.5%。",
            accent=ACC)

    # ======================================================== 25 边际收益
    s = T.blank(prs)
    y = T.head(s, "失效降 16 倍，时间只降 5 倍",
               kicker="任务 3(b)　问题 3", accent=ACC)
    T.table(s, M, y, Inches(7.6), [
        ["块大小", "周期数", "IPC", "mshr_mpki", "MLP"],
        ["16B", "4,982,012", "1.165", "8.838", "2.99"],
        ["32B", "1,286,370", "4.510", "4.421", "15.58"],
        ["64B", "1,099,658", "5.276", "2.210", "15.60"],
        ["128B", "1,007,524", "5.758", "1.104", "15.61"],
        ["256B", "961,473", "6.034", "0.552", "15.61"],
    ], col_w=[1.4, 1.9, 1.2, 1.7, 1.2], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(1, 2, 3, 4), hi_rows=(1,))

    T.txt(s, M, y + Inches(2.82), Inches(7.6), Inches(0.9),
          [[("排除异常的 16B：32B → 256B 失效降 8 倍，周期只降 ",
             15.5, False, INK),
            ("1.34 倍", 15.5, True, RED), ("。", 15.5, False, INK)],
           [("乱序核把失效延迟重叠掉了（MLP ≈ 15.6），边际收益急剧递减。",
             15.5, False, INK)]], spacing=1.45)

    T.card(s, Inches(8.7), y - Inches(0.05), Inches(3.9), Inches(4.32))
    T.txt(s, Inches(9.05), y + Inches(0.32), Inches(3.25), Inches(3.7),
          [[("和实验一任务 4 连起来", 15.5, True, INK)],
           [("", 8, False, INK)],
           [("timing 核（MLP = 1）", 15, True, INK, True)],
           [("失效降 8 倍 = 时间降 8 倍", 14, False, INK)],
           [("", 8, False, INK)],
           [("o3 核（MLP = 15.6）", 15, True, INK, True)],
           [("失效降 8 倍 = 时间降 1.34 倍", 14, False, INK)],
           [("", 10, False, INK)],
           [("同一个硬件改进，", 15.5, True, INK)],
           [("在不同的核上价值完全不同。", 15.5, True, ACC)]], spacing=1.28)

    T.note(s, M, y + Inches(3.84), Inches(7.6),
           "优化的价值取决于它周围的系统。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 26 证伪
    s = T.blank(prs)
    y = T.head(s, "一个合理的假设，被自己的实验否定",
               kicker="任务 3　问题 4　★★", accent=ACC)

    T.txt(s, M, y, Inches(8.3), Inches(0.5),
          [[("假设：16B 崩塌是因为 ", 17, False, INK),
            ("MSHR 不够用了", 17, True, INK),
            ("。", 17, False, INK)]])

    T.table(s, M, y + Inches(0.68), Inches(8.3), [
        ["块大小", "MSHR = 4", "MSHR = 16", "MSHR = 64"],
        ["16B", "4,982,012", "4,981,985", "4,982,483"],
        ["32B", "1,286,370", "1,286,551", "1,286,551"],
        ["64B", "1,099,658", "1,099,658", "1,099,658"],
    ], col_w=[1.6, 2.2, 2.2, 2.2], size=14, head_size=12.5,
        row_h=Inches(0.46), mono_cols=(1, 2, 3), hi_rows=(1,))

    T.code(s, M, y + Inches(2.72), Inches(8.3), [
        "system.cpu.dcache.blockedCycles::no_mshrs = 0    # 全部配置，恒为 0",
    ], size=13.5, hi=(0,))

    T.txt(s, M, y + Inches(3.58), Inches(8.3), Inches(0.6),
          [[("MSHR 从 4 加到 64，性能纹丝不动。", 16, False, INK),
            ("假设被彻底否定。", 16, True, RED)]])

    T.card(s, Inches(9.35), y + Inches(0.68), Inches(3.25), Inches(3.5))
    T.txt(s, Inches(9.7), y + Inches(1.0), Inches(2.6), Inches(2.9),
          [[("这一步的价值", 15.5, True, INK)],
           [("不在猜对", 24, True, ACC)],
           [("", 8, False, INK)],
           [("提出假设 → 设计能证伪", 14, False, INK)],
           [("的实验 → 接受被否定", 14, False, INK)],
           [("→ 继续找真因", 14, False, INK)],
           [("", 8, False, INK)],
           [("这就是正确的工作方式，", 14, True, GREEN)],
           [("满分。", 14, True, GREEN)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 27 取指侧
    s = T.blank(prs)
    y = T.head(s, "真因在取指侧，不在数据通路",
               kicker="任务 3　问题 5", accent=ACC)
    T.table(s, M, y, Inches(8.4), [
        ["块大小", "fetch.cacheLines", "icacheStallCycles", "总周期", "取指停顿占比"],
        ["16B", "1,660,295", "3,319,880", "4,982,012", "66.6%"],
        ["32B", "20,781", "42,003", "1,286,370", "3.3%"],
        ["64B", "6,546", "13,466", "1,099,658", "1.2%"],
    ], col_w=[1.3, 2.1, 2.1, 1.8, 1.6], size=13.5, head_size=11,
        row_h=Inches(0.46), mono_cols=(1, 2, 3, 4), hi_rows=(1,))

    T.bullets(s, M, y + Inches(2.2), Inches(8.4), [
        [("取指单元一次最多只能从一个 Cache 块里取指令", 15, False, INK)],
        [("块 = 16B 时，每约 4 条指令就要重新访问一次 I-Cache，每次停约 2 周期",
          15, False, INK)],
        [("停顿 3,319,880 周期 = 总周期的 66.6%；减掉它就回到 32B 的量级",
          15, False, INK)],
    ], gap=Inches(0.52), marker=(INK_SOFT, INK_SOFT, RED))

    T.note(s, M, y + Inches(3.80), Inches(8.4),
           "MLP 掉到 2.99 是结果不是原因：核被取指饿死了。",
           color=RED, fill=RED_DIM, size=13.5, icon="★")

    T.card(s, Inches(9.45), y - Inches(0.05), Inches(3.15), Inches(4.35))
    T.txt(s, Inches(9.78), y + Inches(0.32), Inches(2.5), Inches(3.7),
          [[("我们在调的是", 15, True, INK)],
           [("数据 Cache", 22, True, INK)],
           [("的块大小", 15, True, INK)],
           [("", 8, False, INK)],
           [("崩塌却发生在", 15, True, INK)],
           [("取指通路", 22, True, RED)],
           [("", 10, False, INK)],
           [("cacheline 同时作用于", 13, False, INK_SOFT, True)],
           [("L1I、L1D、L2 和取指缓冲。", 13, False, INK_SOFT)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 28 punch
    T.punch(prs,
            [("一个「局部」的设计参数，", False),
             ("它的影响不一定局限在局部。", True),
             ("只在数据通路里找原因，", False),
             ("你永远找不到。", True)],
            sub="这就是本课程坚持让你看完整 stats.txt、而不只是 CSV 里那几列的理由。",
            accent=ACC)

    # ======================================================== 29 §05 节间
    T.section(prs, "05", "两个不值得投资的维度",
              "任务 4、5　·　十个配置点，换来「不必做哪些实验」的知识",
              accent=ACC)

    # ======================================================== 30 MSHR
    s = T.blank(prs)
    y = T.head(s, "失效率不是程序的属性",
               kicker="任务 4　问题 1、2　★", accent=ACC)
    T.table(s, M, y, Inches(7.5), [
        ["MSHR 数", "周期数", "l1d_miss_rate", "mshr_mpki", "MLP"],
        ["1", "1,114,224", "0.78%", "2.210", "1.00"],
        ["2", "1,099,928", "12.20%", "2.210", "15.59"],
        ["4", "1,099,658", "12.20%", "2.210", "15.60"],
        ["8", "1,099,658", "12.20%", "2.210", "15.60"],
        ["16", "1,099,658", "12.20%", "2.210", "15.60"],
    ], col_w=[1.5, 1.9, 2.0, 1.7, 1.2], size=13.5, head_size=11.5,
        row_h=Inches(0.44), mono_cols=(0, 1, 2, 3, 4), hi_rows=(1, 2))

    T.txt(s, M, y + Inches(2.82), Inches(7.5), Inches(1.4),
          [[("miss_rate 跳了 ", 15.5, False, INK),
            ("15.6 倍", 15.5, True, RED),
            ("，mshr_mpki 恒为 2.210 一点没变。", 15.5, False, INK)],
           [("MSHR=1 时次级失效被阻塞而不是被记账 —— 统计口径变了而已。",
             15, False, INK_SOFT)],
           [("4 个 MSHR 服务了 60 多个访问，所以 MLP 15.6 和 MSHR 4 并不矛盾。",
             15, False, INK_SOFT)]], spacing=1.45)

    T.card(s, Inches(8.65), y - Inches(0.05), Inches(3.95), Inches(4.42))
    T.txt(s, Inches(9.0), y + Inches(0.32), Inches(3.3), Inches(3.8),
          [[("程序没变，数据没变，", 15, True, INK)],
           [("Cache 配置也没变。", 15, True, INK)],
           [("", 8, False, INK)],
           [("只把一个队列", 15, False, INK)],
           [("从 1 加深到 2，", 15, False, INK)],
           [("「失效率」变了", 15, False, INK)],
           [("15 倍", 34, True, RED)],
           [("", 8, False, INK)],
           [("所以它是微体系结构的产物，", 13.5, False, INK_SOFT)],
           [("不是程序的属性。", 13.5, True, ACC)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 31 L2
    s = T.blank(prs)
    y = T.head(s, "在 DRAM 流量为零的负载上优化 L2",
               kicker="任务 5　钱该花在哪一级", accent=ACC)
    T.table(s, M, y, Inches(7.7), [
        ["L2 容量", "周期数", "IPC", "l2_miss_rate", "dram_bytes"],
        ["128kB", "1,075,328", "5.395", "0.29%", "3,328"],
        ["256kB（基线）", "1,099,658", "5.276", "0.19%", "1,472"],
        ["512kB", "1,124,600", "5.159", "0.19%", "1,472"],
        ["1MB", "1,150,161", "5.044", "0.19%", "1,472"],
        ["2MB", "1,175,289", "4.936", "0.19%", "1,472"],
    ], col_w=[2.0, 1.9, 1.2, 1.9, 1.6], size=13.5, head_size=11.5,
        row_h=Inches(0.44), mono_cols=(1, 2, 3, 4), hi_rows=(1,))

    T.txt(s, M, y + Inches(2.82), Inches(7.7), Inches(0.9),
          [[("dram_bytes = 1,472 —— 单位是", 15.5, False, INK),
            ("字节", 15.5, True, RED),
            ("，不是 KB，不是 MB。", 15.5, False, INK)],
           [("ROI 里 L1D 访问了 164 万次，和主存交换的只有一千多字节。",
             15, False, INK_SOFT)]], spacing=1.45)

    T.note(s, M, y + Inches(3.80), Inches(7.7),
           "性能优化的第一步不是「哪里能改进」，是「哪里是瓶颈」。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.card(s, Inches(8.85), y - Inches(0.05), Inches(3.75), Inches(4.42))
    T.txt(s, Inches(9.2), y + Inches(0.3), Inches(3.1), Inches(1.0),
          [[("同样的面积", 17, True, INK)],
           [("两个方向", 17, True, INK)]], spacing=1.3)
    T.stat(s, Inches(9.2), y + Inches(1.24), Inches(3.1), "+23.3%",
           "L1D 32kB → 128kB", color=GREEN, size=40)
    T.stat(s, Inches(9.2), y + Inches(2.62), Inches(3.1), "−9.3%",
           "L2 128kB → 2MB", color=RED, size=40)
    T.txt(s, Inches(9.2), y + Inches(3.72), Inches(3.1), Inches(0.4),
          [("架构师会把 L2 的面积挪给 L1D。", 13, True, INK)], spacing=1.25)
    T.foot(s, FOOT)

    # ======================================================== 32 §06 节间
    T.section(prs, "06", "拿出你的配置提案",
              "任务 6　·　四个维度，每个都要回答「为什么不是另外那个」",
              accent=ACC)

    # ======================================================== 33 提案
    s = T.blank(prs)
    y = T.head(s, "一个可行解（不是唯一解）",
               kicker="任务 6　参考提案", accent=ACC)

    T.code(s, M, y + Inches(0.06), Inches(8.2), [
        "--l1d-size 128kB  --l1d-assoc 4",
        "--cacheline 256   --l2-size 128kB",
    ], size=15, hi=(0, 1))

    T.txt(s, Inches(9.25), y, Inches(3.35), Inches(0.6),
          [[("1.234×", 34, True, GREEN, True)]])
    T.txt(s, Inches(9.25), y + Inches(0.6), Inches(3.35), Inches(0.6),
          [[("实测 891,409 周期", 14, True, INK)],
           [("相对基线 1,099,658", 12.5, False, INK_SOFT)]], spacing=1.3)

    T.table(s, M, y + Inches(1.34), CONTENT_W, [
        ["维度", "取值", "为什么不选别的"],
        ["l1d-size", "128kB",
         "唯一能装下 100.7KB 的最小容量；64kB 无收益纯付延迟，256kB 只剩延迟"],
        ["l1d-assoc", "4 路",
         "128kB 下 1/2/4/8 路完全相同；选 4 路是为别的负载留鲁棒性，代价为 0"],
        ["cacheline", "256B",
         "qnn 空间局部性 100%，块越大越好 —— 但这是负载相关的选择"],
        ["l2-size", "128kB",
         "L2 失效率 0.19%、DRAM 流量 1.5KB，基本闲置，取最小值省延迟和面积"],
    ], col_w=[1.7, 1.3, 8.8], size=13.5, head_size=12.5,
        row_h=Inches(0.60), mono_cols=(0,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])
    T.foot(s, FOOT)

    # ======================================================== 34 不能相乘
    s = T.blank(prs)
    y = T.head(s, "收益为什么不能相乘",
               kicker="任务 6　问题 2　★考点", accent=ACC)

    T.txt(s, M, y, Inches(8.4), Inches(0.5),
          [[("1,099,658", 17, True, INK, True),
            ("  ×  0.811  ×  0.874  ×  0.978  =  ", 17, False, INK_SOFT),
            ("762,500", 17, True, RED, True)]])
    T.txt(s, M, y + Inches(0.46), Inches(8.4), Inches(0.4),
          [[("                   128kB L1D    256B 块    128kB L2      外推预测",
             12, False, INK_SOFT)]])

    T.txt(s, M, y + Inches(1.12), Inches(8.4), Inches(0.5),
          [[("实测：", 17, False, INK), ("891,409", 17, True, GREEN, True),
            ("　　外推值比实测", 17, False, INK),
            ("乐观了 14.5%", 17, True, RED), ("。", 17, False, INK)]])

    T.bullets(s, M, y + Inches(1.92), Inches(8.4), [
        [("三项收益作用在", 15.5, False, INK),
         ("同一批失效", 15.5, True, RED), ("上", 15.5, False, INK)],
        [("128kB 的 L1D 已经把 mshr_mpki 从 2.210 打到 0.002 —— 失效基本消失了",
          15.5, False, INK)],
        [("此时「块更大能减少一半事务」没有对象可以作用，自然兑现不了",
          15.5, False, INK)],
    ], gap=Inches(0.56), marker=(RED, INK_SOFT, INK_SOFT))

    T.note(s, M, y + Inches(3.72), Inches(8.4),
           "收益不能相乘，因为它们在抢同一个瓶颈。",
           color=RED, fill=RED_DIM, size=15, icon="★")

    T.card(s, Inches(9.45), y + Inches(1.12), Inches(3.15), Inches(3.2))
    T.txt(s, Inches(9.78), y + Inches(1.44), Inches(2.5), Inches(2.6),
          [[("助教查作业时", 15, True, INK)],
           [("", 8, False, INK)],
           [("学生报的实测值", 14, False, INK)],
           [("如果恰好等于外推值，", 14, False, INK)],
           [("", 8, False, INK)],
           [("八成是没跑，", 15, True, RED)],
           [("直接查他的 CSV。", 15, True, RED)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 35 换负载
    s = T.blank(prs)
    y = T.head(s, "换个负载，一半的结论就翻了",
               kicker="任务 6　问题 3　·　pchase", accent=ACC)
    T.table(s, M, y, Inches(8.0), [
        ["pchase 配置", "周期数", "IPC", "mshr_mpki", "MLP"],
        ["32kB / 64B", "4,522,374", "0.265", "147.0", "1.00"],
        ["32kB / 256B", "4,679,105", "0.257", "146.1", "1.00"],
        ["128kB / 64B", "3,857,427", "0.311", "86.0", "1.00"],
        ["128kB / 256B", "3,728,458", "0.322", "83.8", "1.00"],
    ], col_w=[2.2, 1.9, 1.2, 1.6, 1.1], size=13.5, head_size=12,
        row_h=Inches(0.46), mono_cols=(1, 2, 3, 4))

    T.txt(s, M, y + Inches(2.5), Inches(8.0), Inches(0.9),
          [[("容量的结论", 15.5, True, GREEN), ("成立：128kB 仍然快 17%。",
                                                15.5, False, INK)],
           [("块大小的结论", 15.5, True, RED),
            ("翻转：32kB 下 256B 块反而慢 3.5%。", 15.5, False, INK)]],
          spacing=1.45)

    T.txt(s, M, y + Inches(3.62), Inches(8.0), Inches(0.6),
          [[("pchase 的 MLP = 1.00：下一个地址存在这次访存的返回值里，",
             14.5, False, INK_SOFT)],
           [("串行依赖链，乱序核再宽也并行不了。受", 14.5, False, INK_SOFT),
            ("延迟", 14.5, True, INK), ("限制，不是受", 14.5, False, INK_SOFT),
            ("带宽", 14.5, True, INK), ("限制。", 14.5, False, INK_SOFT)]],
          spacing=1.4)

    T.card(s, Inches(9.05), y - Inches(0.05), Inches(3.55), Inches(4.42))
    T.txt(s, Inches(9.4), y + Inches(0.32), Inches(2.9), Inches(3.8),
          [[("「最优配置」", 17, True, INK)],
           [("是负载的函数", 24, True, ACC)],
           [("不是芯片的属性", 17, True, INK)],
           [("", 8, False, INK)],
           [("通用处理器只能在一整套", 14, False, INK)],
           [("基准上取折中 —— 这就是", 14, False, INK)],
           [("SPEC 存在的理由。", 14, False, INK)],
           [("", 8, False, INK)],
           [("而领域专用加速器可以", 14, False, INK)],
           [("这样「过拟合」地优化。", 14, True, ACC)],
           [("第 6 次实验见。", 13.5, False, INK_SOFT)]], spacing=1.28)
    T.foot(s, FOOT)

    # ======================================================== 36 交付
    s = T.blank(prs)
    y = T.head(s, "交什么，怎么判", kicker="提交要求", accent=ACC)

    cw, gapx = Inches(3.72), Inches(0.29)
    for k, (big, cap, body, col) in enumerate([
        ("6 表", "任务 1~6 全部数据",
         [("三张图：容量曲线（开/关）、", 14, False, INK),
          ("相联度 × 替换策略、块大小。", 14, False, INK),
          ("结论必须指向你自己的数据。", 14, True, ACC)], ACC),
        ("400 字", "配置提案",
         [("四个维度的取值、加速比、", 14, False, INK),
          ("以及每个维度", 14, False, INK),
          ("「为什么不选别的」。", 14, True, ACC)], ACC),
        ("45 / 15", "机制分析 / 方法学",
         [("任务 2 和任务 3 的分析", 14, False, INK),
          ("占了机制分析的一多半。", 14, False, INK),
          ("按分析质量给分，不按跑通。", 14, True, RED)], RED),
    ]):
        x = M + (cw + gapx) * k
        T.card(s, x, y, cw, Inches(3.55))
        T.txt(s, x + Inches(0.38), y + Inches(0.34), cw - Inches(0.76),
              Inches(0.6), [(big, 34, True, col)])
        T.txt(s, x + Inches(0.38), y + Inches(0.98), cw - Inches(0.76),
              Inches(0.34), [(cap, 15, True, INK)])
        T.txt(s, x + Inches(0.38), y + Inches(1.62), cw - Inches(0.76),
              Inches(1.6), [[r] for r in body], spacing=1.42)

    T.note(s, M, y + Inches(3.76), CONTENT_W,
           "小于 0.1% 的差异一律当作「没有差异」，不许解释。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 37 一页纸
    s = T.blank(prs, dark=True)
    y = T.head(s, "这一次的一页纸", kicker="带走这六条", dark=True, accent=ACC)

    rows = [
        ("容量的收益是阶跃的", "装下之前严格为零，装下那一刻全部兑现"),
        ("失效率不是程序的属性", "只动一个队列深度，它就变 15 倍；看 mshr_mpki"),
        ("课本有前提", "3C 模型假设替换策略合理；LRU 在扫描下反向失效"),
        ("局部参数的影响不局限在局部", "调数据 Cache 的块，崩塌发生在取指通路"),
        ("收益不能相乘", "三项优化在抢同一个瓶颈，外推会乐观 14.5%"),
        ("最优配置是负载的函数", "不是芯片的属性 —— 这是加速器存在的理由"),
    ]
    for k, (t, d) in enumerate(rows):
        yy = y + Inches(0.72) * k
        T.rect(s, M, yy + Inches(0.14), Inches(0.13), Inches(0.13), ACC)
        T.txt(s, M + Inches(0.38), yy, Inches(4.5), Inches(0.4),
              [(t, 16.5, True, PAPER)])
        T.txt(s, M + Inches(5.1), yy + Inches(0.03), Inches(6.7), Inches(0.4),
              [(d, 14, False, WHITE_DIM)])

    T.txt(s, M, SLIDE_H - Inches(1.0), CONTENT_W, Inches(0.4),
          [("下一次：改 gem5 的源码，把替换策略自己写一个出来。",
            14, False, WHITE_DIM)])

    return prs


if __name__ == "__main__":
    prs = build()
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    print("wrote %s  (%d slides)" % (out, len(prs.slides._sldIdLst)))
