# -*- coding: utf-8 -*-
"""实验五《软硬件协同 I：自定义指令》讲课用 PPT。

    python _tools/ppt/lab5.py            → labs/lab5/幻灯片.pptx

所有数字来自 labs/lab5/参考解答.md，改数据请同步改那一处。
主表口径：--cpu o3 --dotp8-lat 3，seed 0x01352505。
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
                   "..", "..", "labs", "lab5", "幻灯片.pptx")

ACC = T.LAB_ACCENT[5]          # 洋红
DIM = "F7E3EA"                 # 洋红的浅色（表格高亮行用）
FOOT = "实验五　软硬件协同 I：自定义指令"


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


# ------------------------------------------------------------------ 字节长度条
BPI = Inches(0.124)            # 每字节的绘图宽度：64 B ≈ 7.94 in


def bytebar(slide, x, y, nbytes, h, fill, label, fg=PAPER, size=13):
    """按字节数等比画一条横条，用来比"循环体多少字节"。"""
    w = int(BPI * nbytes)
    T.rect(slide, x, y, w, h, fill)
    T.txt(slide, x + Inches(0.14), y, w - Inches(0.28), h,
          [(label, size, True, fg)], anchor=MSO_ANCHOR.MIDDLE)
    return w


# ------------------------------------------------------------------ 位域图
def bitfield(slide, x, y, w, h, cells, size=12.5, lab_size=10.5):
    """32 位指令位域：cells = [(位宽, 上文字, 下文字, 填色, 文字色), ...]，位宽求和须为 32。"""
    total = float(sum(c[0] for c in cells))
    cx = x
    for bits, top, bot, fill, fg in cells:
        cw = int(w * bits / total)
        T.rect(slide, cx, y, cw, h, fill)
        T.txt(slide, cx, y, cw, h, [(top, size, True, fg, True)],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        T.txt(slide, cx, y + h + Inches(0.05), cw, Inches(0.26),
              [(bot, lab_size, False, INK_SOFT)], align=PP_ALIGN.CENTER)
        cx += cw
    return y + h + Inches(0.34)


def build():
    prs = T.new_deck()

    # ======================================================== 00 封面
    T.cover(prs, 5,
            "软硬件协同 I：\n自定义指令",
            "核心问题：这条新指令该做多少事\n"
            "动态指令数从 580 万降到 82 万，程序只快 3 倍——少掉的 86% 去哪了",
            "计算机系统综合设计实验　·　4 学时　·　改 gem5 的译码器")

    # ======================================================== 01 立题
    T.punch(prs,
            [("加一条指令，很容易。", False),
             ("让它真的变快，很难。", True),
             ("本次实验会加成功，", False),
             ("然后连撞三个坑。", True)],
            sub="三个坑分别是：算错的加速比、看不见的依赖链、多出来的两个字节。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "本次实验要做的决策", kicker="任务", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("实验二到四都在既有硬件里挪资源。本次动 ISA："
             "自己造一条指令，再回答四个问题——", 17, False, INK)]])

    cw = (CONTENT_W - Inches(0.9)) / 4
    yc = y + Inches(0.66)
    for k, (ttl, body) in enumerate([
        ("加什么指令", "一条指令干几件事，才划算"),
        ("挂哪个功能单元", "延迟给几拍，是硬件的成本"),
        ("软件怎么配合", "同一条指令，写法差 1.49 倍"),
        ("代价是什么", "指令变宽，取指带宽先崩"),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, yc, cw, Inches(1.42))
        T.txt(s, xx + Inches(0.22), yc + Inches(0.24), cw - Inches(0.44),
              Inches(1.0),
              [[(ttl, 17, True, ACC)],
               [(body, 13.5, False, INK)]], spacing=1.4)

    T.txt(s, M, y + Inches(2.34), Inches(11.8), Inches(1.0),
          [[("问：软硬件各自能拿走多少收益？", 21, True, INK)],
           [("同一条 dotp8 指令，最差软件 3.03 倍，最好软件 4.50 倍。硬件只做了一次。",
             17, False, INK_SOFT)]], spacing=1.42)

    T.note(s, M, y + Inches(3.36), CONTENT_W,
           "本次实验要改 gem5 源码并重新编译，一次约 7 分钟。请珍惜每一次编译。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 03 §01
    T.section(prs, "01", "加一条指令，要动哪几处",
              "在改代码之前，先把四步和三个陷阱说清楚", accent=ACC)

    # ======================================================== 04 §1.1 四步
    s = T.blank(prs)
    y = T.head(s, "一条新指令要落四个地方", kicker="补课 1.1", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["步骤", "改哪里", "作用", "本次实验"],
        ["① 挑编码", "RISC-V 手册 custom 槽", "占一个不冲突的 opcode", "custom-0 = 0x0b"],
        ["② 写译码", "src/arch/riscv/isa/decoder.isa", "让 gem5 认得这 32 位", "写 40 行"],
        ["③ 配单元", "src/cpu/o3/…FUPool", "决定它占几拍、几个口", "SimdMultAcc"],
        ["④ 发指令", "汇编 .insn / 内联汇编", "让程序真的用上它", "改 qnn 内循环"],
    ], col_w=[Inches(1.5), Inches(3.9), Inches(3.3), Inches(3.133)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1, 3))

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("汇编器不用改。", 20, True, INK)],
           [("GNU as 的 .insn 伪指令可以直接拼出任意 32 位编码——"
             "这是本次实验能在 4 学时内做完的关键。", 16, False, INK_SOFT)]],
          spacing=1.42)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "少了第 ③ 步也能跑：gem5 会给未指定 OpClass 的指令挂 IntAlu、延迟 1 拍——"
           "于是你测出一个白送的加速比。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 05 §1.2 R 型位域
    s = T.blank(prs)
    y = T.head(s, "R 型指令的 32 个位，怎么分", kicker="补课 1.2", accent=ACC)

    bitfield(s, M, y, CONTENT_W, Inches(0.72), [
        (7, "funct7", "31…25", INK, PAPER),
        (5, "rs2", "24…20", "3E4A57", PAPER),
        (5, "rs1", "19…15", "3E4A57", PAPER),
        (3, "funct3", "14…12", INK, PAPER),
        (5, "rd", "11…7", "3E4A57", PAPER),
        (7, "opcode", "6…0", ACC, PAPER),
    ])

    T.txt(s, M, y + Inches(1.14), Inches(11.8), Inches(0.44),
          [[("gem5 的译码树不看全部 7 位 opcode。低 2 位恒为 11（表示 32 位指令），"
             "它只看 bit[6:2] —— 即 ", 15.5, False, INK),
            ("OPCODE5", 15.5, True, ACC, True),
            ("。", 15.5, False, INK)]])

    yc = y + Inches(1.66)
    T.txt(s, M, yc, Inches(11.8), Inches(0.34),
          [[("四个 custom 槽（RISC-V 手册留给用户的编码空间）", 16, True, INK)]])

    cw = (CONTENT_W - Inches(0.72)) / 4
    for k, (nm, op7, op5, taken) in enumerate([
        ("custom-0", "0x0b", "0x02", None),
        ("custom-1", "0x2b", "0x0a", None),
        ("custom-2", "0x5b", "0x16", None),
        ("custom-3", "0x7b", "0x1e", "已被 M5Op 占用"),
    ]):
        xx = M + (cw + Inches(0.24)) * k
        T.card(s, xx, yc + Inches(0.38), cw, Inches(1.42),
               fill=RED_DIM if taken else PAPER_DIM)
        T.txt(s, xx + Inches(0.2), yc + Inches(0.52), cw - Inches(0.4),
              Inches(1.16),
              [[(nm, 16, True, RED if taken else ACC)],
               [("opcode " + op7, 13, False, INK, True)],
               [("OPCODE5 " + op5, 13, True, INK, True)],
               [(taken or "可用", 12.5, True, RED if taken else GREEN)]],
              spacing=1.3)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "0x0b >> 2 == 0x02。写 decoder.isa 时填的是 0x02，不是 0x0b——填错一位，"
           "指令会被译成别人。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 06 §1.3 decoder.isa
    s = T.blank(prs)
    y = T.head(s, "decoder.isa 是一棵 switch 树", kicker="补课 1.3", accent=ACC)

    T.code(s, M, y, Inches(7.0), [
        "decode OPCODE5 default Unknown::unknown() {",
        "  0x02: decode FUNCT3 {",
        "    0x0: decode FUNCT7 {",
        "      0x0: dotp8({{",
        "        /* C++ 语句写在这里 */",
        "      }}, IntAlu);",
        "    } }",
        "}",
    ], size=13.5, hi=(1, 5))

    T.txt(s, Inches(8.0), y + Inches(0.04), Inches(4.58), Inches(2.6),
          [[("三层筛选", 19, True, ACC)],
           [("OPCODE5 → FUNCT3 → FUNCT7，", 15, False, INK)],
           [("一层比一层细。", 15, False, INK)],
           [("", 9, False, INK)],
           [("大括号里是真正的 C++，", 15, False, INK)],
           [("在模拟器里被直接执行。", 15, False, INK)]], spacing=1.34)

    T.txt(s, M, y + Inches(2.82), Inches(11.8), Inches(0.74),
          [[("这不是 C++，是一门描述语言。", 20, True, INK)],
           [("gem5 编译时由 src/arch/isa_parser/ 生成真正的 C++ 类，"
             "所以改完必须重新编译。", 16, False, INK_SOFT)]], spacing=1.42)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "Rd、Rs1、Rs2 这些名字不是变量，是让生成器登记依赖关系的标记。"
           "谁被读、谁被写，全靠它们推断。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 07 §1.4 读-改-写
    s = T.blank(prs)
    y = T.head(s, "写 Rd 的指令，读不到 Rd", kicker="补课 1.4　陷阱", accent=ACC)

    T.code(s, M, y, Inches(5.9), [
        "// 想写累加：acc += a*b",
        "Rd = Rd + (a * b);",
        "//    ↑ 这个 Rd 读到的是 0",
    ], size=14, hi=(2,))

    T.code(s, Inches(6.94), y, Inches(5.64), [
        "// 正确：显式声明先读后写",
        "Rd_sd = Rd_sd + (a * b);",
        "//  ↑ 加 _sd 后缀，登记为读+写",
    ], size=14, fill="14332C", fg="CFE7DF", hi=(2,))

    T.txt(s, M, y + Inches(1.42), Inches(11.8), Inches(1.4),
          [[("生成器扫描代码，看到 Rd 在赋值号左边，就登记为「只写」。", 17, False, INK)],
           [("于是执行时给你一个未初始化的源操作数——每次迭代累加器都被清零。",
             17, False, INK)],
           [("程序不崩，结果全错。", 19, True, RED)]], spacing=1.46)

    T.txt(s, M, y + Inches(2.98), Inches(11.8), Inches(0.4),
          [[("依据：", 15, True, INK),
            ("src/arch/isa_parser/operand_list.py:74-75", 15, False, ACC, True)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "本次实验的 checksum 一票否决就是冲着这个坑来的：七行 checksum 有一行对不上，"
           "全卷作废。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 08 punch
    T.punch(prs,
            [("模拟器不会告诉你", False),
             ("你的指令算错了。", True),
             ("它只会照着你写的算，", False),
             ("然后给你一个很好看的加速比。", True)],
            sub="所以每一步都要先验证正确性，再看性能。checksum 先行。",
            accent=ACC)

    # ======================================================== 09 §1.5 OpClass
    s = T.blank(prs)
    y = T.head(s, "延迟不是猜的，是配的", kicker="补课 1.5", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["功能单元", "OpClass", "opLat", "口数", "本次实验"],
        ["IntALU", "IntAlu", "1", "6", "基线 addi/addw 走这里"],
        ["IntMultDiv", "IntMult", "3", "2", "基线 mulw 走这里"],
        ["IntMultDiv", "IntDiv", "20", "2", "—"],
        ["SIMD_Unit", "SimdMultAcc", "1", "4", "dotp8 挂这里"],
    ], col_w=[Inches(2.3), Inches(2.5), Inches(1.2), Inches(1.0), Inches(4.833)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1, 2, 3), hi_rows=(4,), hi_fill=DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("为什么不能挂 IntMult？", 20, True, INK)],
           [("基线的 mulw 也走 IntMult，ROI 内有 813,056 条。"
             "两者抢同一个口，测出来的差异分不清是新指令的功劳还是抢口的代价。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "SimdMultAcc 的 opLat 出厂是 1 拍。1 拍的乘加是不诚实的硬件——"
           "本次实验用 --dotp8-lat 把它改成 3 拍，与 IntMult 对齐。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 10 §1.6 .insn
    s = T.blank(prs)
    y = T.head(s, "怎么把这条指令写进 C 程序", kicker="补课 1.6", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        'asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2"',
        '             : "+r"(acc) : "r"(pa), "r"(pb));',
        '//              ↑ opcode  ↑f3 ↑f7   rd   rs1  rs2',
    ], size=14, hi=(1,))

    yc = y + Inches(1.40)
    cw = (CONTENT_W - Inches(0.36)) / 2
    for k, (ttl, a, b, col) in enumerate([
        ("0x0b：写 7 位", ".insn 是汇编器的伪指令，要的是完整 opcode，",
         "不是 decoder.isa 里的 OPCODE5。这里必须写 0x0b。", ACC),
        ('"+r"：读+写', 'acc 既是输入又是输出。写成 "=r"，编译器认为',
         "它只被写，会把之前的累加值优化掉。", RED),
    ]):
        xx = M + (cw + Inches(0.36)) * k
        T.card(s, xx, yc, cw, Inches(1.34),
               fill=RED_DIM if col == RED else PAPER_DIM)
        T.txt(s, xx + Inches(0.26), yc + Inches(0.16), cw - Inches(0.52),
              Inches(1.06),
              [[(ttl, 17.5, True, col)],
               [(a, 14, False, INK)],
               [(b, 14, False, INK)]], spacing=1.32)

    T.txt(s, M, y + Inches(2.90), Inches(11.8), Inches(0.46),
          [[("同一条指令，两处写编码，两处写法还不同。", 20, True, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "decoder.isa 填 0x02，内联汇编填 0x0b。写反了不会报错，"
           "只会安静地译成别的指令——所以任务四要求 objdump 逐位对照。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 11 §1.7 循环携带依赖
    s = T.blank(prs)
    y = T.head(s, "一个累加器，就是一条串行链", kicker="补课 1.7", accent=ACC)

    T.code(s, M, y, Inches(5.9), [
        "for (i = 0; i < n; i++)",
        "    acc = dotp8(acc, a[i], b[i]);",
        "//         ↑ 下一次要等上一次",
    ], size=14, hi=(2,))

    T.txt(s, Inches(6.94), y + Inches(0.04), Inches(5.64), Inches(1.4),
          [[("乱序核再宽也没用。", 18, True, RED)],
           [("链上每一环都要等前一环，", 14.5, False, INK)],
           [("总时间 = 迭代数 × 延迟。", 14.5, False, INK)]], spacing=1.34)

    yc = y + Inches(1.44)
    T.txt(s, M, yc, Inches(11.8), Inches(0.34),
          [[("拆成 4 个累加器：4 条独立链，可以并行", 17, True, INK)]])

    T.code(s, M, y + Inches(1.84), Inches(12.0), [
        "a0 = dotp8(a0, ...);  a1 = dotp8(a1, ...);",
        "a2 = dotp8(a2, ...);  a3 = dotp8(a3, ...);   /* 循环外再合并 */",
    ], size=13.5)

    T.txt(s, M, y + Inches(2.94), Inches(11.8), Inches(0.46),
          [[("这一步不改硬件，只改软件：3.03 倍 → 4.50 倍。", 20, True, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "拆累加器要付代价：多 3 个寄存器、多一段合并代码、循环体变长。"
           "陷阱三就是被这个代价咬到的。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 12 §1.8 取指块
    s = T.blank(prs)
    y = T.head(s, "取指是按 64 字节一块拿的", kicker="补课 1.8", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("O3 CPU 的 fetchBufferSize = 64 字节，且按 64 对齐。"
             "循环体跨过一条边界，每次迭代就要多取一次。", 16, False, INK)]])

    x0 = M + Inches(1.85)
    edge = x0 + Inches(7.94)

    yc = y + Inches(0.66)
    T.rect(s, x0, yc, Inches(7.94), Inches(0.34), PAPER_DIM)
    T.rect(s, edge + Inches(0.05), yc, Inches(1.95), Inches(0.34), "E3E6EA")
    T.txt(s, x0, yc + Inches(0.02), Inches(7.94), Inches(0.3),
          [("← 一个 64 字节取指块 →", 11.5, False, INK_SOFT)],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    T.txt(s, edge + Inches(0.05), yc + Inches(0.02), Inches(1.95), Inches(0.3),
          [("下一块", 11.5, False, INK_SOFT)],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    yb = y + Inches(1.28)
    for k, (nb, col, lab) in enumerate([
        (38, GREEN, "38 B　一次取完"),
        (60, GREEN, "60 B　一次取完"),
        (66, RED, "66 B　每次多取一趟"),
    ]):
        yy = yb + Inches(0.62) * k
        T.txt(s, M, yy, Inches(1.7), Inches(0.44),
              [(["dotp8x2", "dotp8x4c", "dotp8x4"][k], 13.5, True, INK, True)],
              align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        bytebar(s, x0, yy, nb, Inches(0.44), col, lab)
    T.line(s, edge, yb - Inches(0.42), edge, yb + Inches(1.72),
           color=RED, width=1.75, dash="dash")

    T.txt(s, M, y + Inches(3.44), Inches(11.8), Inches(0.78),
          [[("64 和 66，差两个字节。", 20, True, INK)],
           [("取指次数差 7.01 倍，前端阻塞差 6.86 倍。这是本次实验的陷阱三。",
             16, False, INK_SOFT)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 13 §02
    T.section(prs, "02", "先算账，再动手",
              "在写一行代码之前，先用纸笔算出这条指令的上限", accent=ACC)

    # ======================================================== 14 任务1 数内循环
    s = T.blank(prs)
    y = T.head(s, "先数清楚内循环有几条指令", kicker="任务 1", accent=ACC)

    T.code(s, M, y, Inches(6.1), [
        "10a80:  lb    a4,0(a5)     # 取 a[i]",
        "10a84:  lb    a3,0(a2)     # 取 b[i]",
        "10a88:  addi  a5,a5,1",
        "10a8c:  addi  a2,a2,1",
        "10a90:  mulw  a4,a4,a3     # 乘",
        "10a94:  addw  a0,a0,a4     # 加",
        "10a96:  bne   a5,a1,10a80",
    ], size=13, hi=(4, 5))

    T.txt(s, Inches(7.2), y + Inches(0.06), Inches(5.38), Inches(2.4),
          [[("7 条指令", 26, True, ACC)],
           [("换 1 次乘加。", 17, False, INK)],
           [("", 9, False, INK)],
           [("0x10a96 − 0x10a80 = 22 字节", 15, True, INK, True)],
           [("循环体 22 字节，取指块装得下。", 15, False, INK_SOFT)]],
          spacing=1.36)

    T.txt(s, M, y + Inches(2.72), Inches(11.8), Inches(0.86),
          [[("乘加次数 = 8 × 101,632 = 813,056", 19, True, INK, True)],
           [("内循环指令 = 813,056 × 7 = 5,691,392　→　占全程 98.104%",
             17, False, INK)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "98.104% 代入 Amdahl，理论上限是 52.8 倍。请把这个数字先写在纸上——"
           "第 8 问要用它跟实测的 3.08 倍对质。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 15 预测 vs 实测
    s = T.blank(prs)
    y = T.head(s, "指令数可以精确预测", kicker="任务 1", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("一条 dotp8 顶掉 lb/lb/mulw/addw 四条，留下 addi/addi/bne 三条，"
             "再加上一条 dotp8：7 → 7？不。", 16, False, INK)]])

    T.code(s, M, y + Inches(0.62), Inches(12.0), [
        "非循环部分 110,008  +  内循环 101,632 × 7  =  110,008 + 711,424  =  821,432",
    ], size=15)

    yc = y + Inches(1.62)
    T.stat(s, M, yc, Inches(3.7), "821,432", "纸上算出来的", color=INK, size=48)
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "821,432", "gem5 实测",
           color=GREEN, size=48)
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "0", "差多少条", color=ACC,
           size=48)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "动态指令数是可以手算的——它只跟程序有关。周期数不行，那是硬件的事。"
           "这条分界线是本次实验的主线。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 16 任务2 找空槽
    s = T.blank(prs)
    y = T.head(s, "32 个 OPCODE5，哪些还空着", kicker="任务 2", accent=ACC)

    ys = y + Inches(0.1)
    used = {0x00, 0x01, 0x03, 0x04, 0x05, 0x06, 0x08, 0x09, 0x0b, 0x0c,
            0x0d, 0x0e, 0x15, 0x18, 0x19, 0x1b, 0x1c, 0x1e}
    custom = {0x02: "c0", 0x0a: "c1", 0x16: "c2", 0x1e: "c3"}
    cell = Inches(0.68)
    gap = Inches(0.075)
    for v in range(32):
        cx = M + (cell + gap) * (v % 8)
        cy = ys + (cell + gap + Inches(0.06)) * (v // 8)
        if v in used:
            fill, fg = ("A62B5F", PAPER) if v == 0x1e else (INK, PAPER)
        elif v in custom:
            fill, fg = GREEN, PAPER
        else:
            fill, fg = PAPER_DIM, INK_SOFT
        T.rect(s, cx, cy, cell, cell, fill)
        T.txt(s, cx, cy, cell, cell,
              [("%02x" % v, 13.5, True, fg, True)],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if v in custom:
            T.txt(s, cx, cy + cell - Inches(0.02), cell, Inches(0.22),
                  [(custom[v], 10, True, RED if v == 0x1e else GREEN)],
                  align=PP_ALIGN.CENTER)

    xr = M + Inches(6.4)
    T.txt(s, xr, ys + Inches(0.04), Inches(5.4), Inches(2.6),
          [[("18 个已占，14 个空。", 20, True, INK)],
           [("", 9, False, INK)],
           [("■ 石墨 = 标准 RISC-V 已占用", 14, False, INK)],
           [("■ 青绿 = custom-0/1/2，可以用", 14, False, GREEN)],
           [("■ 洋红 = custom-3（0x1e），已被", 14, False, ACC)],
           [("　　 gem5 的 M5Op 伪指令占走了", 14, False, ACC)]], spacing=1.36)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "ROI_BEGIN() 汇编成 .long 0x8400007b —— 低 7 位 0x7b 正是 custom-3。"
           "占了它，你的 ROI 标记就失效。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 17 M5Op 冲突
    s = T.blank(prs)
    y = T.head(s, "为什么 custom-3 不能碰", kicker="任务 2　陷阱", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "// gem5 的伪指令：src/arch/riscv/isa/decoder.isa",
        "0x1e: M5Op::M5Op();          // custom-3 整片被它包了",
        "",
        "// 你的基准里每次都在用它",
        "ROI_BEGIN()  →  .long 0x8400007b   =  (0x42 << 25) | 0x7b",
    ], size=13.5, hi=(1, 4))

    T.txt(s, M, y + Inches(2.06), Inches(11.8), Inches(1.36),
          [[("占了 custom-3，会发生什么？", 20, True, INK)],
           [("m5_dump_stats 不再被识别，ROI 统计消失；或者更糟——"
             "你的 dotp8 被当成 M5Op 执行，程序莫名其妙退出。", 16, False, INK_SOFT)],
           [("这类冲突不报错，只表现为「数据不对」。", 17, True, RED)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "所以本次实验限定只能用 custom-0/1/2。学号尾号决定用哪一个，"
           "全班三种编码互不相同。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 18 punch
    T.punch(prs,
            [("编码空间是公共资源。", False),
             ("你占的每一格，", False),
             ("都是别人不能再用的。", True)],
            sub="真实芯片项目里，custom 槽的分配要过架构委员会。这不是形式主义。",
            accent=ACC)

    # ======================================================== 19 §03
    T.section(prs, "03", "动手：写译码器",
              "40 行 decoder.isa，一次编译 7 分钟", accent=ACC)

    # ======================================================== 20 参考实现
    s = T.blank(prs)
    y = T.head(s, "dotp8 的译码器长这样", kicker="任务 3", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "0x02: decode FUNCT3 {",
        "  0x0: decode FUNCT7 {",
        "    0x0: dotp8({{",
        "        int64_t acc = Rd_sd;              // 显式先读",
        "        for (int k = 0; k < 8; k++) {",
        "            int8_t a = (Rs1_ud >> (k*8)) & 0xff;",
        "            int8_t b = (Rs2_ud >> (k*8)) & 0xff;",
        "            acc += (int64_t)a * (int64_t)b;",
        "        }",
        "        Rd_sd = acc;                      // 再写回",
        "    }}, SimdMultAcc);",
        "} }",
    ], size=12.5, hi=(3, 9, 10))

    T.txt(s, M, y + Inches(4.06), Inches(11.8), Inches(0.44),
          [[("三处细节：", 17, True, INK),
            ("Rd_sd", 15, True, ACC, True),
            ("（读+写）、", 15, False, INK),
            ("_ud", 15, True, ACC, True),
            ("（按无符号取字节）、", 15, False, INK),
            ("SimdMultAcc", 15, True, ACC, True),
            ("（不是 IntAlu）。", 15, False, INK)]])
    T.foot(s, FOOT)

    # ======================================================== 21 写之前先回答
    s = T.blank(prs)
    y = T.head(s, "写之前，先回答三个问题", kicker="任务 3", accent=ACC)

    yc = y + Inches(0.06)
    for k, (q, a) in enumerate([
        ("八个字节是有符号的还是无符号的？",
         "qnn 的权重是 int8，必须有符号。取字节时用 _ud 避免符号扩展污染，"
         "取出来再强转 int8_t。"),
        ("累加器多宽？",
         "8 个 int8×int8 最大 8×16,384，远超 int16。用 int64_t 的 Rd_sd，"
         "与基线 C 代码的 int32 累加保持一致。"),
        ("为什么不是 8 条乘加，而是 1 条？",
         "指令数是省下来了，但延迟不会因此变成 1 拍。"
         "opLat 该给几拍，是任务 5 要回答的。"),
    ]):
        yy = yc + Inches(1.19) * k
        T.rect(s, M, yy + Inches(0.08), Inches(0.055), Inches(0.86), ACC)
        T.txt(s, M + Inches(0.3), yy, Inches(11.5), Inches(1.0),
              [[(q, 18, True, INK)],
               [(a, 14.5, False, INK_SOFT)]], spacing=1.4)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "这三个问题都答完再敲键盘。改完 decoder.isa 要重编 7 分钟，"
           "一次实验课编不了几轮。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 22 编码拆解
    s = T.blank(prs)
    y = T.head(s, "把机器码逐位拆开验证", kicker="任务 4", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.4),
          [[("objdump 印出来的这个数：", 16, False, INK),
            ("  0x00c6870b", 18, True, ACC, True)]])

    bitfield(s, M, y + Inches(0.62), CONTENT_W, Inches(0.66), [
        (7, "0000000", "funct7 = 0", INK, PAPER),
        (5, "01100", "rs2 = 12 (a2)", "3E4A57", PAPER),
        (5, "01101", "rs1 = 13 (a3)", "3E4A57", PAPER),
        (3, "000", "f3 = 0", INK, PAPER),
        (5, "01110", "rd = 14 (a4)", "3E4A57", PAPER),
        (7, "0001011", "opcode = 0x0b", ACC, PAPER),
    ], size=12, lab_size=11)

    T.txt(s, M, y + Inches(1.96), Inches(11.8), Inches(1.3),
          [[("为什么 objdump 印的是 .4byte 而不是 dotp8？", 20, True, INK)],
           [("因为反汇编器不认得它。gem5 认得（改了 decoder.isa），"
             "binutils 不认得（没改 opcodes/riscv-opc.c）。", 16, False, INK_SOFT)],
           [("这两个是两套独立的表。", 17, True, ACC)]], spacing=1.42)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "任务四要求把这六个字段全部拆出来并说明每一位的来源。"
           "拆错的人，多半是把 0x02 和 0x0b 写反了。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 23 checksum
    s = T.blank(prs)
    y = T.head(s, "七行 checksum，一行对不上就作废", kicker="任务 4", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("每个版本跑完都要打印一行 checksum。七个版本七行，必须完全相同。",
             17, False, INK)]])

    T.table(s, M, y + Inches(0.66), Inches(8.4), [
        ["版本", "checksum"],
        ["qnn（基线）", "一致"],
        ["qnn_dotp8", "一致"],
        ["qnn_dotp8u4 / x2 / x4 / x4c", "一致"],
    ], col_w=[Inches(5.0), Inches(3.4)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.48),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER])

    T.txt(s, Inches(9.6), y + Inches(0.72), Inches(2.98), Inches(1.9),
          [[("为什么这么狠？", 18, True, RED)],
           [("因为算错的版本", 14.5, False, INK)],
           [("跑得更快。", 14.5, True, RED)],
           [("累加器被清零的", 14.5, False, INK)],
           [("dotp8 少一条依赖链。", 14.5, False, INK)]], spacing=1.34)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "checksum 对不上或没贴出来 = 全卷作废。性能数据再漂亮也不看。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 24 §04
    T.section(prs, "04", "六个版本，一张主表",
              "同一条指令，六种用法。三个陷阱都藏在这张表里", accent=ACC)

    # ======================================================== 25 主表
    s = T.blank(prs)
    y = T.head(s, "主表", kicker="任务 6　--cpu o3 --dotp8-lat 3", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["版本", "循环体", "动态指令", "周期", "指令比", "加速比", "IPC"],
        ["qnn（基线）", "22 B", "5,801,400", "1,099,949", "1.00", "1.00", "5.274"],
        ["qnn_dotp8", "18 B", "821,432", "356,625", "7.06", "3.08", "2.303"],
        ["qnn_dotp8u4", "66 B", "561,608", "363,387", "10.33", "3.03", "1.545"],
        ["qnn_dotp8x2", "38 B", "682,232", "259,087", "8.50", "4.25", "2.633"],
        ["qnn_dotp8x4", "66 B", "574,216", "290,047", "10.10", "3.79", "1.980"],
        ["qnn_dotp8x4c", "60 B", "517,880", "244,335", "11.20", "4.50", "2.120"],
    ], col_w=[Inches(2.6), Inches(1.3), Inches(2.0), Inches(1.9),
              Inches(1.4), Inches(1.4), Inches(1.233)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.42),
        mono_cols=(1, 2, 3, 4, 5, 6), hi_rows=(6,), hi_fill=DIM)

    T.note(s, M, y + Inches(3.30), CONTENT_W,
           "指令比一路涨到 11.20，加速比却在 3.03 和 4.50 之间来回摆。"
           "接下来三张片子，就讲这两列为什么对不上。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 26 陷阱一
    s = T.blank(prs)
    y = T.head(s, "指令少 7.06 倍，只快 3.08 倍", kicker="陷阱一", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "加速比  =  指令比  ×  ( 新 IPC / 旧 IPC )",
        "  3.08  =   7.06   ×  (  2.303 / 5.274  )   =  7.06 ÷ 2.29",
    ], size=16, hi=(1,))

    yc = y + Inches(1.24)
    T.stat(s, M, yc, Inches(3.7), "7.06×", "指令少了这么多", color=GREEN,
           size=52)
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "2.29×", "IPC 也掉了这么多",
           color=RED, size=52)
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "3.08×", "剩下这么多",
           color=INK, size=52)

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(0.5),
          [[("IPC 掉下来不是坏事——那 7 条指令里有 6 条本来就是空转的开销。",
             17, False, INK)]])

    T.note(s, M, y + Inches(3.52), CONTENT_W,
           "把指令数当性能，是本次实验第一个也是最常见的错误。"
           "报告里只写「指令少了 86%」而不给周期数的，D 部分直接扣。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 27 两条常数线
    s = T.blank(prs)
    y = T.head(s, "有两样东西一直没变", kicker="陷阱一", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["版本", "L1D MSHR 缺失", "分支预测错误", "周期"],
        ["qnn", "12,823", "1,445", "1,099,949"],
        ["qnn_dotp8", "12,823", "1,443", "356,625"],
        ["qnn_dotp8x2", "12,812", "1,394", "259,087"],
        ["qnn_dotp8x4c", "12,819", "1,404", "244,335"],
    ], col_w=[Inches(3.2), Inches(3.0), Inches(2.8), Inches(2.833)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1, 2, 3))

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("换指令不改变要读多少数据，也不改变要跳多少次。", 20, True, INK)],
           [("dotp8 把八次乘加压成一条，但那八个字节还是要从内存里搬进来。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "这两列恒定，正好把嫌疑范围缩到两处：依赖链（后端）和取指（前端）。"
           "陷阱二、陷阱三各占一处。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 28 punch
    T.punch(prs,
            [("少掉的指令，", False),
             ("不是免费变成时间的。", True),
             ("它先要经过 IPC 这道汇率。", False)],
            sub="加速比 = 指令比 × IPC 比。三个数只要报两个，第三个就能被验算出来。",
            accent=ACC)

    # ======================================================== 29 陷阱二
    s = T.blank(prs)
    y = T.head(s, "同样展开 4 次，差了 1.5 倍", kicker="陷阱二", accent=ACC)

    T.code(s, M, y, Inches(5.9), [
        "/* u4：展开，但只有 1 个累加器 */",
        "acc = dotp8(acc, ...);   /* 4 次 */",
        "acc = dotp8(acc, ...);   /* 串成一条链 */",
    ], size=13, hi=(2,))

    T.code(s, Inches(6.94), y, Inches(5.64), [
        "/* x4：展开 + 4 个累加器 */",
        "a0 = dotp8(a0, ...);  a1 = dotp8(a1, ...);",
        "a2 = dotp8(a2, ...);  a3 = dotp8(a3, ...);",
    ], size=13, fill="14332C", fg="CFE7DF", hi=(1, 2))

    yc = y + Inches(1.42)
    hbars(s, M, yc, Inches(11.8), [
        ("u4  加速比", 3.03, RED, "3.03×　363,387 周期"),
        ("x4  加速比", 3.79, ACC, "3.79×　290,047 周期"),
        ("x4c 加速比", 4.50, GREEN, "4.50×　244,335 周期"),
    ], bar_h=Inches(0.42), gap=Inches(0.20), label_w=Inches(1.95),
        val_w=Inches(2.9))

    T.txt(s, M, y + Inches(3.42), Inches(11.8), Inches(0.5),
          [[("u4 的指令比 10.33，比 dotp8 的 7.06 高得多，加速比却更低。",
             17, False, INK)]])

    T.note(s, M, y + Inches(3.98), CONTENT_W,
           "展开只减少循环开销，不解开依赖链。链没解开，展开就是白展。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 30 依赖链下界
    s = T.blank(prs)
    y = T.head(s, "依赖链给出的时间下界", kicker="陷阱二", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.42),
          [[("内循环共 101,632 次迭代，dotp8 延迟 3 拍。"
             "链上的迭代数 × 3，就是这个版本再快也快不过的下界。",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.6), CONTENT_W, [
        ["版本", "累加器", "链长（迭代）", "下界（拍）", "实测周期", "下界占比"],
        ["qnn_dotp8", "1", "101,632", "304,896", "356,625", "85.5%"],
        ["qnn_dotp8x2", "2", "50,816", "152,448", "259,087", "58.8%"],
        ["qnn_dotp8x4c", "4", "25,408", "76,224", "244,335", "31.2%"],
    ], col_w=[Inches(2.7), Inches(1.4), Inches(2.1), Inches(2.0),
              Inches(2.0), Inches(1.633)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.48),
        mono_cols=(1, 2, 3, 4, 5), hi_rows=(1,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.72), Inches(11.8), Inches(0.82),
          [[("85.5% 的时间，机器在等上一次的结果。", 20, True, RED)],
           [("这时候把 ROB、IQ、发射宽度全加大也没用——实验四已经试过了。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "下界占比降到 31.2% 之后，瓶颈就不在依赖链上了。它搬到了别处。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 31 延迟扫描
    s = T.blank(prs)
    y = T.head(s, "把硬件变慢，看谁先扛不住",
               kicker="任务 6　--vary dotp8-lat", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["opLat", "dotp8（1 累加器）", "dotp8x2（2 个）", "dotp8x4c（4 个）"],
        ["1", "245,970", "255,435", "244,762"],
        ["2", "272,865", "256,733", "244,824"],
        ["3", "356,625", "259,087", "244,335"],
        ["4", "473,027", "283,228", "250,968"],
        ["6", "668,806", "366,123", "263,270"],
        ["8", "793,122", "452,910", "285,708"],
        ["1 → 8 变慢", "3.22×", "1.77×", "1.17×"],
    ], col_w=[Inches(2.4), Inches(3.2), Inches(3.1), Inches(3.133)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.38),
        mono_cols=(0, 1, 2, 3), hi_rows=(3, 8), hi_fill=DIM)

    T.note(s, M, y + Inches(3.34), CONTENT_W,
           "lat=3 这一行必须与主表逐位相同——这是你自己数据的自洽检查点。"
           "对不上，说明两次跑的不是同一个二进制。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 32 lat=1
    s = T.blank(prs)
    y = T.head(s, "把硬件调到 1 拍，三个版本一样快", kicker="陷阱二", accent=ACC)

    yc = y + Inches(0.12)
    hbars(s, M, yc, Inches(11.8), [
        ("lat = 1", 245970, INK_SOFT, "三版极差 4.3%"),
        ("lat = 3", 356625, ACC, "三版极差 45.9%"),
        ("lat = 8", 793122, RED, "三版极差 3.2 倍"),
    ], bar_h=Inches(0.44), gap=Inches(0.24), label_w=Inches(1.7),
        val_w=Inches(2.6))

    T.txt(s, M, y + Inches(2.26), Inches(11.8), Inches(1.24),
          [[("硬件越快，软件写法越不重要。", 21, True, INK)],
           [("反过来说：硬件的延迟藏在哪里，软件就得在哪里下功夫。",
             17, False, INK)],
           [("而真实加速器的延迟从来不是 1 拍。", 18, True, ACC)]], spacing=1.42)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "所以 opLat 出厂值 1 是个陷阱：不改它，你会得出「软件怎么写都一样」"
           "的错误结论。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 33 punch
    T.punch(prs,
            [("硬件只做了一次。", False),
             ("软件做了六次，", False),
             ("拿走了 1.49 倍。", True)],
            sub="同一条 dotp8：最差写法 3.03 倍，最好写法 4.50 倍。这就是软硬件协同。",
            accent=ACC)

    # ======================================================== 34 陷阱三
    s = T.blank(prs)
    y = T.head(s, "多两个字节，慢 15.76%", kicker="陷阱三", accent=ACC)

    x0 = M + Inches(2.2)
    edge = x0 + Inches(7.94)
    yc = y + Inches(0.14)
    T.rect(s, x0, yc, Inches(7.94), Inches(0.32), PAPER_DIM)
    T.rect(s, edge + Inches(0.05), yc, Inches(1.55), Inches(0.32), "E3E6EA")
    T.txt(s, x0, yc, Inches(7.94), Inches(0.32),
          [("← 64 字节取指块 →", 11.5, False, INK_SOFT)],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    for k, (nm, nb, col, lab) in enumerate([
        ("qnn_dotp8x4", 66, RED, "66 B　跨界"),
        ("qnn_dotp8x4c", 60, GREEN, "60 B　不跨界"),
    ]):
        yy = yc + Inches(0.62) + Inches(0.66) * k
        T.txt(s, M, yy, Inches(2.05), Inches(0.46),
              [(nm, 13.5, True, INK, True)],
              align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        bytebar(s, x0, yy, nb, Inches(0.46), col, lab)
    T.line(s, edge, yc - Inches(0.1), edge, yc + Inches(1.86),
           color=RED, width=1.75, dash="dash")

    T.table(s, M, y + Inches(2.24), CONTENT_W, [
        ["指标", "x4（66 B）", "x4c（60 B）", "变化"],
        ["动态指令", "574,216", "517,880", "−9.81%"],
        ["周期", "290,047", "244,335", "−15.76%"],
        ["取指访问缓存行", "62,265", "8,884", "÷ 7.01"],
        ["前端取指阻塞（拍）", "124,564", "18,160", "÷ 6.86"],
    ], col_w=[Inches(4.0), Inches(2.7), Inches(2.7), Inches(2.433)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.4),
        mono_cols=(1, 2, 3), hi_rows=(4,), hi_fill=DIM)
    T.foot(s, FOOT)

    # ======================================================== 35 两个字节多少钱
    s = T.blank(prs)
    y = T.head(s, "这两个字节，值多少", kicker="陷阱三", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "主循环迭代数  =  8 × (128 × 24 + 10 × 4)  =  24,896",
        "多出来的取指  =  (62,265 − 8,884) / 24,896  =  2.14  次 / 迭代",
    ], size=15, hi=(1,))

    yc = y + Inches(1.30)
    T.stat(s, M, yc, Inches(3.7), "6 B", "循环体缩短了", color=INK, size=52)
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "2.14", "每迭代少取指（次）",
           color=GREEN, size=52)
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "15.76%", "周期直接省下",
           color=ACC, size=52)

    T.txt(s, M, y + Inches(2.92), Inches(11.8), Inches(0.5),
          [[("x4c 做的事：把合并累加器的四条指令挪到循环外，循环体从 66 B 缩到 60 B。",
             17, False, INK)]])

    T.note(s, M, y + Inches(3.58), CONTENT_W,
           "指令数只少了 9.81%，周期却少了 15.76%——多出来的那部分，全是前端省下来的。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 36 稀释与放大
    s = T.blank(prs)
    y = T.head(s, "同一个开销，占比翻了 35 倍", kicker="陷阱三", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["版本", "总周期", "前端取指阻塞", "占比"],
        ["qnn（基线）", "1,099,949", "13,498", "1.2%"],
        ["qnn_dotp8", "356,625", "13,478", "3.8%"],
        ["qnn_dotp8x4（66 B）", "290,047", "124,564", "42.9%"],
        ["qnn_dotp8x4c（60 B）", "244,335", "18,160", "7.4%"],
    ], col_w=[Inches(4.2), Inches(2.6), Inches(2.9), Inches(2.133)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.5),
        mono_cols=(1, 2, 3), hi_rows=(3,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("基线里 1.2% 的东西，不值得看一眼。", 20, True, INK)],
           [("把计算削掉 86% 之后，它成了主角——这是 Amdahl 定律的第二幕。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "加速一个部分，等于放大其余所有部分的占比。每优化一轮，都要重新找一次瓶颈。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 37 打地鼠
    s = T.blank(prs)
    y = T.head(s, "瓶颈搬了四次家", kicker="小结", accent=ACC)

    steps = [
        ("基线 qnn", "后端算力", "813,056 次乘加占满乘法器", RED),
        ("+ dotp8", "依赖链", "85.5% 的时间在等上一次", RED),
        ("+ 4 个累加器", "前端取指", "循环体 66 B，跨取指块", RED),
        ("+ 循环体对齐", "访存队列", "LQ 满 85,131 次 → 实验六", ACC),
    ]
    cw = (CONTENT_W - Inches(0.72)) / 4
    for k, (act, bn, why, col) in enumerate(steps):
        xx = M + (cw + Inches(0.24)) * k
        T.txt(s, xx, y, cw, Inches(0.34),
              [(act, 14, True, INK_SOFT)], align=PP_ALIGN.CENTER)
        T.rect(s, xx, y + Inches(0.42), cw, Inches(1.5),
               RED_DIM if col == RED else DIM)
        T.txt(s, xx + Inches(0.16), y + Inches(0.58), cw - Inches(0.32),
              Inches(1.2),
              [[(bn, 19, True, col)],
               [(why, 13, False, INK)]], spacing=1.36,
              align=PP_ALIGN.CENTER)
        if k < 3:
            T.txt(s, xx + cw - Inches(0.08), y + Inches(0.9),
                  Inches(0.4), Inches(0.4), [("→", 17, True, INK_SOFT)],
                  align=PP_ALIGN.CENTER)

    T.txt(s, M, y + Inches(2.34), Inches(11.8), Inches(1.24),
          [[("每一步都是对的，每一步都换来新瓶颈。", 21, True, INK)],
           [("实验四打的是核内的地鼠，本次打的是 ISA 和前端的地鼠，"
             "实验六要打的是访存的地鼠。", 17, False, INK_SOFT)]], spacing=1.46)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "所以性能优化没有「做完」这个状态，只有「当前瓶颈在哪」。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 38 punch
    T.punch(prs,
            [("加速器不是加上去就有用的。", False),
             ("它把瓶颈推给了下一个人：", False),
             ("先是编译器，再是取指，", False),
             ("最后是内存。", True)],
            sub="本次实验走完了前两站。第三站是实验六。",
            accent=ACC)

    # ======================================================== 39 §05
    T.section(prs, "05", "软件拿走多少，硬件拿走多少",
              "任务 7 与思考题：把这次实验的账算清楚", accent=ACC)

    # ======================================================== 40 问题1
    s = T.blank(prs)
    y = T.head(s, "硬件做了一次，软件做了六次", kicker="任务 7", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "最差软件 / 最好软件  =  363,387 / 244,335  =  1.49 倍",
    ], size=16, hi=(0,))

    yc = y + Inches(0.96)
    T.stat(s, M, yc, Inches(3.7), "1", "硬件改了几次", color=INK, size=52,
           sub="一条 dotp8，opLat 3 拍")
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "6", "软件写了几个版本",
           color=INK, size=52, sub="u4 / x2 / x4 / x4c …")
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "1.49×", "软件独自拿到的",
           color=ACC, size=52, sub="同一份 gem5，同一条指令")

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(0.5),
          [[("如果只写一个版本就交报告，你会漏掉这 1.49 倍，"
             "并且不知道自己漏了。", 17, False, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "判的是对照，不是最大值。只报一个「我拿到了 4.5 倍」而没有横向对比的报告，"
           "D 部分不超过 15 分。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 41 问题2
    s = T.blank(prs)
    y = T.head(s, "硬件变差，谁受伤最重", kicker="任务 7", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["软件写法", "opLat = 3", "opLat = 6", "变慢"],
        ["dotp8（1 累加器）", "356,625", "668,806", "+87.5%"],
        ["dotp8x2（2 累加器）", "259,087", "366,123", "+41.3%"],
        ["dotp8x4c（4 累加器）", "244,335", "263,270", "+7.7%"],
    ], col_w=[Inches(4.2), Inches(2.7), Inches(2.7), Inches(2.233)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1, 2, 3), hi_rows=(3,), hi_fill=GREEN_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("好软件同时也是保险。", 20, True, INK)],
           [("硬件延迟翻倍，单累加器版本被打回原形，四累加器版本只掉 7.7%。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "换句话说：软件把依赖链拆开之后，硬件延迟就被乱序执行吸收掉了。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 42 punch
    T.punch(prs,
            [("慢硬件 + 好软件  =  1.64 倍", False),
             ("快硬件 + 差软件  =  3.03 倍", False),
             ("快硬件 + 好软件  =  4.50 倍", True)],
            sub="lat=6 单累加器 668,806 拍；lat=3 四累加器 244,335 拍。"
                "同一颗芯片，差 2.74 倍。",
            accent=ACC)

    # ======================================================== 43 下一站
    s = T.blank(prs)
    y = T.head(s, "最快的版本，卡在哪", kicker="任务 7　思考题 3", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["资源", "qnn（基线）", "qnn_dotp8x4c", "说明"],
        ["ROB 满", "0", "0", "重排序缓冲从来不是瓶颈"],
        ["IQ 满", "71,028", "32,025", "降了一半以上"],
        ["LQ 满", "207,625", "85,131", "仍然是最大的一项"],
    ], col_w=[Inches(2.2), Inches(2.4), Inches(2.6), Inches(4.633)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.5),
        mono_cols=(1, 2), hi_rows=(3,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.76), Inches(11.8), Inches(0.86),
          [[("再加一条 dotp16 有用吗？没有。", 20, True, INK)],
           [("dotp16 减少的是计算指令，而现在排队的是 load。"
             "要动的是搬数据的方式——那是实验六的 DMA。", 16, False, INK_SOFT)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.68), CONTENT_W,
           "思考题 3 第 6 问留空的，E 部分不超过 5 分。这一问是通向实验六的桥。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 44 可复现性
    s = T.blank(prs)
    y = T.head(s, "你的数字和参考解答不会一样", kicker="附录 B0", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.42),
          [[("SE 模式是确定性的，但「同一条命令」包含的东西比你想的多。",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.58), CONTENT_W, [
        ["变量", "对周期数的影响", "对指令数的影响", "对比值的影响"],
        ["argv[0] 路径长度", "极差 36（0.015%）", "无", "无"],
        ["随机种子（学号）", "极差 0.303%", "极差恰好 34 条", "无"],
        ["重新编译", "同量级", "无", "无"],
    ], col_w=[Inches(3.2), Inches(3.1), Inches(2.9), Inches(2.633)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.48),
        mono_cols=(1, 2))

    T.txt(s, M, y + Inches(2.66), Inches(11.8), Inches(0.86),
          [[("所以判分只看比值和三位有效数字。", 20, True, INK)],
           [("指令比 7.06 在三个种子下一致到小数点后两位；"
             "cycles 差 <0.3%、insts 差 ±50 之内都算对。", 16, False, INK_SOFT)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "唯一的「逐位相同」硬要求：你自己的主表与延迟扫描表在 lat=3 那一列必须一致。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 45 判分
    s = T.blank(prs)
    y = T.head(s, "分怎么给", kicker="评分", accent=ACC)

    T.table(s, M, y, Inches(7.3), [
        ["部分", "内容", "分"],
        ["A", "任务 1：算账与预测", "15"],
        ["B", "任务 2–4：写译码器并验证", "20"],
        ["C", "任务 5：功能单元与延迟", "5"],
        ["D", "任务 6：六版对照与三个陷阱", "40"],
        ["E", "任务 7 与思考题", "10"],
        ["Q", "过程记录与可复现性", "10"],
        ["F / G", "附加分 / 反向扣分", "+10 / −10"],
    ], col_w=[Inches(1.1), Inches(4.9), Inches(1.3)],
        head_fill=INK, size=13, head_size=12.5, row_h=Inches(0.38),
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
        hi_rows=(4,), hi_fill=DIM)

    xr = Inches(8.5)
    T.txt(s, xr, y, Inches(4.08), Inches(0.34),
          [[("五条一票否决", 19, True, RED)]])
    T.bullets(s, xr, y + Inches(0.46), Inches(4.08), [
        [("七行 checksum 对不上或没贴 → 全卷作废", 13.5, False, INK)],
        [("任务 1 第 7 问事后补填 → A ≤ 8", 13.5, False, INK)],
        [("任务 4 的 diff 没贴 → B4 记 0", 13.5, False, INK)],
        [("只报最大加速比、不做对照 → D ≤ 15", 13.5, False, INK)],
        [("思考题 3 第 6 问留空 → E ≤ 5", 13.5, False, INK)],
    ], size=13.5, gap=Inches(0.58), marker=RED, marker_size=Inches(0.11))

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "D 占 40 分，全在对照上。六个版本缺一个，这 40 分就拿不满。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 46 一页纸
    s = T.blank(prs, dark=True)
    T.txt(s, M, Inches(0.85), CONTENT_W, Inches(0.44),
          [("实验五　一页纸", 15, True, ACC)])
    T.txt(s, M, Inches(1.32), CONTENT_W, Inches(0.72),
          [("带走这五句", 36, True, PAPER)])

    lines = [
        ("加速比 = 指令比 × IPC 比。", "指令少 7.06 倍，IPC 掉 2.29 倍，只快 3.08 倍。"),
        ("延迟不是猜的，是配的。", "opLat 出厂值 1 拍会给你一个假的加速比，必须显式设成 3。"),
        ("软件能独自拿走 1.49 倍。", "同一条 dotp8：最差 3.03 倍，最好 4.50 倍。"),
        ("两个字节能值 15.76%。", "循环体 66 B 跨取指块，取指次数变 7.01 倍。"),
        ("瓶颈会搬家，而且不止一次。", "算力 → 依赖链 → 前端 → 访存。最后一站是实验六。"),
    ]
    yy = Inches(2.42)
    for k, (a, b) in enumerate(lines):
        yl = yy + Inches(0.82) * k
        T.rect(s, M, yl + Inches(0.08), Inches(0.05), Inches(0.5), ACC)
        T.txt(s, M + Inches(0.3), yl, Inches(11.4), Inches(0.72),
              [[(a, 18, True, PAPER)],
               [(b, 13.5, False, WHITE_DIM)]], spacing=1.34)

    T.txt(s, M, SLIDE_H - Inches(0.95), CONTENT_W, Inches(0.4),
          [("下一次：实验六　把数据搬过去——DMA 与访存瓶颈", 13, False, WHITE_DIM)])

    return prs


if __name__ == "__main__":
    prs = build()
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    print("wrote %s  (%d slides)" % (out, len(prs.slides._sldIdLst)))
