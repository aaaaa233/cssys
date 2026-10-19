# -*- coding: utf-8 -*-
"""实验一《性能评价与仿真方法学》讲课用 PPT。

    python _tools/ppt/lab1.py            → labs/lab1/幻灯片.pptx

所有数字来自 labs/lab1/参考解答.md，改数据请同步改那一处。
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
                   "..", "..", "labs", "lab1", "幻灯片.pptx")

ACC = T.LAB_ACCENT[1]          # 石墨蓝
FOOT = "实验一　性能评价与仿真方法学"


# ------------------------------------------------------------------ 水平条形图
def hbars(slide, x, y, w, rows, bar_h=Inches(0.4), gap=Inches(0.24),
          label_w=Inches(1.6), val_w=Inches(1.85), maxv=None,
          label_size=14, value_size=13):
    """并排水平条：rows = [(标签, 数值, 颜色, 数值文字), ...]，按最大值归一化。

    条形长度是成比例的——本课程的视觉母题，别用装饰色条代替。
    """
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
    T.cover(prs, 1,
            "性能评价与仿真方法学",
            "核心问题：用哪个 CPU 模型做后续实验，误差多大可接受\n"
            "同一份源码、同一个模拟器，性能可以差 3 倍——先把测量本身变成可信的",
            "计算机系统综合设计实验　·　4 学时　·　gem5 v25.0.0.1 / RISC-V SE")

    # ======================================================== 01 立题
    T.punch(prs,
            [("模拟器输出的数字，", False),
             ("默认是不可信的。", True),
             ("使其可信，是实验者的责任。", False)],
            sub="本次实验的目标不是「学会使用 gem5」——工具本身并不难掌握。"
                "难的是判断哪个数字可信、哪个不可信。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "本次实验要求做出的决策", kicker="任务", accent=ACC)
    T.txt(s, M, y, Inches(7.6), Inches(1.3),
          [[("后续六次实验，应当选用哪个 ", 22, False, INK),
            ("CPU 模型", 22, True, ACC),
            ("？", 22, False, INK)],
           [("测得的数据，其误差是否会导致", 22, False, INK),
            ("选错方案", 22, True, RED),
            ("？", 22, False, INK)]], spacing=1.35)
    T.bullets(s, M, y + Inches(1.72), Inches(7.5), [
        [("gem5 提供四个模型，精度与速度相差 ", 15.5, False, INK),
         ("数十倍", 15.5, True, INK)],
        [("选用快的可节省机时，但可能得出", 15.5, False, INK),
         ("方向相反", 15.5, True, RED, ),
         ("的结论", 15.5, False, INK)],
        [("此题没有标准答案，但须以", 15.5, False, INK),
         ("数据", 15.5, True, GREEN),
         ("支持所作的选择", 15.5, False, INK)],
    ], gap=Inches(0.58), marker=(INK_SOFT, RED, GREEN))

    T.note(s, M, y + Inches(3.62), Inches(7.5),
           "交付物中有一段 300 字的「模型选择声明」——那是本次实验的成果。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.stat(s, Inches(9.0), y + Inches(0.1), Inches(3.6), "4",
           "个 CPU 模型", color=ACC, size=62,
           sub="atomic / timing / minor / o3")
    T.stat(s, Inches(9.0), y + Inches(2.3), Inches(3.6), "23×",
           "最快与最慢的仿真速率之比", color=RED, size=62,
           sub="1,518,040 vs 356,115 指令/秒")
    T.foot(s, FOOT)

    # ======================================================== 03 三种天真
    s = T.blank(prs)
    y = T.head(s, "三个任务，纠正三种直觉", kicker="今天的路线", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["任务", "常见的预设", "实测结果"],
        ["任务 2", "程序的总耗时即算法的耗时",
         "启动段占用 40.26% 的周期"],
        ["任务 2(c)", "源码相同，测量结果就应相同",
         "一个编译参数，性能差 3.06 倍"],
        ["任务 4", "低成本模型只是精度较低",
         "低成本模型给出方向相反的结论"],
    ], col_w=[1.5, 4.6, 5.0], size=15, head_size=13,
        row_h=Inches(0.66),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])

    T.note(s, M, y + Inches(3.28), CONTENT_W,
           "三条都不是 gem5 的缺陷，而是「测量」本身固有的问题。"
           "换用真机或 FPGA，同样无法回避。",
           color=ACC, fill=PAPER_DIM, size=15.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 04 §1 节间
    T.section(prs, "01", "为什么非模拟器不可",
              "流片一次的成本在数百万至上亿元量级，不可能「先造出来再测量性能」。",
              accent=ACC)

    # ======================================================== 05 三档手段
    s = T.blank(prs)
    y = T.head(s, "评价手段只有三档", kicker="§1.1　方法学", accent=ACC)
    T.table(s, M, y, Inches(8.1), [
        ["手段", "速度", "精度", "什么时候用"],
        ["解析模型（Roofline）", "秒级", "量级正确", "早期排除不可行方案"],
        ["周期级模拟器 gem5", "慢 10⁴~10⁶ 倍", "5%~20% 误差", "设计空间探索"],
        ["FPGA 原型 / 流片", "接近实时", "精确", "方案定稿后验证"],
    ], col_w=[2.9, 1.7, 1.7, 2.4], size=13.5, head_size=12.5,
        row_h=Inches(0.52), hi_rows=(2,),
        aligns=[PP_ALIGN.LEFT] * 4)

    T.txt(s, M, y + Inches(2.5), Inches(8.1), Inches(0.32),
          [("「慢 10⁴ 倍」意味着：", 14, True, INK)])
    T.area_blocks(s, M, y + Inches(2.95), Inches(8.1), Inches(0.72), [
        ("真机 1 秒", 1.0, GREEN, PAPER),
        ("gem5 要跑约 3 小时", 40.0, RED, PAPER),
    ], label_size=13)
    T.txt(s, M, y + Inches(3.92), Inches(8.1), Inches(0.32),
          [("因此「如何在不失真的前提下压低测量成本」本身即是一门专门的技术。",
            13, False, INK_SOFT)])

    T.stat(s, Inches(9.4), y + Inches(0.5), Inches(3.2), "10⁴",
           "gem5 相对真机的减速", color=RED, size=58,
           sub="本课程的一切取舍都源于这一数量级")
    T.foot(s, FOOT)

    # ======================================================== 06 gem5 / SE
    s = T.blank(prs)
    y = T.head(s, "gem5 与 SE 模式", kicker="§1.2　工具", accent=ACC)
    y += Inches(0.22)

    T.card(s, M, y, Inches(5.72), Inches(2.3))
    T.txt(s, M + Inches(0.42), y + Inches(0.38), Inches(4.9), Inches(1.8),
          [[("周期级全系统模拟器", 21, True, INK)],
           [("", 7, False, INK)],
           [("逐条解释 RISC-V 指令，同时用软件模拟", 14.5, False, INK)],
           [("流水线、Cache、总线、DRAM 的时序。", 14.5, False, INK)],
           [("产出：该程序需要多少个周期。", 14.5, True, ACC)]], spacing=1.32)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.3))
    T.txt(s, M + Inches(6.53), y + Inches(0.38), Inches(4.9), Inches(1.8),
          [[("SE 模式（本课程用）", 21, True, INK)],
           [("", 7, False, INK)],
           [("不启动操作系统，系统调用由 gem5 代为处理。", 14.5, False, INK)],
           [("优点是启动快、配置简单；代价是无法测量", 14.5, False, INK)],
           [("OS 相关行为——对本课程已经足够。", 14.5, True, GREEN)]],
          spacing=1.32)

    T.code(s, M, y + Inches(2.70), CONTENT_W, [
        "$GEM5_BIN --outdir=out/试一下 framework/cssys_se.py \\",
        "    --cmd bench/bin/riscv/qnn --options \"8 1234\" --cpu o3",
        "python3 framework/stats.py out/试一下/stats.txt",
    ], size=13.5)
    T.txt(s, M, y + Inches(4.01), CONTENT_W, Inches(0.3),
          [("--options 的第二个参数为学号后四位。seed 不同则权重不同，"
            "曲线拐点会有差异。", 12.5, False, INK_SOFT)])
    T.foot(s, FOOT)

    # ======================================================== 07 §2 节间
    T.section(prs, "02", "性能究竟如何度量",
              "《计算机组成原理》中的那条公式仍然成立，且是今天全部讨论的基础。",
              accent=ACC)

    # ======================================================== 08 三因子
    s = T.blank(prs)
    y = T.head(s, "只有三个因子", kicker="§2.1　性能的定义", accent=ACC)
    T.txt(s, M, y, CONTENT_W, Inches(0.7),
          [[("CPU 时间", 27, True, INK),
            ("　=　", 27, False, INK_SOFT),
            ("指令数", 27, True, RED),
            ("　×　", 27, False, INK_SOFT),
            ("CPI", 27, True, ACC),
            ("　×　", 27, False, INK_SOFT),
            ("时钟周期", 27, True, GREEN)]], spacing=1.2)

    T.table(s, M, y + Inches(1.15), CONTENT_W, [
        ["因子", "主要由谁决定", "本课程在哪次实验中调整它"],
        ["指令数", "ISA、编译器、算法", "第 5、6 次　自定义指令直接减少指令数"],
        ["CPI", "微体系结构：流水线、Cache、分支预测", "第 2、3、4 次"],
        ["时钟周期", "工艺、流水级划分", "第 7 次　作为约束条件"],
    ], col_w=[1.8, 5.0, 5.0], size=14.5, head_size=13,
        row_h=Inches(0.62), aligns=[PP_ALIGN.LEFT] * 3)

    T.note(s, M, y + Inches(3.85), CONTENT_W,
           "本课程七次实验，即沿这三个因子各展开一次——最后在实验七合并计算。",
           color=ACC, fill=PAPER_DIM, size=15.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 09 IPC 不是性能
    s = T.blank(prs)
    y = T.head(s, "IPC 不是性能", kicker="§2.2　最常见的误报方式", accent=ACC)
    T.txt(s, M, y, Inches(7.7), Inches(0.34),
          [("一个反例：用一条自定义指令替换一段循环。", 15.5, False, INK)])

    T.table(s, M, y + Inches(0.6), Inches(7.7), [
        ["", "改之前", "改之后", "变化"],
        ["指令数", "100 万", "10 万", "↓ 10 倍"],
        ["IPC", "5.0", "1.0", "↓ 5 倍　表面上变差"],
        ["周期数", "20 万", "10 万", "↓ 2 倍　实际快一倍"],
    ], col_w=[1.7, 1.7, 1.7, 2.6], size=14.5, head_size=13,
        row_h=Inches(0.56), hi_rows=(3,), mono_cols=(1, 2),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT])

    T.note(s, M, y + Inches(3.72), Inches(7.7),
           "比较方案时一律报周期数。IPC 只用于解释原因，不用于得出结论。",
           color=RED, fill=RED_DIM, size=15, icon="★")

    T.card(s, Inches(9.05), y - Inches(0.05), Inches(3.55), Inches(4.40))
    T.txt(s, Inches(9.4), y + Inches(0.3), Inches(2.9), Inches(3.95),
          [[("加速比要用", 17, True, INK)],
           [("几何平均", 26, True, ACC)],
           [("", 8, False, INK)],
           [("A 比 B 快 4 倍，", 13.5, False, INK)],
           [("B 比 A 快 0.25 倍。", 13.5, False, INK)],
           [("", 5, False, INK)],
           [("算术平均：(4+0.25)/2 = 2.125", 13.5, False, RED)],
           [("两个方向不互为倒数，自相矛盾。", 13, False, INK_SOFT)],
           [("", 5, False, INK)],
           [("几何平均：√(4×0.25) = 1", 13.5, False, GREEN)],
           [("才自洽。", 13, False, INK_SOFT)]], spacing=1.3)
    T.foot(s, FOOT)

    # ======================================================== 10 §3 节间
    T.section(prs, "03", "测量的对象究竟是什么",
              "一个静态链接的 C 程序，在 main() 之前会执行大量与算法无关的代码。",
              accent=ACC)

    # ======================================================== 11 三段分解 ★
    s = T.blank(prs)
    y = T.head(s, "16% 的指令，占用 40% 的周期",
               kicker="任务 2(a)　qnn 8 / o3 实测", accent=ACC)

    T.txt(s, M, y + Inches(0.16), Inches(1.5), Inches(0.32),
          [("指令数", 15, True, INK_SOFT)])
    T.area_blocks(s, M + Inches(1.5), y, Inches(10.3), Inches(0.78), [
        ("启动 16.24%", 16.24, RED, PAPER),
        ("ROI　推理主循环 83.62%", 83.62, GREEN, PAPER),
        ("", 0.14, INK_SOFT, PAPER),
    ], label_size=14)

    T.txt(s, M, y + Inches(1.36), Inches(1.5), Inches(0.32),
          [("周期数", 15, True, INK_SOFT)])
    T.area_blocks(s, M + Inches(1.5), y + Inches(1.2), Inches(10.3),
                  Inches(0.78), [
        ("启动 40.26%", 40.26, RED, PAPER),
        ("ROI 58.50%", 58.50, GREEN, PAPER),
        ("", 1.23, INK_SOFT, PAPER),
    ], label_size=14)

    T.txt(s, M, y + Inches(2.4), CONTENT_W, Inches(0.34),
          [[("同一次运行，同一个程序。", 16, False, INK),
            ("上下两条的比例为何不同？", 16, True, INK)]])

    T.stat(s, M, y + Inches(3.0), Inches(3.4), "1.489",
           "启动段的 IPC", color=RED, size=46,
           sub="冷 Cache、直线代码、无循环可学习")
    T.stat(s, M + Inches(4.2), y + Inches(3.0), Inches(3.4), "5.276",
           "ROI 的 IPC", color=GREEN, size=46,
           sub="热循环、乱序核可利用的 ILP 集中于此")
    T.stat(s, M + Inches(8.4), y + Inches(3.0), Inches(3.4), "3.5×",
           "同一条指令，启动段多耗", color=INK, size=46,
           sub="周期数 = 指令数 ÷ IPC，差别源于此")
    T.foot(s, FOOT)

    # ======================================================== 12 三段实测表
    s = T.blank(prs)
    y = T.head(s, "三段各是什么", kicker="任务 2(a)　stats.txt 的三段",
               accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["段", "对应源码", "指令数", "周期数", "IPC", "L1D 失效率"],
        ["0　启动", "_start → ROI_BEGIN　libc 初始化、权重生成",
         "1,126,715", "756,839", "1.489", "26.90%"],
        ["1　ROI", "ROI_BEGIN → ROI_END　推理主循环",
         "5,801,400", "1,099,683", "5.276", "12.20%"],
        ["2　收尾", "ROI_END → exit　打印校验和",
         "9,835", "23,136", "0.425", "4.84%"],
        ["合计", "", "6,937,950", "1,879,658", "3.691", ""],
    ], col_w=[1.35, 4.3, 1.75, 1.75, 1.15, 1.5], size=13.5, head_size=12.5,
        row_h=Inches(0.5), hi_rows=(2,), mono_cols=(2, 3, 4, 5),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(3.05), Inches(7.4), Inches(0.9),
          [[("framework/stats.py 默认取第 1 段。", 15.5, True, INK)],
           [("两个 ROI 标记都使用「转储并重置」，因此启动段并未被丢弃，"
             "而是单独成段——一次运行即可量化。", 14.5, False, INK)]],
          spacing=1.35)

    T.note(s, Inches(8.8), y + Inches(3.05), Inches(3.75),
           "第 2 段过短，流水线未填满。",
           color=INK, fill=PAPER_DIM, size=13.5, icon="→")
    T.foot(s, FOOT)

    # ======================================================== 13 低估 30%
    s = T.blank(prs)
    y = T.head(s, "用全程序 IPC 会低估 30%",
               kicker="任务 2(a)　问题 2", accent=ACC)
    y += Inches(0.3)

    T.txt(s, M, y, Inches(7.6), Inches(0.4),
          [[("ROI IPC", 20, True, GREEN), ("　÷　", 20, False, INK_SOFT),
            ("全程序 IPC", 20, True, RED), ("　=　", 20, False, INK_SOFT),
            ("5.276 / 3.691", 20, True, INK, True),
            ("　=　", 20, False, INK_SOFT),
            ("1.43", 20, True, ACC, True)]])

    T.txt(s, M, y + Inches(0.85), Inches(7.6), Inches(0.9),
          [[("内核的真实 IPC 是全程序读数的 1.43 倍。", 17, True, INK)],
           [("不划分 ROI，所报的就不是算法的性能，而是算法与 glibc 启动的"
             "加权平均——而这两段代码的性质完全不同。", 15, False, INK)]],
          spacing=1.35)

    T.note(s, M, y + Inches(2.35), Inches(7.6),
           "「把启动段与内核平均」这一操作本身即是错误的：前者是访存密集的"
           "一次性初始化，后者是计算密集的热循环，平均值不代表其中任何一段。",
           color=RED, fill=RED_DIM, size=14.5, icon="★")

    T.card(s, Inches(9.0), y - Inches(0.15), Inches(3.6), Inches(3.5))
    T.txt(s, Inches(9.35), y + Inches(0.2), Inches(2.95), Inches(3.0),
          [[("写报告时", 17, True, INK)],
           [("", 6, False, INK)],
           [("凡报出一个比值，", 14.5, False, INK)],
           [("必须写明是由", 14.5, False, INK)],
           [("哪两个数相除。", 14.5, True, ACC)],
           [("", 8, False, INK)],
           [("只给出一个孤立的", 14.5, False, INK)],
           [("倍数，不予计分。", 14.5, True, RED)]], spacing=1.36)
    T.foot(s, FOOT)

    # ======================================================== 14 伪指令
    s = T.blank(prs)
    y = T.head(s, "ROI 是如何划定的", kicker="§3.2　gem5 伪指令", accent=ACC)

    T.code(s, M, y, Inches(7.6), [
        "#define ROI_BEGIN() M5OP_RAW(0x8400007b)   /* 转储并重置 */",
        "#define ROI_END()   M5OP_RAW(0x8400007b)",
        "",
        "0x8400007b = 1000010 ..... 1111011",
        "             └─func 0x42─┘ └op 0x7b┘",
    ], size=13.5, hi=(3, 4))

    T.bullets(s, M, y + Inches(2.05), Inches(7.6), [
        [("低 7 位 ", 15, False, INK), ("0x7b", 15, True, ACC, True),
         (" 是 RISC-V 留给厂商的 custom-3 空间", 15, False, INK)],
        [("高 7 位 ", 15, False, INK), ("0x42", 15, True, ACC, True),
         (" 是 gem5 定义的功能号：转储并重置统计", 15, False, INK)],
        [("在真实 RISC-V 上它是非法指令；在 gem5 中它触发模拟器动作",
          15, False, INK)],
    ], gap=Inches(0.55), marker=(ACC, ACC, INK_SOFT))

    T.card(s, Inches(8.9), y - Inches(0.05), Inches(3.7), Inches(4.42))
    T.txt(s, Inches(9.25), y + Inches(0.32), Inches(3.0), Inches(3.9),
          [[("这就是", 16, True, INK)],
           [("软硬件协同", 26, True, ACC)],
           [("的最小案例", 16, True, INK)],
           [("", 6, False, INK)],
           [("在 ISA 预留的编码空间中，", 14, False, INK)],
           [("我们自行规定一条指令的含义。", 14, False, INK)],
           [("", 6, False, INK)],
           [("第 5 次实验采用同样的方法，", 14, False, INK)],
           [("在 custom-0 中定义一条真正", 14, False, INK)],
           [("参与运算的新指令。", 14, True, ACC)]], spacing=1.32)
    T.foot(s, FOOT)

    # ======================================================== 15 加大负载
    s = T.blank(prs)
    y = T.head(s, "加大负载能替代 ROI 吗", kicker="任务 2(b)", accent=ACC)
    T.table(s, M, y, Inches(8.0), [
        ["样本数", "启动段周期", "启动占全程序周期", "全程序 IPC", "ROI IPC"],
        ["8", "756,839", "40.26%", "3.691", "5.276"],
        ["64", "756,839", "7.91%", "4.967", "5.278"],
    ], col_w=[1.3, 1.9, 2.2, 1.5, 1.4], size=14.5, head_size=12.5,
        row_h=Inches(0.55), mono_cols=(0, 1, 2, 3, 4),
        aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * 4)

    T.txt(s, M, y + Inches(1.95), Inches(8.0), Inches(0.34),
          [[("启动段的绝对开销：", 15.5, False, INK),
            ("756,839 → 756,839，完全不变。", 15.5, True, RED, True)]])
    T.txt(s, M, y + Inches(2.4), Inches(8.0), Inches(0.34),
          [[("改变的只是分母。加大负载可以", 15.5, False, INK),
            ("稀释", 15.5, True, INK), ("启动开销，不能", 15.5, False, INK),
            ("消除", 15.5, True, RED), ("它。", 15.5, False, INK)]])

    T.note(s, M, y + Inches(3.0), Inches(8.0),
           "n=64 时全程序 IPC 仍低估 6.3%，而仿真时间增加 8 倍——"
           "为省去一个成本≈0 的宏，这笔投入并不合算。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")

    T.stat(s, Inches(9.3), y + Inches(0.3), Inches(3.3), "8×",
           "仿真时间的代价", color=RED, size=54,
           sub="20 秒 → 160 秒")
    T.stat(s, Inches(9.3), y + Inches(2.3), Inches(3.3), "≈0",
           "划 ROI 的代价", color=GREEN, size=54,
           sub="两个宏，两条伪指令")
    T.foot(s, FOOT)

    # ======================================================== 16 §4 节间
    T.section(prs, "04", "同样的源码，性能差 3 倍",
              "本次实验的分水岭：它区分「运行完成」与「真正理解」。",
              accent=RED)

    # ======================================================== 17 四个二进制
    s = T.blank(prs)
    y = T.head(s, "四个二进制，同一份源码",
               kicker="任务 2(c)　唯一的区别是编译时是否加对齐参数", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["二进制", "ROI 标记", "对齐参数", "dot_i8 地址", "mod 64",
         "全程序指令", "全程序周期"],
        ["qnn", "✓", "✓", "0x10a40", "0", "6,937,950", "1,879,658"],
        ["qnn_noroi", "✗", "✓", "0x10a40", "0", "6,938,022", "1,879,671"],
        ["qnn_noalign", "✓", "✗", "0x1096a", "42", "6,924,469", "1,875,525"],
        ["qnn_noalign_noroi", "✗", "✗", "0x1095a", "26", "6,924,487",
         "5,732,767"],
    ], col_w=[2.9, 1.15, 1.15, 1.6, 1.1, 1.95, 1.95], size=13.5,
        head_size=12, row_h=Inches(0.52), hi_rows=(4,),
        mono_cols=(3, 4, 5, 6),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER,
                PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(3.15), CONTENT_W, Inches(0.34),
          [[("注意最后一行。", 16, True, RED),
            ("它与上面三行执行的指令数仅差 18 条，周期数却是它们的 3.06 倍。",
             16, False, INK)]])

    T.note(s, M, y + Inches(3.72), CONTENT_W,
           "差异 100% 来自微体系结构行为，与算法无关、与指令数无关、与访存量无关。",
           color=RED, fill=RED_DIM, size=15.5)
    T.foot(s, FOOT)

    # ======================================================== 18 punch 3 倍
    T.punch(prs,
            [("执行的指令几乎完全相同，", False),
             ("周期数差 3.06 倍。", True),
             ("而这 3 倍与所要研究的", False),
             ("任何设计决策都无关。", True)],
            sub="做体系结构实验，一半的工作在于控制住这类干扰项。",
            accent=RED)

    # ======================================================== 19 错误 vs 正确
    s = T.blank(prs)
    y = T.head(s, "不能直接得出「对齐就快」", kicker="任务 2(c)　问题 3",
               accent=ACC)
    y += Inches(0.25)

    T.card(s, M, y, Inches(5.72), Inches(2.75), RED_DIM)
    T.txt(s, M + Inches(0.42), y + Inches(0.34), Inches(4.9), Inches(2.1),
          [[("✗　常见错误结论", 18, True, RED)],
           [("", 7, False, INK)],
           [("「加对齐参数就快，不加就慢。」", 15.5, False, INK)],
           [("", 7, False, INK)],
           [("第三行：qnn_noalign 未加对齐，", 14.5, False, INK)],
           [("落在 mod64 = 42，却与对齐版本", 14.5, False, INK)],
           [("同样快，甚至快 0.22%。", 14.5, True, RED)]], spacing=1.32)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.75), GREEN_DIM)
    T.txt(s, M + Inches(6.53), y + Inches(0.34), Inches(4.9), Inches(2.1),
          [[("✓　正确结论", 18, True, GREEN)],
           [("", 7, False, INK)],
           [("不对齐不等于慢，", 15.5, False, INK)],
           [("不对齐等于让性能取决于偶然。", 15.5, True, GREEN)],
           [("", 7, False, INK)],
           [("64 个落点中多数无影响，个别几个", 14.5, False, INK)],
           [("是灾难。编译器既不知道也不关心。", 14.5, False, INK)]],
          spacing=1.32)

    T.note(s, M, y + Inches(3.15), CONTENT_W,
           "对齐不是优化手段，而是控制变量的手段——目的是使测量可重复，而非使程序更快。",
           color=ACC, fill=PAPER_DIM, size=15.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 20 取指机制
    s = T.blank(prs)
    y = T.head(s, "取指块：每周期只能取一个 64 字节对齐块",
               kicker="任务 2(c)　问题 4　机制", accent=ACC)
    T.table(s, M, y, Inches(8.3), [
        ["二进制", "mod 64", "fetch.cacheLines", "取指停顿周期", "占总周期"],
        ["qnn", "0", "10,953", "31,040", "1.7%"],
        ["qnn_noalign", "42", "222,546", "454,339", "24.2%"],
        ["qnn_noalign_noroi", "26", "1,853,127", "3,714,136", "64.8%"],
    ], col_w=[2.7, 1.1, 2.0, 1.7, 1.3], size=13.5, head_size=12,
        row_h=Inches(0.54), hi_rows=(3,), mono_cols=(1, 2, 3, 4),
        aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * 4)

    T.txt(s, M, y + Inches(2.5), Inches(8.3), Inches(0.9),
          [[("循环体跨在块边界上，每次迭代都要多访问一次 I-Cache。",
             15, False, INK)],
           [("mod64 = 26 时重取 185 万次 ≈ 平均每 3 条指令一次。",
             15, True, RED)]], spacing=1.4)

    T.txt(s, M, y + Inches(3.45), Inches(8.3), Inches(0.34),
          [[("5,732,767 − 3,714,136 = 2,018,631", 15, True, INK, True),
            ("　与对齐版本的 1,879,658 已是同一量级。", 15, False, INK)]])

    T.note(s, Inches(9.3), y + Inches(0.3), Inches(3.28),
           "取指停顿解释了这 3 倍。",
           color=GREEN, fill=GREEN_DIM, size=13, icon="✓")
    T.foot(s, FOOT)

    # ======================================================== 21 非线性容错
    s = T.blank(prs)
    y = T.head(s, "微体系结构的容错是非线性的",
               kicker="任务 2(c)　最重要的一段观察", accent=ACC)

    hbars(s, M, y + Inches(0.15), Inches(8.2), [
        ("mod64 = 0", 1.7, GREEN, "停顿 1.7%"),
        ("mod64 = 42", 24.2, GOLD, "停顿 24.2%"),
        ("mod64 = 26", 64.8, RED, "停顿 64.8%"),
    ], bar_h=Inches(0.46), gap=Inches(0.3), label_w=Inches(1.9),
        val_w=Inches(1.8))

    T.txt(s, M, y + Inches(2.7), Inches(8.2), Inches(0.34),
          [[("中间一组停顿增加 14 倍，总周期却", 15.5, False, INK),
            ("没有变慢", 15.5, True, GOLD),
            ("。", 15.5, False, INK)]])
    T.txt(s, M, y + Inches(3.15), Inches(8.2), Inches(0.34),
          [[("因为乱序核会隐藏停顿：只要 ROB 中还有指令可执行，后端就不会空闲。",
             15, False, INK)]])
    T.txt(s, M, y + Inches(3.6), Inches(8.2), Inches(0.34),
          [[("但隐藏能力有上限——到 64.8%，ROB 被耗尽，性能急剧下降。",
             15, True, RED)]])

    T.card(s, Inches(9.35), y + Inches(0.15), Inches(3.25), Inches(3.5))
    T.txt(s, Inches(9.68), y + Inches(0.5), Inches(2.6), Inches(2.9),
          [[("所以", 16, True, INK)],
           [("", 6, False, INK)],
           [("「我改动了一个小参数，", 14.5, False, INK)],
           [("测出来没有变化」", 14.5, False, INK)],
           [("", 6, False, INK)],
           [("推不出", 14.5, False, INK)],
           [("", 6, False, INK)],
           [("「这个参数不重要」。", 14.5, True, RED)]], spacing=1.34)
    T.foot(s, FOOT)

    # ======================================================== 22 两条规则
    s = T.blank(prs)
    y = T.head(s, "由此得到两条方法学规则", kicker="任务 2(c)　问题 5",
               accent=ACC)
    y += Inches(0.2)

    T.card(s, M, y, Inches(5.72), Inches(2.55))
    T.txt(s, M + Inches(0.42), y + Inches(0.32), Inches(4.9), Inches(2.0),
          [[("规则一", 13, True, ACC)],
           [("能直接测量的，不要用相减推算", 18, True, INK)],
           [("", 7, False, INK)],
           [("只有两个二进制的代码布局逐字节", 14.5, False, INK)],
           [("相同时，相减法才成立。而「源码", 14.5, False, INK)],
           [("相同、选项相同」推不出布局相同。", 14.5, True, RED)]],
          spacing=1.32)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.55))
    T.txt(s, M + Inches(6.53), y + Inches(0.32), Inches(4.9), Inches(2.0),
          [[("规则二", 13, True, ACC)],
           [("Makefile 强制对齐是为了可重复", 18, True, INK)],
           [("", 7, False, INK)],
           [("待测的收益是 15%，而落点的偶然性", 14.5, False, INK)],
           [("能带来 ±200% 的波动，测量便失去", 14.5, False, INK)],
           [("意义。应把随机变量固定为常数。", 14.5, True, GREEN)]],
          spacing=1.32)

    T.note(s, M, y + Inches(2.95), CONTENT_W,
           "本课程第一版参考解答即在规则一上出错：用 qnn_noroi 减 qnn 的 ROI，"
           "算出「启动段占 80.5%」，复核时才发现两个二进制不可比。",
           color=RED, fill=RED_DIM, size=15)
    T.foot(s, FOOT)

    # ======================================================== 23 §5 节间
    T.section(prs, "05", "四个 CPU 模型",
              "精度与速度相差数十倍。选择哪一个，是今天要提交的答案。",
              accent=ACC)

    # ======================================================== 24 速查表
    s = T.blank(prs)
    y = T.head(s, "四个模型建模到什么程度", kicker="§4　速查表", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["模型", "流水线", "乱序", "分支预测", "访存重叠", "适用场景"],
        ["atomic", "✗", "✗", "✗", "✗", "功能验证、快进、生成 checkpoint"],
        ["timing", "✗", "✗", "✗", "✗", "只关心访存行为，且不考虑重叠"],
        ["minor", "✓", "✗", "✓", "有限", "目标是低功耗顺序核时"],
        ["o3", "✓", "✓", "✓", "✓", "本课程后续默认——但需自行论证"],
    ], col_w=[1.5, 1.2, 1.1, 1.4, 1.4, 5.2], size=14, head_size=12.5,
        row_h=Inches(0.52), hi_rows=(4,),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER,
                PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.LEFT])

    # 表压到 0.52 行高，下面两块整体上移 0.20in，把页脚间距留够。
    T.txt(s, M, y + Inches(3.05), CONTENT_W, Inches(0.34),
          [[("atomic 的访存不经过总线，每次访存返回一个固定的估算延迟。",
             15, False, INK)]])
    T.note(s, M, y + Inches(3.55), CONTENT_W,
           "因此 atomic 给出的任何性能数字都不可引用——它只能证明程序计算正确。",
           color=RED, fill=RED_DIM, size=15.5)
    T.foot(s, FOOT)

    # ======================================================== 25 实测
    s = T.blank(prs)
    y = T.head(s, "同一个程序，四个模型的读数",
               kicker="任务 3　qnn 8 / ROI 段实测", accent=ACC)

    hbars(s, M, y + Inches(0.1), Inches(8.4), [
        ("timing", 25081750, RED, "25,081,750"),
        ("minor", 6724379, INK_SOFT, "6,724,379"),
        ("atomic", 6652265, INK_SOFT, "6,652,265"),
        ("o3", 1099658, GREEN, "1,099,658"),
    ], bar_h=Inches(0.44), gap=Inches(0.26), label_w=Inches(1.4),
        val_w=Inches(1.9))

    T.txt(s, M, y + Inches(3.05), Inches(8.4), Inches(0.3),
          [("ROI 周期数（越短越快）", 12.5, False, INK_SOFT)])

    T.txt(s, M, y + Inches(3.55), Inches(8.4), Inches(0.34),
          [[("同一段代码，读数相差 23 倍。", 16, True, INK),
            ("区别不是「准与不准」，而是在建模不同的机器。", 16, False, INK)]])

    T.card(s, Inches(9.5), y, Inches(3.1), Inches(3.4))
    T.txt(s, Inches(9.82), y + Inches(0.32), Inches(2.5), Inches(2.8),
          [[("主机耗时", 15, True, INK)],
           [("", 6, False, INK)],
           [("atomic　　3.8 s", 14, False, INK, True)],
           [("timing　　5.9 s", 14, False, INK, True)],
           [("minor　　15.5 s", 14, False, INK, True)],
           [("o3　　　 16.3 s", 14, True, GREEN, True)],
           [("", 8, False, INK)],
           [("最准确的模型只比最快的", 13.5, False, INK_SOFT)],
           [("多耗 4 倍机时，可以接受。", 13.5, True, GREEN)]], spacing=1.34)
    T.foot(s, FOOT)

    # ======================================================== 26 o3 失效率
    s = T.blank(prs)
    y = T.head(s, "o3 的失效率高 15 倍，它错了吗",
               kicker="§4.3　本次实验最反直觉的一个数据", accent=ACC)
    T.table(s, M, y, Inches(8.1), [
        ["", "minor", "o3", "差异"],
        ["l1d_misses　　失效次数", "12,835", "200,001", "15.6×"],
        ["l1d_mshr_misses　实际下发到 L2", "12,823", "12,823", "完全相同"],
        ["MLP = misses / mshr_misses", "1.001", "15.598", "15.6×"],
    ], col_w=[4.0, 1.5, 1.5, 1.6], size=14, head_size=12.5,
        row_h=Inches(0.58), hi_rows=(2,), mono_cols=(1, 2),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(2.65), Inches(8.1), Inches(0.4),
          [[("200,001", 19, True, RED, True), ("　=　", 19, False, INK_SOFT),
            ("187,178", 19, True, INK_SOFT, True),
            ("　被 MSHR 合并　+　", 15, False, INK),
            ("12,823", 19, True, GREEN, True),
            ("　实际流量", 15, False, INK)]])

    T.txt(s, M, y + Inches(3.3), Inches(8.1), Inches(0.34),
          [("乱序核会对同一个 Cache 块发出多次请求；后续请求挂在 MSHR 上等待，"
            "不再下发。", 14.5, False, INK)])

    T.note(s, Inches(9.4), y + Inches(0.4), Inches(3.2),
           "o3 的高失效率并非缺陷。",
           color=GREEN, fill=GREEN_DIM, size=13.5, icon="→")
    T.foot(s, FOOT)

    # ======================================================== 27 punch MSHR
    T.punch(prs,
            [("overallMisses 不是访存流量，", False),
             ("overallMshrMisses 才是。", True)],
            sub="从第 2 次实验起，这条规则将反复使用。"
                "凡以 o3 的 l1d_miss_rate 论证「Cache 容量不足」的，都是错误的。",
            accent=ACC)

    # ======================================================== 28 §6 节间
    T.section(prs, "06", "低成本模型是否会误导",
              "要检验的不是「模型是否准确」，而是「模型是否会导致方案选错」。",
              accent=RED)

    # ======================================================== 29 三种结论 ★
    s = T.blank(prs)
    y = T.head(s, "一个设计问题，三种相反的答案",
               kicker="任务 4　L1D 选 16kB 还是 128kB", accent=ACC)
    T.table(s, M, y, CONTENT_W, [
        ["模型", "16kB 周期数", "128kB 周期数", "该模型的结论", "对不对"],
        ["timing", "23,434,105", "28,133,615", "128kB 慢 20.1% → 选 16kB",
         "✗ 方向错"],
        ["minor", "6,657,131", "6,650,058", "两者差 0.11% → 无差异",
         "✗ 分辨不出"],
        ["o3", "1,074,577", "891,719", "128kB 快 17.0% → 选 128kB",
         "✓ 基准"],
    ], col_w=[1.4, 2.0, 2.0, 4.5, 1.7], size=14, head_size=12.5,
        row_h=Inches(0.62), hi_rows=(1,), mono_cols=(1, 2),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.LEFT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(3.1), CONTENT_W, Inches(0.34),
          [[("三个模型给出了三种结论：", 16.5, False, INK),
            ("反对、无差异、支持。", 16.5, True, RED)]])

    T.note(s, M, y + Inches(3.65), CONTENT_W,
           "若只运行 timing，将做出一个恰好相反的设计决策——"
           "并且不会察觉任何异常。",
           color=RED, fill=RED_DIM, size=15.5)
    T.foot(s, FOOT)

    # ======================================================== 30 各错在哪
    s = T.blank(prs)
    y = T.head(s, "各自错在何处", kicker="任务 4　问题 2、3", accent=ACC)
    y += Inches(0.2)

    T.card(s, M, y, Inches(5.72), Inches(2.9), RED_DIM)
    T.txt(s, M + Inches(0.42), y + Inches(0.34), Inches(4.9), Inches(2.3),
          [[("timing　结构性地偏向小 Cache", 17, True, RED)],
           [("", 7, False, INK)],
           [("容量翻 3 番 → 命中延迟 +3 周期。", 14.5, False, INK)],
           [("它的 MLP = 1.000，每个周期都直接", 14.5, False, INK)],
           [("计入总时间，没有任何隐藏。", 14.5, False, INK)],
           [("", 6, False, INK)],
           [("代价全额计入，收益无法兑现。", 14.5, True, RED)]], spacing=1.3)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.9))
    T.txt(s, M + Inches(6.53), y + Inches(0.34), Inches(4.9), Inches(2.3),
          [[("minor　分辨率不够", 17, True, INK)],
           [("", 7, False, INK)],
           [("它并未给出反向结论，只报告「无差异」。", 14.5, False, INK)],
           [("同样 MLP ≈ 1，同样无法把「失效减少」", 14.5, False, INK)],
           [("转化为收益，只是绝对延迟基数大，", 14.5, False, INK)],
           [("+3 周期被淹没了。", 14.5, False, INK)],
           [("", 6, False, INK)],
           [("这是巧合，而非正确。", 14.5, True, INK)]], spacing=1.3)

    T.note(s, M, y + Inches(3.3), CONTENT_W,
           "timing 给出明显的反向结论，一验证即可发现；"
           "minor 只报告「无差异」，会导致直接放弃 17% 的收益。",
           color=ACC, fill=PAPER_DIM, size=15)
    T.foot(s, FOOT)

    # ======================================================== 31 punch 假阴性
    T.punch(prs,
            [("假阴性比假阳性", False),
             ("更难发现。", True),
             ("因为无从知晓", False),
             ("自己错过了什么。", True)],
            sub="minor 的错误比 timing 更危险——这是本次实验最需要记住的一条。",
            accent=RED)

    # ======================================================== 32 两种保真
    s = T.blank(prs)
    y = T.head(s, "需要的是排序保真，不是绝对保真",
               kicker="§5　误差如何看待", accent=ACC)
    y += Inches(0.3)

    T.card(s, M, y, Inches(5.72), Inches(2.35))
    T.txt(s, M + Inches(0.42), y + Inches(0.36), Inches(4.9), Inches(1.7),
          [[("绝对保真", 21, True, INK_SOFT)],
           [("", 7, False, INK)],
           [("IPC 数值接近真机。", 15, False, INK)],
           [("性能预测、产品规格承诺需要它。", 15, False, INK)],
           [("本课程不需要。", 15, True, INK_SOFT)]], spacing=1.34)

    T.card(s, M + Inches(6.11), y, Inches(5.72), Inches(2.35), GREEN_DIM)
    T.txt(s, M + Inches(6.53), y + Inches(0.36), Inches(4.9), Inches(1.7),
          [[("排序保真", 21, True, GREEN)],
           [("", 7, False, INK)],
           [("A 比 B 好，模型也判定 A 比 B 好。", 15, False, INK)],
           [("设计空间探索只需要这一点。", 15, False, INK)],
           [("这是本课程的全部要求。", 15, True, GREEN)]], spacing=1.34)

    T.txt(s, M, y + Inches(2.75), CONTENT_W, Inches(0.34),
          [[("一个模型只要保住排序，绝对值差 3 倍也仍然有用；", 16, False, INK),
            ("绝对值再准，排序错了就是有害的。", 16, True, RED)]])

    T.note(s, M, y + Inches(3.3), CONTENT_W,
           "「模拟器误差 20% 所以没用」这一说法，错在把误差当作标量——"
           "误差的方向与一致性，比大小更重要。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 33 负载规模
    s = T.blank(prs)
    y = T.head(s, "负载规模多大才足够", kicker="任务 5　成本与偏差的平衡",
               accent=ACC)
    T.table(s, M, y, Inches(7.5), [
        ["样本数", "ROI IPC", "相对 n=32 的偏差", "主机耗时"],
        ["2", "5.280", "−0.11%", "4.3 s"],
        ["4", "5.283", "−0.06%", "8.3 s"],
        ["8", "5.276", "−0.19%", "17.3 s"],
        ["16", "5.286", "−0.004%", "33.3 s"],
        ["32", "5.286", "—", "67.0 s"],
    ], col_w=[1.5, 1.8, 2.4, 1.8], size=13.5, head_size=12.5,
        row_h=Inches(0.45), hi_rows=(3,), mono_cols=(0, 1, 2, 3),
        aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * 3)

    T.txt(s, M, y + Inches(3.05), Inches(7.5), Inches(0.34),
          [[("IPC 从 n=2 起即已稳定，全程波动 < 0.2%。", 15.5, True, INK)]])
    T.txt(s, M, y + Inches(3.5), Inches(7.5), Inches(0.34),
          [[("主机耗时与样本数严格线性，斜率约 2.1 秒/样本。",
             15, False, INK)]])

    T.card(s, Inches(8.85), y - Inches(0.05), Inches(3.75), Inches(3.85))
    T.txt(s, Inches(9.2), y + Inches(0.3), Inches(3.05), Inches(3.2),
          [[("选 n = 8", 26, True, GREEN)],
           [("", 8, False, INK)],
           [("20 个配置点 / 8 核 = 3 轮", 14, False, INK)],
           [("n=8：约 52 秒", 14, True, GREEN, True)],
           [("n=32：约 201 秒", 14, False, INK_SOFT, True)],
           [("", 8, False, INK)],
           [("偏差 0.19%，任务 4 的效应是 17%。", 14, False, INK)],
           [("信噪比约 90:1，足够。", 14, True, GREEN)],
           [("", 8, False, INK)],
           [("仅说「n=8 偏差小」不是工程判断，", 13.5, False, INK_SOFT)],
           [("把偏差与效应并置比较才是。", 13.5, False, INK_SOFT)]],
          spacing=1.32)
    T.foot(s, FOOT)

    # ======================================================== 34 噪声地板
    s = T.blank(prs)
    y = T.head(s, "噪声地板有多高", kicker="§6　最后一条纪律", accent=ACC)

    T.txt(s, M, y, Inches(7.9), Inches(0.34),
          [("gem5 是完全确定性的。但只要有一处不同，结果就会波动。",
            15.5, False, INK)])

    T.code(s, M, y + Inches(0.55), Inches(7.9), [
        "--cmd bench/bin/riscv/qnn           → ROI 1,099,683 周期",
        "--cmd /mnt/.../bench/bin/riscv/qnn  → ROI 1,099,658 周期",
        "                                       差 25 个周期",
    ], size=13, hi=(2,))

    T.txt(s, M, y + Inches(2.05), Inches(7.9), Inches(0.7),
          [[("唯一的差别是命令行多了 21 个字符。", 15, True, INK)],
           [("SE 模式下 argv 压在初始栈上，字符串变长 → 整个栈平移 → "
             "栈上数据所落的 Cache 组随之改变。", 14.5, False, INK)]],
          spacing=1.35)

    T.table(s, M, y + Inches(3.05), Inches(7.9), [
        ["干扰源", "影响量级", "本课程的处理方式"],
        ["热函数的代码对齐", "3 倍", "编译时强制 64B 对齐，予以固定"],
        ["argv 字符串长度", "0.002%", "无法消除，但已量化"],
    ], col_w=[2.6, 1.6, 3.7], size=13.5, head_size=12.5, row_h=Inches(0.48),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT])

    T.stat(s, Inches(9.3), y + Inches(0.35), Inches(3.3), "0.1%",
           "本课程的判定线", color=RED, size=58,
           sub="小于它的差异，一律视为「无差异」")
    T.note(s, Inches(9.3), y + Inches(2.5), Inches(3.3),
           "声称「A 比 B 好」之前，先确认它是噪声的几倍。",
           color=ACC, fill=PAPER_DIM, size=13.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 35 交付
    s = T.blank(prs)
    y = T.head(s, "交什么，怎么判", kicker="提交要求", accent=ACC)
    y += Inches(0.15)

    T.card(s, M, y, Inches(3.75), Inches(3.0))
    T.txt(s, M + Inches(0.36), y + Inches(0.32), Inches(3.1), Inches(2.4),
          [[("表与图", 26, True, ACC)],
           [("任务 1~5 全部", 16, True, INK)],
           [("", 8, False, INK)],
           [("图必须有坐标轴标签和单位。", 14.5, False, INK)],
           [("每个「要回答」都须作答，", 14.5, False, INK)],
           [("结论须指向自己的数据。", 14.5, True, ACC)]], spacing=1.34)

    T.card(s, M + Inches(4.04), y, Inches(3.75), Inches(3.0))
    T.txt(s, M + Inches(4.40), y + Inches(0.32), Inches(3.1), Inches(2.4),
          [[("300 字", 26, True, ACC)],
           [("模型选择声明", 16, True, INK)],
           [("", 8, False, INK)],
           [("选用哪个模型、为什么、", 14.5, False, INK)],
           [("预计它在什么情况下", 14.5, False, INK)],
           [("会产生误导。", 14.5, True, ACC)]], spacing=1.34)

    T.card(s, M + Inches(8.08), y, Inches(3.75), Inches(3.0))
    T.txt(s, M + Inches(8.44), y + Inches(0.32), Inches(3.1), Inches(2.4),
          [[("40 / 30", 26, True, RED)],
           [("分析 / 跑通", 16, True, INK)],
           [("", 8, False, INK)],
           [("一张填满数字但无解释的表，", 14.5, False, INK)],
           [("分低于一张只有三个点、", 14.5, False, INK)],
           [("但讲清楚机制的图。", 14.5, True, RED)]], spacing=1.34)

    T.note(s, M, y + Inches(3.25), CONTENT_W,
           "只写「用 o3 因为它最准」仅达及格线。须体现成本意识与例外情况才算完整。",
           color=ACC, fill=PAPER_DIM, size=15.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 36 一页纸
    s = T.blank(prs, dark=True)
    y = T.head(s, "本次带走的五条结论", kicker="一页纸", dark=True, accent=ACC)
    T.bullets(s, M, y + Inches(0.25), CONTENT_W, [
        [("不划 ROI，测的就是 glibc 的启动性能——", 17, False, PAPER),
         ("16% 的指令占用 40% 的周期", 17, True, PAPER)],
        [("能直接测量的，绝不用两次运行相减推算——", 17, False, PAPER),
         ("布局一变，差 3 倍", 17, True, PAPER)],
        [("对齐不是优化，而是控制变量——", 17, False, PAPER),
         ("目的是可重复，不是变快", 17, True, PAPER)],
        [("overallMisses 不是流量，", 17, False, PAPER),
         ("overallMshrMisses 才是", 17, True, PAPER)],
        [("低成本模型不是不够准，而是会导致选错——", 17, False, PAPER),
         ("要排序保真，不要绝对保真", 17, True, PAPER)],
    ], gap=Inches(0.72), marker=ACC, marker_size=Inches(0.15))

    T.txt(s, M, SLIDE_H - Inches(1.5), CONTENT_W, Inches(0.4),
          [("下一次：展开 Cache 的设计空间，看这五条纪律如何应用。",
            15, False, WHITE_DIM)])
    T.foot(s, FOOT, dark=True)

    prs.save(os.path.abspath(OUT))
    print("wrote %s  (%d slides)"
          % (os.path.abspath(OUT), len(prs.slides._sldIdLst)))


if __name__ == "__main__":
    build()
