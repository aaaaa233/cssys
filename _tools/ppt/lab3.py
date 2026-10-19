# -*- coding: utf-8 -*-
"""实验三《修改 gem5：替换策略与预取器》讲课用 PPT。

    python _tools/ppt/lab3.py            → labs/lab3/幻灯片.pptx

所有数字来自 labs/lab3/参考解答.md，改数据请同步改那一处。
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
                   "..", "..", "labs", "lab3", "幻灯片.pptx")

ACC = T.LAB_ACCENT[3]          # 紫
FOOT = "实验三　修改 gem5：替换策略与预取器"


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
    T.cover(prs, 3,
            "修改 gem5：\n替换策略与预取器",
            "核心问题：自己实现的替换策略，值不值这些复杂度\n"
            "十五个策略在 L1 一个都不管用；原样搬到 L2，排名彻底反转",
            "计算机系统综合设计实验　·　4 学时　·　本次要动 gem5 源码")

    # ======================================================== 01 立题
    T.punch(prs,
            [("换一个替换策略，", False),
             ("面积开销是零。", True),
             ("可是教科书上那十五个，", False),
             ("在 L1 一个都不管用。", True)],
            sub="这不是它们写错了 —— 是 L1 这个位置，不给它们发挥的机会。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "今天要你做出的决策", kicker="任务", accent=ACC)
    T.txt(s, M, y, Inches(8.4), Inches(1.3),
          [[("实验二你的结论多半是「把 L1D 加到 128kB」。", 22, False, INK)],
           [("现在问：同样的性能，", 22, False, INK),
            ("能不能不花这 96 KB", 22, True, ACC),
            ("？", 22, False, INK)]], spacing=1.35)

    cw = (CONTENT_W - Inches(0.4)) / 2
    T.card(s, M, y + Inches(1.58), cw, Inches(1.98))
    T.txt(s, M + Inches(0.34), y + Inches(1.82), cw - Inches(0.68),
          Inches(1.5),
          [[("换替换策略", 20, True, ACC)],
           [("只改控制逻辑，", 15, False, INK),
            ("面积开销为零", 15, True, GREEN),
            ("。", 15, False, INK)],
           [("任务 1～3，要动 gem5 源码。", 15, False, INK_SOFT)]],
          spacing=1.42)

    T.card(s, M + cw + Inches(0.4), y + Inches(1.58), cw, Inches(1.98))
    T.txt(s, M + cw + Inches(0.74), y + Inches(1.82), cw - Inches(0.68),
          Inches(1.5),
          [[("加预取器", 20, True, ACC)],
           [("面积很小，", 15, False, INK),
            ("代价是带宽和功耗", 15, True, RED),
            ("。", 15, False, INK)],
           [("任务 4～6，只改配置。", 15, False, INK_SOFT)]],
          spacing=1.42)

    T.note(s, M, y + Inches(3.76), CONTENT_W,
           "两条路都不加容量。交付物是：它们各自省下了什么。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 03 先算一个数
    s = T.blank(prs)
    y = T.head(s, "先算一个数", kicker="它决定了今天全部的结果", accent=ACC)

    T.table(s, M, y, Inches(7.5), [
        ["量", "算式", "值"],
        ["权重 w1", "128 × 784 int8", "100,352 B"],
        ["折成块", "÷ 64 B", "1,568 块"],
        ["L1D 64kB", "64 KB ÷ 64 B", "1,024 块"],
        ["组数", "1024 ÷ 4 路", "256 组"],
        ["每组要挤进来 N", "1568 ÷ 256", "6.125"],
    ], col_w=[2.5, 2.6, 2.4], size=13.5, head_size=12.5,
        row_h=Inches(0.46), mono_cols=(1, 2), hi_rows=(5,), hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(8.9), y + Inches(0.16), Inches(3.9), "6.125 > 4",
           "每组要挤进来的块数 ＞ 每组的位置数", color=ACC, size=40,
           sub="这就是 LRU 病态的全部前提。\n没有它，什么策略都一样。")

    T.txt(s, M, y + Inches(3.06), Inches(7.5), Inches(0.5),
          [[("循环扫描 ", 16, False, INK),
            ("N > A", 16, True, RED, True),
            (" 个块 —— LRU 的命中率恰好是 ", 16, False, INK),
            ("0", 16, True, RED, True),
            ("。", 16, False, INK)]])

    T.note(s, M, y + Inches(3.68), CONTENT_W,
           "不是「比较低」，是零。一次都不中。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 04 §01
    T.section(prs, "01", "病理学",
              "为什么 LRU 会在这个负载上输给「随机」", accent=ACC)

    # ======================================================== 05 循环扫描病态
    s = T.blank(prs)
    y = T.head(s, "循环扫描下的四条理论线", kicker="病理学", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("反复扫描 N 个块，每组只有 A 个位置。这时候命中率完全可以手算：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.62), CONTENT_W, [
        ["策略", "命中率", "为什么"],
        ["LRU", "0", "刚踢掉的那一块，正好是下一圈第一个要用的"],
        ["FIFO", "0", "顺序扫描时与 LRU 等价，同样系统性踢错"],
        ["MRU", "(A−1)/N", "只反复牺牲一个位置，另外 A−1 个稳定留住"],
        ["Random", "0 ～ A/N", "没有规律，也就没有系统性地反向"],
        ["OPT（上界）", "A/N", "留下最晚才会用到的，任何策略都超不过"],
    ], col_w=[1.9, 1.5, 8.4], size=13.5, head_size=12.5,
        row_h=Inches(0.48), mono_cols=(1,), hi_rows=(1,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.LEFT])

    T.note(s, M, y + Inches(3.66), CONTENT_W,
           "LRU 输给 Random，是这一页唯一要你记住的事。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 06 qnn 就是它
    s = T.blank(prs)
    y = T.head(s, "qnn 恰好就是这个循环", kicker="病理学", accent=ACC)

    T.code(s, M, y, Inches(7.4), [
        "for (p = 0; p < 8; p++)          /* 8 遍 */",
        "  for (o = 0; o < 128; o++)",
        "    for (i = 0; i < 784; i++)",
        "      acc += w1[o][i] * x[i];    /* 顺序扫全表 */",
    ], size=13.5)

    T.txt(s, M, y + Inches(1.78), Inches(7.4), Inches(1.0),
          [[("w1 一整张表 98 KB，从头到尾顺序读，读完再从头来 —— ",
             15.5, False, INK),
            ("一共 8 遍。这就是教科书里那个反例本身。",
             15.5, True, INK)]], spacing=1.45)

    T.stat(s, Inches(8.9), y + Inches(0.04), Inches(3.9), "1,568",
           "w1 折成 64 B 的块", color=ACC, size=46)
    T.stat(s, Inches(8.9), y + Inches(1.34), Inches(3.9), "1,024",
           "L1D 64kB 一共只有", color=RED, size=46,
           sub="每扫完一遍，一块都没剩下。")

    T.note(s, M, y + Inches(3.44), CONTENT_W,
           "工作集比容量大 53%，就足以让命中率归零。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 07 与相联度无关
    s = T.blank(prs)
    y = T.head(s, "加相联度救不了它", kicker="病理学", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.5),
          [[("N / A ＝（工作集 ÷ 块大小 ÷ 组数）÷ A ＝ ",
             17, False, INK),
            ("工作集 ÷ 容量", 17, True, ACC),
            ("　—— 相联度被约掉了。", 17, False, INK)]])

    T.table(s, M, y + Inches(0.7), Inches(9.4), [
        ["相联度 A", "组数", "每组 N", "N / A", "实测周期数"],
        ["2 路", "512", "3.06", "1.53", "1,137,187"],
        ["4 路", "256", "6.13", "1.53", "1,137,187"],
        ["8 路", "128", "12.25", "1.53", "1,137,187"],
        ["16 路", "64", "24.50", "1.53", "1,137,187"],
    ], col_w=[1.8, 1.5, 1.7, 1.6, 2.8], size=13.5, head_size=12.5,
        row_h=Inches(0.46), mono_cols=(1, 2, 3, 4),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.txt(s, Inches(10.30), y + Inches(0.9), Inches(2.28), Inches(2.0),
          [[("四行", 30, True, ACC)],
           [("最后一列", 15, False, INK)],
           [("逐位相同", 15, True, RED)],
           [("不是「接近」，", 13, False, INK_SOFT)],
           [("是同一个数。", 13, False, INK_SOFT)]], spacing=1.35)

    T.note(s, M, y + Inches(3.16), CONTENT_W,
           "面积翻四倍，性能一位不差。这是一条硬信息。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 08 punch
    T.punch(prs,
            [("相联度从 2 路加到 16 路，", False),
             ("周期数逐位相同。", True),
             ("能省的面积，先在这里就省下了。", False)],
            sub="任务 1 要你先手算这四行，再去跑 —— 算错了比跑错了值钱。",
            accent=ACC)

    # ======================================================== 09 §02
    T.section(prs, "02", "十五个策略，跑一遍",
              "有效的三个，和无效的十二个", accent=ACC)

    # ======================================================== 10 L1D 结果表
    s = T.blank(prs)
    y = T.head(s, "L1D 64kB / 4 路，十五个策略", kicker="任务 1", accent=ACC)

    T.table(s, M, y, Inches(8.5), [
        ["替换策略", "类", "l1d MSHR 失效", "vs LRU"],
        ["lru（基准）", "甲", "12,808", "—"],
        ["lfu", "甲", "6,953", "−45.7%"],
        ["mru", "甲", "7,678", "−40.1%"],
        ["random", "甲", "8,638", "−32.6%"],
        ["treeplru", "甲", "12,689", "−0.9%"],
        ["fifo / secondchance", "甲", "12,979 / 12,835", "+1.3% / +0.2%"],
        ["lip / bip / rrip / brrip", "乙", "12,781 ～ 12,816", "±0.2%"],
        ["nru / drrip / ship / ship_pc", "乙", "12,778 ～ 12,788", "±0.2%"],
    ], col_w=[3.3, 0.8, 2.4, 2.0], size=13, head_size=12.5,
        row_h=Inches(0.40), mono_cols=(2, 3), hi_rows=(2, 3, 4),
        hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.34), Inches(3.13), "3 / 15",
           "真正有效的策略数", color=ACC, size=44,
           sub="其余十二个，包括全部\n八个「插入位置型」，\n一个不剩。")

    T.note(s, M, y + Inches(3.72), CONTENT_W,
           "换一个替换策略，MSHR 失效少 45.7% —— 面积开销为零。",
           color=GREEN, fill=GREEN_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 11 甲乙分类
    s = T.blank(prs)
    y = T.head(s, "十五个策略，其实只有两类", kicker="分类学", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("一块新数据装进 Cache，只有两个旋钮可以拧：",
             16.5, False, INK)]])

    cw = (CONTENT_W - Inches(0.44)) / 2
    yc = y + Inches(0.66)
    T.card(s, M, yc, cw, Inches(2.46))
    T.txt(s, M + Inches(0.34), yc + Inches(0.26), cw - Inches(0.68),
          Inches(1.9),
          [[("甲　牺牲者选择型", 20, True, GREEN)],
           [("满了以后，踢谁？", 15, False, INK)],
           [("LRU　FIFO　Random　MRU", 14, True, INK, True)],
           [("LFU　TreePLRU　SecondChance", 14, True, INK, True)],
           [("经典教材的主线，1960 年代至今。", 13.5, False, INK_SOFT)]],
          spacing=1.44)

    T.card(s, M + cw + Inches(0.44), yc, cw, Inches(2.46))
    T.txt(s, M + cw + Inches(0.78), yc + Inches(0.26), cw - Inches(0.68),
          Inches(1.9),
          [[("乙　插入位置型", 20, True, RED)],
           [("刚进来，放在什么优先级上？", 15, False, INK)],
           [("LIP　BIP　SRRIP　BRRIP", 14, True, INK, True)],
           [("DRRIP　SHiP　SHiP-PC　NRU", 14, True, INK, True)],
           [("2007–2011 顶会主线，全部无效。", 13.5, False, INK_SOFT)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.36), CONTENT_W,
           "有效的三个全在甲类。这不是巧合，是结构性的。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 12 punch
    T.punch(prs,
            [("2007 到 2011，顶会上的八个策略，", False),
             ("在这里一个都没用。", True),
             ("这是个需要解释的现象，不是失败。", False)],
            sub="任务 3 的全部工作，就是把这个现象解释清楚 —— 占 30 分。",
            accent=ACC)

    # ======================================================== 13 预测 vs 实测
    s = T.blank(prs)
    y = T.head(s, "先预测，再开机", kicker="任务 1a／1b", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["要预测的量", "手算依据", "预测值", "实测值", "对不对"],
        ["LRU 的 MSHR 失效", "8 遍 × 1,568 块", "12,544", "12,808", "偏 2.1%"],
        ["MRU 的命中率", "(A−1)/N = 3/6.125", "49.0%", "46.7%", "偏 2.3pt"],
        ["相联度 2→16 的影响", "N/A 与 A 无关", "无变化", "逐位相同", "完全命中"],
    ], col_w=[3.0, 2.9, 1.8, 1.8, 2.0], size=13.5, head_size=12.5,
        row_h=Inches(0.50), mono_cols=(2, 3),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.CENTER])

    T.txt(s, M, y + Inches(2.24), Inches(11.8), Inches(1.0),
          [[("多出来的 264 次不是噪声：xbuf、hbuf、b1 和栈也在争这个 Cache。",
             16, False, INK)],
           [("能把 264 解释掉，比把 12,544 算对更能说明你懂了。",
             16, True, ACC)]], spacing=1.42)

    T.note(s, M, y + Inches(3.46), CONTENT_W,
           "预测错了不扣分，不预测才扣分。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 14 OPT 兑现
    s = T.blank(prs)
    y = T.head(s, "离最优还差多远", kicker="Belady OPT 是天花板", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("OPT 的命中率 = A/N。把每个策略拿到的收益，除以 OPT 的收益：",
             16, False, INK)]])

    hbars(s, M, y + Inches(0.62), Inches(10.4), [
        ("lfu", 81.7, GREEN, "81.7%"),
        ("mru", 71.6, GREEN, "71.6%"),
        ("random", 58.2, GREEN, "58.2%"),
        ("treeplru", 1.7, INK_SOFT, "1.7%"),
        ("其余 12 个", 0.4, RED, "≈ 0%"),
    ], bar_h=Inches(0.38), gap=Inches(0.20), label_w=Inches(1.7),
        val_w=Inches(1.4), maxv=100.0, label_size=14, value_size=13)

    T.txt(s, M, y + Inches(3.46), Inches(11.8), Inches(0.5),
          [[("lfu 拿走了理论收益的 ", 16, False, INK),
            ("八成", 16, True, GREEN),
            ("；十二个策略连 1% 都没拿到。", 16, False, INK)]])
    T.foot(s, FOOT)

    # ======================================================== 15 MRU 的偏差
    s = T.blank(prs)
    y = T.head(s, "MRU 在 16 路上反而变差", kicker="理论会在哪里失灵",
               accent=ACC)

    T.table(s, M, y, Inches(8.2), [
        ["相联度 A", "理论 (A−1)/N", "实测 MSHR 失效", "偏差"],
        ["2 路", "9,224", "9,128", "−1.0%"],
        ["4 路", "7,432", "7,678", "+3.3%"],
        ["8 路", "6,536", "7,499", "+14.7%"],
        ["16 路", "6,088", "8,244", "+35.4%"],
    ], col_w=[1.8, 2.2, 2.4, 1.8], size=13.5, head_size=12.5,
        row_h=Inches(0.46), mono_cols=(1, 2, 3), hi_rows=(4,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.txt(s, Inches(9.1), y + Inches(0.2), Inches(3.7), Inches(2.4),
          [[("理论说：路数越多越好。", 15.5, False, INK)],
           [("实测说：8 路最好，", 15.5, True, INK)],
           [("16 路掉回去。", 15.5, True, RED)],
           [("MRU 只保护 A−1 个位置。", 13.5, False, INK_SOFT)],
           [("路数一多，被牺牲的那一路就扫得更频繁。",
             13.5, False, INK_SOFT)]],
          spacing=1.42)

    T.note(s, M, y + Inches(2.60), CONTENT_W,
           "公式只在自己的适用区间里成立。找到边界，比背下公式值钱。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 16 对照组
    s = T.blank(prs)
    y = T.head(s, "对照组：把病治好以后", kicker="任务 1c　诚信底线",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("把 L1D 换成 128kB / 4 路 —— 工作集装得下了，病态消失。"
             "同样十五个策略再跑一遍：", 15.5, False, INK)]])

    T.table(s, M, y + Inches(0.62), CONTENT_W, [
        ["策略", "周期数", "l1d 失效", "MSHR 失效", "vs LRU", "结论"],
        ["lru", "891,719", "209", "14", "—", "基准"],
        ["bip", "891,719", "209", "14", "±0", "完全一样"],
        ["random", "894,599", "1,398", "92", "+557%", "看着还好，其实已经坏了"],
        ["mru", "908,990", "10,238", "677", "+4736%", "从冠军变成灾难"],
    ], col_w=[1.3, 1.7, 1.4, 1.5, 1.5, 4.4], size=13, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(1, 2, 3, 4), hi_rows=(4,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(3.02), Inches(11.8), Inches(0.5),
          [[("random 的周期数只差 0.3%，", 16, False, INK),
            ("如果只看周期数，你会以为它没问题。", 16, True, RED)]])

    T.note(s, M, y + Inches(3.66), CONTENT_W,
           "任务 1c 缺席，任务 1 整体判 0 分。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 17 punch
    T.punch(prs,
            [("「MRU 比 LRU 好」不是结论。", False),
             ("「MRU 只在病态下比 LRU 好，", False),
             ("病一好它就烂得离谱」", True),
             ("才是结论。", True)],
            sub="差别在于：后者说明你知道自己的结论在什么条件下会失效。",
            accent=ACC)

    # ======================================================== 18 §03
    T.section(prs, "03", "动手改 gem5",
              "复制一个文件，注册一个 SimObject，改一个字符", accent=ACC)

    # ======================================================== 19 接口
    s = T.blank(prs)
    y = T.head(s, "替换策略只有五个函数", kicker="任务 2", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["函数", "什么时候被调用", "你在这里能做什么"],
        ["instantiateEntry()", "建 Cache 时", "给每个块分配你自己的元数据"],
        ["reset(data)", "块刚被装进来", "设初始优先级 —— 乙类只能改这里"],
        ["touch(data)", "块被命中", "更新优先级 —— 甲类主要改这里"],
        ["getVictim(cands)", "要踢人了", "从候选里挑一个 —— 甲类的核心"],
        ["invalidate(data)", "块被作废", "把它标成最该被踢的"],
    ], col_w=[2.9, 2.5, 6.4], size=13.5, head_size=12.5,
        row_h=Inches(0.46), mono_cols=(0,), hi_rows=(2, 3),
        hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(3.02), Inches(11.8), Inches(0.5),
          [[("gem5 里 LRU 的完整实现不到 40 行 —— ", 16, False, INK),
            ("整个接口就这么大。", 16, True, INK)]])

    T.note(s, M, y + Inches(3.70), CONTENT_W,
           "乙类只能改 reset()。记住这一点，任务 3 就破了。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 20 一个字符
    s = T.blank(prs)
    y = T.head(s, "把 < 改成 >，LRU 就变成了 MRU", kicker="任务 2b",
               accent=ACC)

    T.code(s, M, y, Inches(7.7), [
        "// LRU 的 getVictim：挑最久没被碰过的那一块",
        "if (candidate->lastTouchTick < victim->lastTouchTick)",
        "    victim = candidate;",
        "",
        "// MRU：挑刚刚才被碰过的那一块",
        "if (candidate->lastTouchTick > victim->lastTouchTick)",
        "    victim = candidate;",
    ], size=13, hi=(5,))

    T.txt(s, M, y + Inches(2.62), Inches(7.7), Inches(0.9),
          [[("整个策略的全部改动，就是这一个字符。", 16, True, INK)],
           [("重编译 2 分 54 秒，重编 1 个文件。", 15, False, INK_SOFT)]],
          spacing=1.42)

    T.stat(s, Inches(9.2), y + Inches(0.34), Inches(3.6), "1",
           "个字符的改动", color=ACC, size=96,
           sub="L1D MSHR 失效\n12,808 → 7,678\n降 40.1%")

    T.note(s, M, y + Inches(3.72), CONTENT_W,
           "改一个字符，MSHR 失效降 40.1%。这就是「零面积」。",
           color=GREEN, fill=GREEN_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 21 注册三处
    s = T.blank(prs)
    y = T.head(s, "加一个 SimObject，要动三处", kicker="任务 2a", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("三处缺一处，gem5 就编不过 —— 而报错信息通常指不到真正的地方。",
             16, False, INK)]])

    cw = (CONTENT_W - Inches(0.8)) / 3
    yc = y + Inches(0.68)
    for k, (no, ttl, path, desc) in enumerate([
        ("1", "复制", "cssys_rp.hh / .cc",
         "照着 lru_rp 抄一份，改类名和构造函数名。"),
        ("2", "声明", "ReplacementPolicies.py",
         "注册 SimObject，把可调参数写成 Param。"),
        ("3", "编译", "SConscript",
         "把新的 .cc 加进去，否则永远链接不到。"),
    ]):
        xx = M + (cw + Inches(0.4)) * k
        T.card(s, xx, yc, cw, Inches(2.30))
        T.txt(s, xx + Inches(0.3), yc + Inches(0.22), cw - Inches(0.6),
              Inches(1.8),
              [[(no, 26, True, ACC, True), ("　" + ttl, 19, True, INK)],
               [(path, 13.5, True, ACC, True)],
               [(desc, 14, False, INK)]], spacing=1.40)

    T.note(s, M, y + Inches(3.26), CONTENT_W,
           "首次注册新 SimObject：5 分 22 秒，153 个文件。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 22 编译时间
    s = T.blank(prs)
    y = T.head(s, "编译时间要计入你的实验计划", kicker="现实", accent=ACC)

    T.table(s, M, y, Inches(8.4), [
        ["你改了什么", "重编文件数", "实测耗时"],
        ["首次注册新 SimObject", "153", "5 分 22 秒"],
        ["只改一个 .cc 的函数体", "1", "2 分 54 秒"],
        ["改 Python 里的参数声明", "≈150", "约 5 分"],
        ["本次实验全程（4 次编译）", "—", "约 17 分"],
    ], col_w=[4.2, 2.0, 2.2], size=13.5, head_size=12.5,
        row_h=Inches(0.48), mono_cols=(1, 2), hi_rows=(2,),
        hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.4), y + Inches(0.3), Inches(3.4), "2:54",
           "改一个字符的代价", color=RED, size=52,
           sub="改一次编译一次，\n一上午只够改六次。\n所以先想清楚再动手。")

    T.txt(s, M, y + Inches(2.66), Inches(8.4), Inches(0.5),
          [[("链接一个 888 MB 的 gem5.opt 是单线程的。", 15.5, False, INK)]])

    T.note(s, M, y + Inches(3.34), CONTENT_W,
           "-j8 对增量编译几乎无效：链接是单线程的。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 23 §04
    T.section(prs, "04", "破案",
              "八个策略全军覆没，需要一个解释", accent=ACC)

    # ======================================================== 24 立假设
    s = T.blank(prs)
    y = T.head(s, "乙类到底在拧什么旋钮", kicker="任务 3a　立假设", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("乙类不改「踢谁」，它改的是「新块进来时，站在什么位置上」。",
             16, False, INK)]])

    cw = (CONTENT_W - Inches(0.8)) / 3
    yc = y + Inches(0.68)
    for k, (ttl, body, col) in enumerate([
        ("它做的事", "把新块插在「最该被踢」的位置，"
                    "LIP 就是插到 LRU 位。", INK),
        ("它下的赌注", "赌它被踢掉之前还会被用到一次，"
                     "中了就晋升，没中就淘汰。", INK),
        ("它的隐含前提", "赌注要有时间兑现。Cache 的轮换必须"
                      "慢到「等得起」。", RED),
    ]):
        xx = M + (cw + Inches(0.4)) * k
        T.card(s, xx, yc, cw, Inches(2.34),
               fill=RED_DIM if col == RED else PAPER_DIM)
        T.txt(s, xx + Inches(0.3), yc + Inches(0.26), cw - Inches(0.6),
              Inches(1.8),
              [[(ttl, 19, True, col if col == RED else ACC)],
               [(body, 14.5, False, INK)]], spacing=1.44)

    T.note(s, M, y + Inches(3.30), CONTENT_W,
           "第三条是假设，不是事实。任务 3 要你去验它。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 25 加统计量
    s = T.blank(prs)
    y = T.head(s, "给 gem5 加两个计数器", kicker="任务 3b　量化", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("假设里有「时间」两个字，就必须有一个量把时间量出来。",
             16, False, INK)]])

    cw = (CONTENT_W - Inches(0.44)) / 2
    yc = y + Inches(0.68)
    T.card(s, M, yc, cw, Inches(2.30))
    T.txt(s, M + Inches(0.32), yc + Inches(0.26), cw - Inches(0.64),
          Inches(1.8),
          [[("refsPerInsertion", 18, True, ACC, True)],
           [("总访问次数 ÷ 总插入次数", 15, True, INK)],
           [("一块数据从进来到被换走，被访问了多少次。", 14, False, INK)],
           [("—— 这个 Cache 轮换有多快。", 14, False, INK)]],
          spacing=1.44)

    T.card(s, M + cw + Inches(0.44), yc, cw, Inches(2.30))
    T.txt(s, M + cw + Inches(0.76), yc + Inches(0.26), cw - Inches(0.64),
          Inches(1.8),
          [[("avgFirstTouchDelay", 18, True, ACC, True)],
           [("插入 → 第一次命中的平均间隔", 15, True, INK)],
           [("乙类下的那个赌注，平均要等多久才兑现。", 14, False, INK)],
           [("—— 赌注有多长的寿命。", 14, False, INK)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.26), CONTENT_W,
           "两个计数器，一次编译，案子就破了。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 26 一个数
    s = T.blank(prs)
    y = T.head(s, "一个数，解释全部", kicker="任务 3b　★ 本次实验的核心",
               accent=ACC)

    cw = Inches(5.7)
    for k, (ttl, val, unit, l1, l2, col) in enumerate([
        ("L1D　64kB / 4 路", "112.38", "refsPerInsertion",
         "换走一块之前，L1D 已经被访问了 112 次。",
         "第一次命中平均等 17 个周期。", RED),
        ("L2　64kB / 4 路", "0.62", "refsPerInsertion",
         "换走一块之前，L2 平均连一次访问都没有。",
         "第一次命中平均等 91,388 个周期。", GREEN),
    ]):
        xx = M + (cw + Inches(0.43)) * k
        T.card(s, xx, y, cw, Inches(2.86),
               fill=RED_DIM if col == RED else GREEN_DIM)
        T.txt(s, xx + Inches(0.34), y + Inches(0.24), cw - Inches(0.68),
              Inches(0.36), [(ttl, 17, True, col)])
        T.stat(s, xx + Inches(0.34), y + Inches(0.68), cw - Inches(0.68),
               val, unit, color=col, size=52)
        T.txt(s, xx + Inches(0.34), y + Inches(1.98), cw - Inches(0.68),
              Inches(0.8), [[(l1, 14.5, False, INK)], [(l2, 14.5, True, INK)]],
              spacing=1.38)

    T.txt(s, M, y + Inches(3.14), Inches(11.8), Inches(0.9),
          [[("同一个旋钮，在这两个位置上面对的时间尺度相差 ",
             18, False, INK),
            ("5,400 倍", 30, True, ACC, True),
            ("。", 18, False, INK)]])
    T.foot(s, FOOT)

    # ======================================================== 27 赌注寿命
    s = T.blank(prs)
    y = T.head(s, "赌注还没兑现，块就已经被换走了", kicker="任务 3b　判决",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("把两个数除一下，乙类为什么无效就是算术问题了：",
             16, False, INK)]])

    for k, (val, lab, sub, col) in enumerate([
        ("16.7", "赌注能活多久", "8,351 tick ÷ 500", RED),
        ("90,918", "块能活多久", "1,137,187 ÷ (12,808/1024)", INK),
        ("0.018%", "赌注寿命 / 块寿命", "旋钮的有效行程", RED),
    ]):
        T.stat(s, M + Inches(4.05) * k, y + Inches(0.72), Inches(3.7),
               val, lab, color=col, size=46, sub=sub)

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(0.9),
          [[("乙类想调节的是「块在低优先级上停留多久」。",
             16, False, INK)],
           [("而在 L1，这段时间只占块整个寿命的万分之二 —— "
             "旋钮拧到底也没有行程。", 16, True, RED)]], spacing=1.42)

    T.note(s, M, y + Inches(3.70), CONTENT_W,
           "赌注活 16.7 周期，块活 90,918 周期。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 28 访存账
    s = T.blank(prs)
    y = T.head(s, "把账算平：一块 64 B 的去向", kicker="任务 3b　自检",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("qnn 按字节读 int8。一块 64 B 装进 L1D，理应被访问 64 次。"
             "数一数：", 16, False, INK)]])

    hbars(s, M, y + Inches(0.66), Inches(11.4), [
        ("MSHR 失效", 1.0, RED, "1.0 次"),
        ("MSHR 命中", 14.6, GOLD, "14.6 次"),
        ("Cache 命中", 48.1, GREEN, "48.1 次"),
        ("合计", 63.7, INK, "63.7 ≈ 64"),
    ], bar_h=Inches(0.42), gap=Inches(0.22), label_w=Inches(1.9),
        val_w=Inches(1.7), maxv=63.7, label_size=14.5, value_size=13.5)

    T.txt(s, M, y + Inches(3.16), Inches(11.8), Inches(0.5),
          [[("账要是不平，说明你的统计量插错了地方 —— ", 16, False, INK),
            ("先修统计量，再谈结论。", 16, True, ACC)]])

    T.note(s, M, y + Inches(3.78), CONTENT_W,
           "账正好平。这说明统计量的定义没写错。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 29 punch
    T.punch(prs,
            [("八个策略不是写得不好。", False),
             ("是在 L1 这个位置上，", False),
             ("它们的旋钮没有接到任何东西。", True)],
            sub="同一个策略换个位置就管用 —— 下一节我们把它搬到 L2 去验。",
            accent=ACC)

    # ======================================================== 30 §05
    T.section(prs, "05", "判决实验",
              "把同样的十五个策略，原样搬到 L2 上再跑一遍", accent=ACC)

    # ======================================================== 31 L1 vs L2
    s = T.blank(prs)
    y = T.head(s, "同一个策略，换一层就翻身", kicker="任务 3c　判决",
               accent=ACC)

    T.table(s, M, y, Inches(8.5), [
        ["策略", "类", "在 L1", "在 L2", "L2 周期数"],
        ["lru（基准）", "甲", "—", "—", "2,364,097"],
        ["lfu", "甲", "−45.7%", "−33.2%", "1,932,524"],
        ["mru", "甲", "−40.1%", "−4.4%", "2,298,462"],
        ["random", "甲", "−32.6%", "−33.4%", "1,929,197"],
        ["lip", "乙", "±0", "−35.1%", "1,901,750"],
        ["bip", "乙", "±0", "−39.8%", "1,843,016"],
        ["brrip", "乙", "±0", "−39.4%", "1,854,701"],
        ["ship", "乙", "±0", "−40.3%", "1,837,617"],
        ["rrip", "乙", "±0", "±0", "2,364,811"],
    ], col_w=[2.0, 0.8, 1.6, 1.6, 2.2], size=12.5, head_size=12,
        row_h=Inches(0.36), mono_cols=(2, 3, 4), hi_rows=(8,),
        hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.txt(s, Inches(9.5), y + Inches(0.16), Inches(3.3), Inches(3.4),
          [[("L1 的冠军", 16, True, INK)],
           [("lfu −45.7%", 15, True, RED, True)],
           [("到 L2 排第四。", 14, False, INK_SOFT)],
           [("", 9, False, INK)],
           [("L1 完全无效的", 16, True, INK)],
           [("ship ±0", 15, True, RED, True)],
           [("到 L2 是第一。", 14, False, INK_SOFT)],
           [("", 9, False, INK)],
           [("mru 从 −40.1% 掉到 −4.4%。", 14, True, ACC)]], spacing=1.34)

    T.note(s, M, y + Inches(3.72), CONTENT_W,
           "策略没变，代码没变。变的只是它站在哪一层。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 32 排名反转
    s = T.blank(prs)
    y = T.head(s, "排名是彻底反转的", kicker="任务 3c　判决", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("按 MSHR 失效的降幅排名，两层的前几名几乎没有交集：",
             16, False, INK)]])

    cw = (CONTENT_W - Inches(0.44)) / 2
    yc = y + Inches(0.66)
    T.card(s, M, yc, cw, Inches(2.74))
    T.txt(s, M + Inches(0.34), yc + Inches(0.24), cw - Inches(0.68),
          Inches(2.2),
          [[("在 L1 有效的", 19, True, RED)],
           [("lfu　−45.7%　　甲", 15.5, True, INK, True)],
           [("mru　−40.1%　　甲", 15.5, True, INK, True)],
           [("random　−32.6%　甲", 15.5, True, INK, True)],
           [("八个乙类，全部 ±0。", 14, False, INK_SOFT)]], spacing=1.44)

    T.card(s, M + cw + Inches(0.44), yc, cw, Inches(2.74), fill=GREEN_DIM)
    T.txt(s, M + cw + Inches(0.78), yc + Inches(0.24), cw - Inches(0.68),
          Inches(2.2),
          [[("在 L2 有效的", 19, True, GREEN)],
           [("ship　−40.3%　　乙", 15.5, True, INK, True)],
           [("bip　−39.8%　　乙", 15.5, True, INK, True)],
           [("brrip　−39.4%　乙", 15.5, True, INK, True)],
           [("mru 掉到 −4.4%，几乎无效。", 14, False, INK_SOFT)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "112.38 对 0.62 —— 反转的原因只有这一个。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 33 punch
    T.punch(prs,
            [("一个策略「好不好」，", False),
             ("是它和所在层次的匹配问题，", False),
             ("不是它自己的属性。", True)],
            sub="这句话，比这次实验的任何一个数字都值钱。",
            accent=ACC)

    # ======================================================== 34 §06
    T.section(prs, "06", "预取器",
              "不加容量，也不换策略 —— 第二条路", accent=ACC)

    # ======================================================== 35 预取 vs 加容量
    s = T.blank(prs)
    y = T.head(s, "预取和加容量，不是一回事", kicker="任务 5　★ 交付物",
               accent=ACC)

    cw = (CONTENT_W - Inches(0.44)) / 2
    T.card(s, M, y, cw, Inches(2.60), fill=GREEN_DIM)
    T.txt(s, M + Inches(0.34), y + Inches(0.26), cw - Inches(0.68),
          Inches(2.0),
          [[("加容量", 21, True, GREEN)],
           [("让那次搬运根本不发生。", 16, True, INK)],
           [("数据本来就还在 Cache 里，压根不用去下一层要。",
             14.5, False, INK)],
           [("总线上少一次事务。", 14.5, False, INK)]], spacing=1.44)

    T.card(s, M + cw + Inches(0.44), y, cw, Inches(2.60), fill=RED_DIM)
    T.txt(s, M + cw + Inches(0.78), y + Inches(0.26), cw - Inches(0.68),
          Inches(2.0),
          [[("加预取器", 21, True, RED)],
           [("搬运照样发生，只是提前发生。", 16, True, INK)],
           [("总线上的事务一次不少，甚至更多。", 14.5, False, INK)],
           [("—— 猜错的那些是白搬的。", 14.5, False, INK)]], spacing=1.44)

    T.txt(s, M, y + Inches(2.82), Inches(11.8), Inches(0.5),
          [[("要区分这两件事，看 ", 16, False, INK),
            ("l1d_mshr_mpki", 16, True, ACC, True),
            ("（真正发出去的请求数），不要看 ", 16, False, INK),
            ("l1d_miss_rate", 16, True, RED, True),
            ("。", 16, False, INK)]])

    T.note(s, M, y + Inches(3.50), CONTENT_W,
           "用 miss_rate 论证流量，任务 5 直接判不通过。",
           color=RED, fill=RED_DIM, size=15, icon="★")
    T.foot(s, FOOT)

    # ======================================================== 36 预取的代价
    s = T.blank(prs)
    y = T.head(s, "预取不是免费的", kicker="任务 4／6", accent=ACC)

    T.table(s, M, y, Inches(8.4), [
        ["指标", "算式", "它衡量的是"],
        ["覆盖率", "被预取命中的失效 ÷ 原失效", "收益：省掉了多少次等待"],
        ["准确率", "被用上的预取 ÷ 发出的预取", "代价：多少带宽和功耗白花了"],
    ], col_w=[1.5, 3.4, 3.5], size=13.5, head_size=12.5,
        row_h=Inches(0.52),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(1.86), Inches(8.4), Inches(1.4),
          [[("gem5 里可以直接挂的：", 15.5, False, INK)],
           [("tagged　stride　bop　ampm　isb", 15, True, ACC, True)],
           [("qnn 是顺序扫描，stride 一猜一个准；", 15.5, False, INK)],
           [("换成 pchase 这种指针追逐，准确率立刻塌掉 —— "
             "带宽和功耗照付。", 15.5, True, RED)]], spacing=1.42)

    # 中文大字比数字满格，stat() 的标签间距按数字算的会贴脸，这里手排。
    T.txt(s, Inches(9.45), y + Inches(0.34), Inches(3.13), Inches(0.72),
          [("两个数", 40, True, ACC)])
    T.txt(s, Inches(9.45), y + Inches(1.10), Inches(3.13), Inches(0.34),
          [("报告预取器必须两个都给", 13, True, INK)])
    T.txt(s, Inches(9.45), y + Inches(1.48), Inches(3.13), Inches(0.9),
          [("只报覆盖率，等于只报收益\n不报成本。任务 6 就是拿\n"
            "pchase 来揭这一层。", 11.5, False, INK_SOFT)], spacing=1.25)

    T.note(s, M, y + Inches(3.50), CONTENT_W,
           "只报覆盖率不报准确率，等于只报收益不报成本。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 37 交付与判分
    s = T.blank(prs)
    y = T.head(s, "交什么，怎么判", kicker="提交要求", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["交付物", "分值", "判分看的是"],
        ["任务 1　预测表 + 实测 + 对照组", "15", "有没有先预测；1c 缺席则任务 1 整体 0 分"],
        ["任务 2　源码 + diff + 验收记录", "20", "能编过、能被 --list 看到、能跑出结果"],
        ["任务 3　假设 → 统计量 → 判决", "30", "三环缺一环扣一环；只给结论不给链条不给分"],
        ["任务 4／5／6　数据与对比", "25", "用 mshr_mpki 论证流量，不是 miss_rate"],
        ["思考题 六道", "10", "答在自己的数据上，不是答在教科书上"],
    ], col_w=[4.2, 1.0, 6.6], size=13, head_size=12.5,
        row_h=Inches(0.50), mono_cols=(1,), hi_rows=(3,), hi_fill="EFE9F6",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(3.22), Inches(11.8), Inches(0.5),
          [[("三条红线：", 16, True, RED),
            ("把 <0.1% 的差异当结论　·　漏掉任务 1c　·　用 miss_rate 谈流量",
             16, False, INK)]])

    T.note(s, M, y + Inches(3.84), CONTENT_W,
           "按分析质量给分，不按「跑通」给分。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 38 一页纸
    s = T.blank(prs, dark=True)
    y = T.head(s, "这一次的一页纸", kicker="带走这六条", dark=True, accent=ACC)

    rows = [
        ("先算 N 和 A", "工作集 ÷ 容量 = 6.125 / 4，一个不等式定全局"),
        ("LRU 会系统性地踢错", "循环扫描下命中率恰好为 0，加相联度也救不了"),
        ("策略分两类", "改「踢谁」的甲类有效，改「插哪」的乙类全军覆没"),
        ("一个数解释全部", "refsPerInsertion：L1 是 112.38，L2 是 0.62"),
        ("好不好是匹配问题", "同一个 ship，L1 ±0，L2 −40.3%，代码一行没改"),
        ("预取不减流量", "它只是把流量提前；覆盖率是收益，准确率是代价"),
    ]
    for k, (t, d) in enumerate(rows):
        yy = y + Inches(0.72) * k
        T.rect(s, M, yy + Inches(0.14), Inches(0.13), Inches(0.13), ACC)
        T.txt(s, M + Inches(0.38), yy, Inches(4.5), Inches(0.4),
              [(t, 16.5, True, PAPER)])
        T.txt(s, M + Inches(5.1), yy + Inches(0.03), Inches(6.7), Inches(0.4),
              [(d, 14, False, WHITE_DIM)])

    T.txt(s, M, SLIDE_H - Inches(1.0), CONTENT_W, Inches(0.4),
          [("下一次：把流水线打开 —— 乱序执行与分支预测。",
            14, False, WHITE_DIM)])

    return prs


if __name__ == "__main__":
    prs = build()
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    print("wrote %s  (%d slides)" % (out, len(prs.slides._sldIdLst)))
