# -*- coding: utf-8 -*-
"""实验六《软硬件协同 II：加速器集成》讲课用 PPT。

    python _tools/ppt/lab6.py            → labs/lab6/幻灯片.pptx

所有数字来自 labs/lab6/参考解答.md，改数据请同步改那一处。
主表口径：--cpu o3 --accel-port l2bus --accel-pe 32 --accel-outstanding 8
--accel-batch 1，seed 0x01352505（--bench-args "8 0x01352505"）。
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
                   "..", "..", "labs", "lab6", "幻灯片.pptx")

ACC = T.LAB_ACCENT[6]          # 翠绿
DIM = "DCEBE2"                 # 翠绿的浅色（表格高亮行用）
FOOT = "实验六　软硬件协同 II：加速器集成"


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


# ------------------------------------------------------------------ Roofline
def roofline(slide, x, y, w, h, peak, roofs, pts,
             imax=4.4, ymax=36.0, xticks=(1, 2, 3, 4), yticks=(8, 16, 24, 32)):
    """Roofline 图：横轴算术强度（MAC/B），纵轴实际算力（MAC/拍）。

    roofs = [(名字, 实测带宽 B/拍, 颜色), ...]
    pts   = [(标签, I, MAC/拍, 颜色, 标签放右?, 纵向偏移英寸), ...]

    斜坡的名字走图例，不贴在拐点上——两条拐点挨得近，贴上去会和屋顶线叠字。
    """
    def px(i):
        return x + int(w * min(i, imax) / imax)

    def py(v):
        return y + h - int(h * min(v, ymax) / ymax)

    for t in yticks:
        T.line(slide, x, py(t), x + w, py(t), color="E6E9ED", width=0.75)
        T.txt(slide, x - Inches(0.58), py(t) - Inches(0.13), Inches(0.5),
              Inches(0.26), [(str(t), 10.5, False, INK_SOFT, True)],
              align=PP_ALIGN.RIGHT)
    for t in xticks:
        T.txt(slide, px(t) - Inches(0.3), y + h + Inches(0.05), Inches(0.6),
              Inches(0.26), [(str(t), 10.5, False, INK_SOFT, True)],
              align=PP_ALIGN.CENTER)

    T.line(slide, x, y, x, y + h, color=INK_SOFT, width=1.0)
    T.line(slide, x, y + h, x + w, y + h, color=INK_SOFT, width=1.0)

    # 算力屋顶
    T.line(slide, x, py(peak), x + w, py(peak), color=INK, width=2.0)
    T.txt(slide, x + w - Inches(2.5), py(peak) - Inches(0.32), Inches(2.44),
          Inches(0.28), [("算力屋顶 %d MAC/拍" % peak, 11, True, INK)],
          align=PP_ALIGN.RIGHT)

    # 带宽斜坡
    for nm, bw, col in roofs:
        istar = peak / float(bw)
        T.line(slide, x, py(0), px(istar), py(peak), color=col, width=2.5)

    # 图例放在右下角的空白区
    lx, ly = px(2.75), py(11)
    for k, (nm, bw, col) in enumerate(roofs):
        yy = ly + Inches(0.36) * k
        T.rect(slide, lx, yy + Inches(0.05), Inches(0.17), Inches(0.17), col)
        T.txt(slide, lx + Inches(0.28), yy, Inches(2.4), Inches(0.28),
              [(nm, 11.5, True, col)])

    for lab, i, v, col, right, dy in pts:
        cx, cy = px(i), py(v)
        T.rect(slide, cx - Inches(0.07), cy - Inches(0.07),
               Inches(0.14), Inches(0.14), col, MSO_SHAPE.OVAL)
        if right:
            T.txt(slide, cx + Inches(0.14), cy - Inches(0.14) + dy,
                  Inches(2.2), Inches(0.28), [(lab, 10.5, True, col, True)])
        else:
            T.txt(slide, cx - Inches(2.34), cy - Inches(0.14) + dy,
                  Inches(2.2), Inches(0.28), [(lab, 10.5, True, col, True)],
                  align=PP_ALIGN.RIGHT)

    T.txt(slide, x, y + h + Inches(0.30), w, Inches(0.26),
          [("算术强度 I（MAC / 字节）", 11, False, INK_SOFT)],
          align=PP_ALIGN.CENTER)
    return y + h + Inches(0.62)


def build():
    prs = T.new_deck()

    # ======================================================== 00 封面
    T.cover(prs, 6,
            "软硬件协同 II：\n加速器集成",
            "核心问题：加速器该做多快，何时访存成为瓶颈\n"
            "整层搬到硬件后快 11.66 倍；再把它做宽一倍，只快了 0.008%",
            "计算机系统综合设计实验　·　4 学时　·　写一个 MMIO 加速器")

    # ======================================================== 01 立题
    T.punch(prs,
            [("把一层搬到硬件上，很容易。", False),
             ("搬对，很难。", True),
             ("本次实验会连错三次：", False),
             ("checksum、瓶颈、和数据的来源。", True)],
            sub="少一条 fence 会算错；pe 翻倍纹丝不动；"
                "而挂在内存总线上的加速器，一次都没读过内存。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "本次实验要做的决策", kicker="任务", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("实验五往 CPU 里加了一条指令。本次把一整层挪出 CPU，"
             "然后回答四个问题——", 17, False, INK)]])

    cw = (CONTENT_W - Inches(0.9)) / 4
    yc = y + Inches(0.66)
    for k, (ttl, body) in enumerate([
        ("挂在哪里", "L2 总线还是内存总线，最多差 21.6%"),
        ("做多宽", "pe 从 8 开到 64，最后 0.008%"),
        ("一次搬多少", "batch=2 最快，batch=8 反而更慢"),
        ("剩下的谁干", "CPU 占 68.5%，天花板 19.58 倍"),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, yc, cw, Inches(1.42))
        T.txt(s, xx + Inches(0.22), yc + Inches(0.24), cw - Inches(0.44),
              Inches(1.0),
              [[(ttl, 17, True, ACC)],
               [(body, 13.5, False, INK)]], spacing=1.4)

    T.txt(s, M, y + Inches(2.34), Inches(11.8), Inches(1.0),
          [[("问：加速器要做到多大才够？", 21, True, INK)],
           [("本次实验的答案是「早就够了」。决定性能的是它挂在哪，"
             "以及旁边那颗没被卸载的 CPU。", 17, False, INK_SOFT)]], spacing=1.42)

    T.note(s, M, y + Inches(3.36), CONTENT_W,
           "本次实验要新增一个 SimObject、给 RISC-V TLB 打补丁，并重新编译。"
           "一次约 2 分 53 秒（-j8）。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 03 §01
    T.section(prs, "01", "一个加速器要过几道关",
              "在跑出第一个正确的 checksum 之前，先把关卡和算账的公式说清楚",
              accent=ACC)

    # ======================================================== 04 §1.1 MMIO
    s = T.blank(prs)
    y = T.head(s, "加速器长什么样：七个寄存器", kicker="补课 1.1", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["偏移", "寄存器", "方向", "语义"],
        ["0x00", "A", "CPU 写", "输入向量基地址"],
        ["0x08", "B", "CPU 写", "权重矩阵基地址"],
        ["0x10", "OUT", "CPU 写", "输出基地址"],
        ["0x18", "DIMS", "CPU 写", "(rows << 32) | n"],
        ["0x20", "GO", "CPU 写", "写入即启动，本身不阻塞"],
        ["0x28", "STATUS", "CPU 读", "读会阻塞，直到这一批算完"],
        ["0x30", "BATCH", "CPU 写", "一次处理几个样本"],
    ], col_w=[Inches(1.2), Inches(1.6), Inches(1.6), Inches(7.433)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.42),
        mono_cols=(0, 1, 3), hi_rows=(6,), hi_fill=DIM)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "基址 0x4000_0000。这段地址不在内存里，它落在加速器上——"
           "但 CPU 眼里它和一块内存没区别。麻烦从这里开始。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 05 §1.2 三道关卡
    s = T.blank(prs)
    y = T.head(s, "CPU 和加速器之间隔着三层", kicker="补课 1.2", accent=ACC)

    cw = (CONTENT_W - Inches(0.6)) / 3
    for k, (no, nm, bad, fix, col) in enumerate([
        ("① ", "数据缓存", "CPU 写的 GO 停在 L1D 里，\n加速器根本看不见",
         "Request::UNCACHEABLE", ACC),
        ("② ", "乱序投机", "o3 提前把 STATUS 读回来，\n那时还没开始算",
         "Request::STRICT_ORDER", ACC),
        ("③ ", "内存模型", "RVWMO 允许写 GO 和读 STATUS\n换个次序发出去",
         "fence ow, ir", RED),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, y, cw, Inches(2.06),
               fill=RED_DIM if col == RED else PAPER_DIM)
        T.txt(s, xx + Inches(0.22), y + Inches(0.2), cw - Inches(0.44),
              Inches(1.5),
              [[(no, 17, True, col, True), (nm, 18, True, col)],
               [(bad.replace("\n", " "), 13.5, False, INK)]], spacing=1.4)
        T.txt(s, xx + Inches(0.22), y + Inches(1.54), cw - Inches(0.44),
              Inches(0.34), [(fix, 13, True, INK, True)])

    T.txt(s, M, y + Inches(2.30), Inches(11.8), Inches(0.9),
          [[("前两层是 gem5 的默认行为，可以用标志关掉。", 20, True, INK)],
           [("第三层不行——它是 RISC-V 体系结构允许的重排，"
             "只能靠程序自己插一条指令。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "三层里漏掉任何一层，checksum 都会变成 0x7a2b4200。三个 bug 长得一模一样。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 06 §1.3 TLB 补丁
    s = T.blank(prs)
    y = T.head(s, "两个标志，各防一件事", kicker="补课 1.3", accent=ACC)

    T.code(s, M, y, Inches(6.5), [
        "// src/arch/riscv/tlb.cc",
        "if (isDeviceAddr(paddr)) {",
        "    req->setFlags(Request::UNCACHEABLE |",
        "                  Request::STRICT_ORDER);",
        "}",
    ], size=13.5, hi=(2, 3))

    T.txt(s, Inches(7.5), y + Inches(0.02), Inches(5.08), Inches(1.9),
          [[("UNCACHEABLE", 17, True, ACC, True)],
           [("这段地址不许进 Cache，每次访问都真的走出去。",
             14, False, INK)],
           [("", 8, False, INK)],
           [("STRICT_ORDER", 17, True, ACC, True)],
           [("不许投机、不许提前发射。", 14, False, INK)],
           [("src/cpu/o3/lsq_unit.cc:1341", 12, False, INK_SOFT, True)]],
          spacing=1.32)

    T.txt(s, M, y + Inches(2.10), Inches(11.8), Inches(0.86),
          [[("没有这个补丁，两个 CPU 都算错。", 20, True, INK)],
           [("而且错得很整齐：checksum 都是 0x7a2b4200，"
             "accel.jobs 都是 0——加速器一次都没启动过。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "MMIO 地址范围是硬编码进 TLB 的。它不是一个配置项，"
           "是这次实验必须自己写进去的一段代码。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 07 §1.4 fence
    s = T.blank(prs)
    y = T.head(s, "第三关：一条软件必须自己插的指令",
               kicker="补课 1.4　陷阱", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "accel->GO = 1;                    // 写：启动加速器",
        '__asm__ __volatile__("fence ow, ir" ::: "memory");',
        "sum = accel->STATUS;              // 读：阻塞等结果",
    ], size=14.5, hi=(1,))

    T.txt(s, M, y + Inches(1.42), Inches(11.8), Inches(1.4),
          [[("RVWMO 只保证同一个地址的先后。GO 和 STATUS 是两个地址。",
             17, False, INK)],
           [("于是 STATUS 的读可以先发出去，GO 的写后到——"
             "加速器还没启动，结果已经读回来了。", 17, False, INK)],
           [("硬件标志挡不住它：这是体系结构明确允许的重排。", 18, True, RED)]],
          spacing=1.46)

    T.txt(s, M, y + Inches(2.98), Inches(11.8), Inches(0.4),
          [[("ow", 15, True, ACC, True),
            (" = 前面所有的写（output / write），", 15, False, INK),
            ("ir", 15, True, ACC, True),
            (" = 后面所有的读（input / read）。", 15, False, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "这是程序的 bug，不是 gem5 的 bug。同一份代码放到真实 RISC-V 硬件上，"
           "照样会错。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 08 punch
    T.punch(prs,
            [("三个 bug，", False),
             ("同一个 checksum。", True),
             ("0x7a2b4200 不告诉你错在哪，", False),
             ("accel.jobs 才告诉你。", True)],
            sub="没打 TLB 补丁：jobs = 0。少一条 fence：jobs = 16、"
                "macs 一个不少，结果照样错。",
            accent=ACC)

    # ======================================================== 09 §1.5 阻塞读
    s = T.blank(prs)
    y = T.head(s, "读 STATUS 的那些拍，CPU 什么都没干",
               kicker="补课 1.5", accent=ACC)

    T.area_blocks(s, M, y, CONTENT_W, Inches(1.0), [
        ("CPU 在算　55,652 拍　59.0%", 55652, INK, PAPER),
        ("CPU 空转，等 STATUS　38,712 拍　41.0%", 38712, ACC, PAPER),
    ], label_size=13)

    T.txt(s, M, y + Inches(1.32), Inches(11.8), Inches(0.36),
          [[("IPC 从 5.274 掉到 0.897，有两个原因，都不是「加速器慢」",
             18, True, INK)]])

    cw = (CONTENT_W - Inches(0.3)) / 2
    for k, (ttl, body, col) in enumerate([
        ("41% 的拍数，CPU 完全空转",
         "阻塞读把 CPU 钉在原地。这部分拍数分母还在，分子没了。", ACC),
        ("剩下的代码 IPC 只有 1.521",
         "84,665 ÷ 55,652。搬走的正是 ILP 最高的那一段。", RED),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, y + Inches(1.78), cw, Inches(1.0),
               fill=RED_DIM if col == RED else PAPER_DIM)
        T.txt(s, xx + Inches(0.24), y + Inches(1.94), cw - Inches(0.48),
              Inches(0.72),
              [[(ttl, 17, True, col)],
               [(body, 13.5, False, INK)]], spacing=1.36)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "卸载是一次反向挑选：你挑走的正是最好算的那部分代码，留给 CPU 的是最难算的。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 10 §1.6 算术强度
    s = T.blank(prs)
    y = T.head(s, "先算一遍：这一层要搬多少字节", kicker="补课 1.6", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "MAC  / 样本 =  784x128 + 128x10                =  101,632",
        "字节 / 样本 =  100,352 +  784 + 1,280 + 128    =  102,544",
        "                 w1       x      h      w2",
        "8 个样本    :  MAC 813,056        字节 820,352",
        "I = 813,056 / 820,352 = 0.9911  MAC / B",
    ], size=14, hi=(4,))

    T.txt(s, M, y + Inches(2.06), Inches(11.8), Inches(0.86),
          [[("这两个数必须和计数器一个不差。", 20, True, INK)],
           [("accel.macs = 813,056，accel.bytesRead = 820,352。对不上，"
             "说明你对这一层的理解是错的，后面全部白算。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "I ≈ 1 MAC/B：每读一个字节只做一次乘加。这是一个典型的带宽受限的核。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 11 §1.7 Roofline
    s = T.blank(prs)
    y = T.head(s, "两条屋顶，一个点", kicker="补课 1.7", accent=ACC)

    roofline(s, M + Inches(0.66), y + Inches(0.06), Inches(6.5), Inches(2.6),
             32,
             [("L2 总线 21.20 B/拍", 21.20, ACC),
              ("内存总线 12.71 B/拍", 12.71, GOLD)],
             [("b=1  21.00", 0.991, 21.00, ACC, False, Inches(0)),
              ("b=1  12.59", 0.991, 12.59, GOLD, False, Inches(0)),
              ("b=2  31.42", 1.965, 31.42, ACC, True, Inches(-0.30)),
              ("b=2  24.96", 1.965, 24.96, GOLD, True, Inches(0))])

    xr = Inches(8.2)
    T.txt(s, xr, y + Inches(0.10), Inches(4.38), Inches(2.5),
          [[("实际算力 = min( 算力, I × 带宽 )", 16, True, INK)],
           [("", 8, False, INK)],
           [("拐点 I* = 算力 ÷ 带宽", 15, True, ACC)],
           [("L2 总线　32 / 21.20 = 1.51", 13.5, False, INK, True)],
           [("内存总线 32 / 12.71 = 2.52", 13.5, False, INK, True)],
           [("", 8, False, INK)],
           [("batch=1 的 I = 0.99，两条总线都落在斜坡上——"
             "带宽说了算，加宽 pe 没有用。", 14, False, INK)]], spacing=1.32)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "batch=2 把 I 提到 1.965，越过了 L2 总线的拐点 1.51，于是跑满算力；"
           "内存总线的拐点是 2.52，越不过去。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 12 §1.8 Little
    s = T.blank(prs)
    y = T.head(s, "同时能有几笔读在路上", kicker="补课 1.8", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "Little 定律 :   带宽  =  在途请求数 x 行大小 / 平均延迟",
        "",
        "               L   =  64 B / 单发带宽          (往返延迟)",
        "               N*  =  L x 峰值带宽 / 64 B      (跑满所需的在途数)",
    ], size=14, hi=(0,))

    cw = (CONTENT_W - Inches(0.3)) / 2
    for k, (nm, one, lat, nstar, col) in enumerate([
        ("挂 L2 总线", "5.689", "11.25", "3.73", ACC),
        ("挂内存总线", "3.074", "20.82", "4.14", GOLD),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, y + Inches(1.76), cw, Inches(1.0))
        T.txt(s, xx + Inches(0.24), y + Inches(1.90), cw - Inches(0.48),
              Inches(0.76),
              [[(nm, 17, True, col)],
               [("单发 " + one + " B/拍　→　L = " + lat + " 拍　→　N* = "
                 + nstar, 14, False, INK, True)]], spacing=1.4)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "两者差 9.6 拍——多穿一级总线，多做一次一致性广播。这 9.6 拍就是「挂得远」的价钱。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 13 §02
    T.section(prs, "02", "先跑对，再跑快",
              "任务 1：四种组合，三个 checksum 一样，一个不一样", accent=ACC)

    # ======================================================== 14 任务1 四格
    s = T.blank(prs)
    y = T.head(s, "四种组合，只有一格是错的", kicker="任务 1", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["CPU", "fence", "checksum", "accel.jobs", "结论"],
        ["timing", "有", "0x1989da45", "16", "对"],
        ["timing", "无", "0x1989da45", "16", "对——顺序核不重排，看不出问题"],
        ["o3", "有", "0x1989da45", "16", "对"],
        ["o3", "无", "0x7a2b4200", "16", "错——结果读早了"],
    ], col_w=[Inches(1.3), Inches(1.1), Inches(2.3), Inches(1.6),
              Inches(5.533)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(2, 3), hi_rows=(4,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("顺序核跑对了，不代表程序是对的。", 20, True, INK)],
           [("timing 核不重排，所以少一条 fence 也看不出来。换成 o3 立刻暴露——"
             "这就是为什么两个核都要跑。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "错的那一格里，jobs = 16、macs = 813,056、jobCycles = 38,712，"
           "和正确的一模一样。加速器干完了活，是 CPU 读早了。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 15 两个 bug
    s = T.blank(prs)
    y = T.head(s, "两个 bug，一个计数器分得开", kicker="任务 1", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["看什么", "少一条 fence", "没打 TLB 补丁"],
        ["checksum", "0x7a2b4200", "0x7a2b4200"],
        ["accel.jobs", "16", "0"],
        ["accel.macs", "813,056", "0"],
        ["实际发生了什么", "算完了，CPU 读早了", "加速器一次都没启动"],
    ], col_w=[Inches(3.3), Inches(4.2), Inches(4.333)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(0, 1, 2), hi_rows=(2,), hi_fill=DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("看 checksum 只能知道「错了」。", 20, True, INK)],
           [("要知道「错在哪」，得看加速器自己的计数器——这就是给硬件加计数器的意义。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "写自己的 SimObject 时顺手加几个 Stats::Scalar，几乎不花时间，"
           "却是唯一能把这两个 bug 分开的手段。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 16 punch
    T.punch(prs,
            [("跑对了，不代表写对了。", False),
             ("换一个 CPU 模型，", False),
             ("同一份代码就会露馅。", True)],
            sub="timing 和 o3 必须都跑一遍。这是任务 1 的 15 分，也是一票否决项。",
            accent=ACC)

    # ======================================================== 17 §03
    T.section(prs, "03", "做多宽才够",
              "任务 3 与任务 4：把加速器加宽、加深，看它什么时候不再动",
              accent=ACC)

    # ======================================================== 18 任务3 主表
    s = T.blank(prs)
    y = T.head(s, "两条总线 × 四种宽度", kicker="任务 3", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["挂载点", "pe", "总周期", "算完用的拍数", "MAC/拍", "B/拍", "加速比"],
        ["l2bus", "8", "158,350", "102,216", "7.95", "8.03", "6.95×"],
        ["l2bus", "16", "107,068", "51,416", "15.81", "15.96", "10.27×"],
        ["l2bus", "32", "94,364", "38,712", "21.00", "21.19", "11.66×"],
        ["l2bus", "64", "94,356", "38,704", "21.01", "21.20", "11.66×"],
        ["membus", "8", "159,009", "102,680", "7.92", "7.99", "6.92×"],
        ["membus", "16", "120,463", "64,576", "12.59", "12.70", "9.13×"],
        ["membus", "32", "120,447", "64,560", "12.59", "12.71", "9.13×"],
        ["membus", "64", "120,439", "64,552", "12.60", "12.71", "9.13×"],
    ], col_w=[Inches(1.7), Inches(0.9), Inches(2.0), Inches(2.3),
              Inches(1.6), Inches(1.5), Inches(1.833)],
        head_fill=INK, size=13, head_size=12.5, row_h=Inches(0.38),
        mono_cols=(1, 2, 3, 4, 5, 6), hi_rows=(3,), hi_fill=DIM)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "动态指令数在这八行里恒为 84,665。变的只有周期——"
           "本次实验从头到尾不看指令数。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 19 加宽 0.008%
    s = T.blank(prs)
    y = T.head(s, "把它做宽一倍，快了 0.008%", kicker="任务 3", accent=ACC)

    hbars(s, M, y + Inches(0.10), CONTENT_W, [
        ("pe = 8", 6.95, INK_SOFT, "6.95×"),
        ("pe = 16", 10.27, INK_SOFT, "10.27×"),
        ("pe = 32", 11.66, ACC, "11.66×"),
        ("pe = 64", 11.66, ACC, "11.66×"),
    ], bar_h=Inches(0.40), gap=Inches(0.20), label_w=Inches(1.5),
        val_w=Inches(1.6))

    T.txt(s, M, y + Inches(2.50), Inches(11.8), Inches(0.9),
          [[("三次翻倍，分别拿到 1.479、1.135、1.00008 倍。", 20, True, INK)],
           [("从 32 加到 64，多花一倍的乘加阵列面积，换来 8 个周期"
             "（94,364 → 94,356）。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "算力屋顶早就顶到带宽屋顶上面去了。这时候再加算力，加的是永远用不上的算力。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 20 stall 陷阱
    s = T.blank(prs)
    y = T.head(s, "stall_frac 不是带宽利用率", kicker="任务 3　陷阱", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["pe", "MAC/拍", "B/拍", "stall_frac", "它到底在说什么"],
        ["8", "7.95", "8.03", "0.0034", "阵列几乎一直在算"],
        ["16", "15.81", "15.96", "0.0073", "还是一直在算"],
        ["32", "21.00", "21.19", "0.3379", "三分之一的口在等数据"],
        ["64", "21.01", "21.20", "0.6662", "三分之二的口在等数据"],
    ], col_w=[Inches(1.0), Inches(1.6), Inches(1.5), Inches(1.9),
              Inches(5.833)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(0, 1, 2, 3), hi_rows=(4,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("它量的是「乘加阵列有多空」，不是「总线有多满」。", 20, True, INK)],
           [("B/拍 从 21.19 到 21.20，一点没动——总线早就满了，空的是新加的那 32 个口。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "把 stall_frac 当成带宽利用率写进报告，是本次实验最常见的错答。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 21 任务4 扫描
    s = T.blank(prs)
    y = T.head(s, "在途请求开到几，才跑得满", kicker="任务 4", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["在途上限", "L2 总线 B/拍", "占峰值", "内存总线 B/拍", "占峰值"],
        ["1", "5.689", "26.8%", "3.074", "24.2%"],
        ["2", "11.06", "52.2%", "6.139", "48.3%"],
        ["4", "19.02", "89.7%", "11.88", "93.5%"],
        ["8", "21.20", "100%", "12.71", "100%"],
        ["16", "21.20", "100%", "12.71", "100%"],
        ["32", "21.20", "100%", "12.71", "100%"],
    ], col_w=[Inches(2.0), Inches(2.6), Inches(2.0), Inches(2.8),
              Inches(2.433)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.4),
        mono_cols=(0, 1, 2, 3, 4), hi_rows=(4,), hi_fill=GREEN_DIM)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "答案：两条总线都是 8。再往上一个周期都不省——"
           "加的是永远排不上队的表项，纯浪费面积。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 22 N* 是下界
    s = T.blank(prs)
    y = T.head(s, "公式给的 3.73，实际要 8", kicker="任务 4", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "L2 总线 :  L = 64 / 5.689 = 11.25 拍    N* = 11.25 x 21.20 / 64 = 3.73",
        "内存总线:  L = 64 / 3.074 = 20.82 拍    N* = 20.82 x 12.71 / 64 = 4.14",
    ], size=14, hi=())

    T.txt(s, M, y + Inches(1.16), Inches(11.8), Inches(1.4),
          [[("N* 是下界，不是答案。", 21, True, INK)],
           [("Little 定律假设请求匀速到达。真实的读是成串发出去的，中间有间隙，"
             "要靠多余的在途表项把间隙填上。", 17, False, INK)],
           [("实测 N=4 时只到 89.7% / 93.5%，开到 8 才满。", 17, False, INK)]],
          spacing=1.46)

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(0.4),
          [[("11.25 拍 vs 20.82 拍：差的 9.6 拍，是多一级总线加一次一致性广播的往返。",
             15, False, INK_SOFT)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "反过来也能用：测不到延迟时，用「单发带宽」倒推它——"
           "这是本次实验里最便宜的一次测量。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 23 punch
    T.punch(prs,
            [("加宽到 64，快 0.008%。", False),
             ("在途开到 32，一拍不省。", False),
             ("能加的都加满了，", False),
             ("还是 11.66 倍。", True)],
            sub="因为瓶颈根本不在加速器里面。它在总线上，和那颗没被卸载的 CPU 上。",
            accent=ACC)

    # ======================================================== 24 §04
    T.section(prs, "04", "一次搬多少",
              "任务 5：batch 从 1 开到 8，算术强度翻了 7.5 倍，程序先快后慢",
              accent=ACC)

    # ======================================================== 25 任务5 主表
    s = T.blank(prs)
    y = T.head(s, "batch 一开，两条总线就分不出来了", kicker="任务 5", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["batch", "挂载点", "I  MAC/B", "B/拍", "MAC/拍", "算完的拍数",
         "总周期", "加速比"],
        ["1", "l2bus", "0.991", "21.19", "21.00", "38,712", "94,364", "11.66×"],
        ["1", "membus", "0.991", "12.71", "12.59", "64,560", "120,447",
         "9.13×"],
        ["2", "l2bus", "1.965", "15.99", "31.42", "25,880", "82,058",
         "13.40×"],
        ["2", "membus", "1.965", "12.70", "24.96", "32,580", "89,030",
         "12.36×"],
        ["4", "l2bus", "3.861", "8.158", "31.50", "25,810", "83,850",
         "13.12×"],
        ["4", "membus", "3.861", "8.068", "31.15", "26,098", "84,072",
         "13.08×"],
        ["8", "l2bus", "7.464", "4.225", "31.54", "25,779", "87,353",
         "12.59×"],
        ["8", "membus", "7.464", "4.183", "31.23", "26,038", "87,594",
         "12.56×"],
    ], col_w=[Inches(1.0), Inches(1.5), Inches(1.6), Inches(1.3),
              Inches(1.4), Inches(1.9), Inches(1.7), Inches(1.433)],
        head_fill=INK, size=13, head_size=12, row_h=Inches(0.38),
        mono_cols=(0, 2, 3, 4, 5, 6, 7), hi_rows=(3,), hi_fill=GREEN_DIM)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "最快的是 batch=2 那一行。往下 batch=4、8 反而变慢——这不是测量误差。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 26 非单调
    s = T.blank(prs)
    y = T.head(s, "batch 开到 8，反而更慢", kicker="任务 5　陷阱", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["batch", "加速器算完用的拍数", "CPU 那边用的拍数", "总周期"],
        ["1", "38,712", "55,652", "94,364"],
        ["2", "25,880", "56,178", "82,058"],
        ["4", "25,810", "58,040", "83,850"],
        ["8", "25,779", "61,574", "87,353"],
        ["batch 2 → 8", "−0.4%", "+9.6%", "+6.5%"],
    ], col_w=[Inches(2.6), Inches(3.3), Inches(3.1), Inches(2.833)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.42),
        mono_cols=(1, 2, 3), hi_rows=(5,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("加速器那边已经停了：25,880 → 25,779，几乎不动。", 20, True, INK)],
           [("总周期还在往上走，涨的全是 CPU 那一边。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "只看加速器的计数器，你会得出「batch 越大越好」。总周期不同意。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 27 教科书验证
    s = T.blank(prs)
    y = T.head(s, "两个比值，误差 0.02%", kicker="任务 5　★", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "算完用的拍数比   64,560 / 38,712  =  1.6677     (membus / l2bus)",
        "实测带宽比       21.20  / 12.71   =  1.6680     (l2bus / membus)",
    ], size=14.5, hi=())

    yc = y + Inches(1.16)
    T.stat(s, M, yc, Inches(3.7), "1.6677", "算完用的拍数比", color=INK,
           size=52, sub="membus ÷ l2bus")
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "1.6680", "实测带宽比",
           color=INK, size=52, sub="l2bus ÷ membus")
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "0.02%", "两者的误差",
           color=ACC, size=52, sub="不是巧合")

    T.txt(s, M, y + Inches(3.02), Inches(11.8), Inches(0.44),
          [[("完全带宽受限的核，时间就是「字节数 ÷ 带宽」——一分不多，一分不少。",
             17, False, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "这是教科书公式在真实模拟器上的一次逐位验证。报告里做出这一步的，"
           "任务 5 的 18 分才拿得满。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 28 CPU 侧的账
    s = T.blank(prs)
    y = T.head(s, "CPU 侧的账：多了一个放不下的缓冲区",
               kicker="任务 5", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["batch", "CPU 侧缓冲区", "L1D 缺失", "L1D 访问", "CPU 段 IPC",
         "CPU 拍数"],
        ["2", "2,928 B", "714", "12,408", "1.521", "56,178"],
        ["8", "11,712 B", "2,601", "12,174", "1.376", "61,574"],
        ["变化", "×4", "×3.64", "−1.9%", "−9.5%", "+9.6%"],
    ], col_w=[Inches(1.3), Inches(2.4), Inches(1.8), Inches(1.8),
              Inches(2.1), Inches(2.433)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1, 2, 3, 4, 5), hi_rows=(3,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.34), Inches(11.8), Inches(1.24),
          [[("访问次数几乎没变，缺失多了 2.6 倍。", 21, True, INK)],
           [("batch=8 时 CPU 要自己攒 11,712 字节的中间结果，"
             "这块缓冲区把 L1D 挤掉了——留给 CPU 的那段代码变慢 9.6%。",
             17, False, INK_SOFT)]], spacing=1.46)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "卸载出去的那部分省了 100 拍，留下来的那部分多花了 5,400 拍。净亏。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 29 挂载点价值
    s = T.blank(prs)
    y = T.head(s, "batch 越大，挂在哪里越不重要", kicker="任务 5", accent=ACC)

    hbars(s, M, y + Inches(0.10), CONTENT_W, [
        ("batch = 1", 27.6, RED, "+27.6%"),
        ("batch = 2", 8.5, ACC, "+8.5%"),
        ("batch = 4", 0.26, INK_SOFT, "+0.26%"),
        ("batch = 8", 0.28, INK_SOFT, "+0.28%"),
    ], bar_h=Inches(0.40), gap=Inches(0.20), label_w=Inches(1.6),
        val_w=Inches(1.6))

    T.txt(s, M, y + Inches(2.50), Inches(11.8), Inches(0.9),
          [[("挂错地方的代价：从 27.6% 掉到 0.26%。", 20, True, INK)],
           [("因为 I 越过了两条拐点（1.51 和 2.52），两边都进了算力受限区——"
             "「该挂哪」取决于你打算喂它多大的强度。", 16, False, INK_SOFT)]],
          spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "0.26% 和 0.28% 都在 0.1% 的噪声地板附近。在这两行上说「l2bus 明显更好」，是要扣分的。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 30 punch
    T.punch(prs,
            [("batch=2 最快，", False),
             ("batch=8 更慢。", True),
             ("加速器停在 25,800 拍不动，", False),
             ("变慢的是旁边那颗 CPU。", True)],
            sub="局部最优不等于整体最优。只看加速器的计数器，会把方向做反。",
            accent=ACC)

    # ======================================================== 31 §05
    T.section(prs, "05", "挂在哪里",
              "任务 6：同一个加速器，只改 L2 的大小，快慢就完全反了过来",
              accent=ACC)

    # ======================================================== 32 L2 扫描
    s = T.blank(prs)
    y = T.head(s, "把 L2 缩小，两条总线换了位置", kicker="任务 6b", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["L2 容量", "挂 L2 总线", "挂内存总线", "谁更快", "快多少"],
        ["32 kB", "207,031", "184,201", "内存总线", "省 11.0%"],
        ["64 kB", "180,757", "161,605", "内存总线", "省 10.6%"],
        ["128 kB", "94,247", "120,279", "L2 总线", "省 21.6%"],
        ["256 kB", "94,364", "120,447", "L2 总线", "省 21.6%"],
        ["512 kB", "94,463", "120,600", "L2 总线", "省 21.7%"],
    ], col_w=[Inches(2.0), Inches(2.5), Inches(2.5), Inches(2.4),
              Inches(2.433)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.42),
        mono_cols=(1, 2), hi_rows=(1, 2), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("工作集是 101,632 字节 = 99.25 kB。", 20, True, INK)],
           [("L2 装得下（≥128 kB）：L2 总线快 21.6%。装不下（≤64 kB）："
             "内存总线快 11%。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "同一个加速器、同一份程序，只改 L2 的大小，「挂哪更好」这个结论就翻了过来。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 33 陷阱 T_CPU
    s = T.blank(prs)
    y = T.head(s, "「加速器污染了 Cache」——数据不同意",
               kicker="任务 6b　陷阱", accent=ACC)

    T.table(s, M, y, Inches(7.0), [
        ["L2 容量", "加速器算完的拍数", "CPU 那边的拍数"],
        ["32 kB", "151,736", "55,295"],
        ["64 kB", "125,435", "55,322"],
        ["128 kB", "38,712", "55,535"],
        ["256 kB", "38,712", "55,652"],
        ["512 kB", "38,712", "55,751"],
    ], col_w=[Inches(2.0), Inches(2.6), Inches(2.4)],
        head_fill=INK, size=13.5, head_size=12.5, row_h=Inches(0.42),
        mono_cols=(1, 2), hi_rows=(1,), hi_fill=RED_DIM)

    xr = Inches(8.2)
    T.stat(s, xr, y + Inches(0.06), Inches(4.38), "×3.92", "加速器慢了这么多",
           color=RED, size=54, sub="jobCycles 38,712 → 151,736")
    T.stat(s, xr, y + Inches(1.52), Inches(4.38), "1.3%", "CPU 侧一共只变了这么多",
           color=INK, size=54, sub="55,295 … 55,751")

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "CPU 的工作集只有约 1.4 kB，L2 缩到 32 kB 也装得下。"
           "「加速器把 CPU 的数据挤出去了」是想当然。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 34 谁在塞 L2
    s = T.blank(prs)
    y = T.head(s, "那谁被挤出去了：加速器挤了自己", kicker="任务 6b", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["L2 容量", "挂载点", "L2 缺失", "从内存条上读的字节"],
        ["32 kB", "l2bus", "8,903", "588,032"],
        ["32 kB", "membus", "35", "442,720"],
        ["256 kB", "l2bus", "30", "1,920"],
        ["256 kB", "membus", "30", "1,920"],
    ], col_w=[Inches(2.2), Inches(2.4), Inches(2.6), Inches(4.633)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(2, 3), hi_rows=(1,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("l2bus 的读会在 L2 里分配行，membus 的读不会。", 20, True, INK)],
           [("12,848 次流式读灌进一个只有 512 行的 L2，把自己上一轮读进来的行"
             "一遍遍挤掉——8,903 次缺失。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "membus 侧的读是被 snoop 出来的，不进 L2，所以缺失只有 35 次。"
           "代价是每次都要走更远的路。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 35 数据从哪来
    s = T.blank(prs)
    y = T.head(s, "挂在内存总线上，却没读过内存", kicker="任务 6c", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["计数器", "值", "它在说什么"],
        ["accel.bytesRead", "820,352", "加速器一共读进来这么多字节"],
        ["membus.snoopTraffic", "820,352", "全部由一致性广播供给"],
        ["accel.lineReads", "12,848", "读了这么多次缓存行"],
        ["membus.snoops", "12,848", "一次不多，一次不少"],
        ["dram.bytesRead", "1,920", "真正从内存条上来的"],
    ], col_w=[Inches(4.0), Inches(2.3), Inches(5.533)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.42),
        mono_cols=(0, 1), hi_rows=(5,), hi_fill=GREEN_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("挂载点决定走哪条路，一致性协议决定数据从哪来。", 20, True, INK)],
           [("数据一直躺在 L2 和 L1D 的脏行里。12.71 B/拍 是 SystemXBar 那 16 B/拍 "
             "的 79%，和 DRAM 带宽没有关系。", 16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "这不是模型的缺陷。ACE-Lite、CXL.cache、Intel CCI 上的加速器，都是这么取数的。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 36 punch
    T.punch(prs,
            [("接在内存总线上，", False),
             ("一次都没读过内存。", True),
             ("820,352 个字节，", False),
             ("全部来自别人的脏行。", True)],
            sub="「接到内存总线 = 从内存取数」——这句话是错的。",
            accent=ACC)

    # ======================================================== 37 §06
    T.section(prs, "06", "剩下的 68.5%",
              "任务 6a 与思考题：把加速器变成 0 拍，程序也只快 1.46 倍",
              accent=ACC)

    # ======================================================== 38 拆账
    s = T.blank(prs)
    y = T.head(s, "把最快的那 82,058 拍拆开", kicker="任务 6a", accent=ACC)

    T.area_blocks(s, M, y, CONTENT_W, Inches(1.0), [
        ("加速器在算　25,880 拍　31.5%", 25880, ACC, PAPER),
        ("CPU 在算　56,178 拍　68.5%", 56178, INK, PAPER),
    ], label_size=13)

    T.code(s, M, y + Inches(1.20), Inches(12.0), [
        "基线                    1,099,949 拍",
        "batch=2 挂 L2 总线         82,058 拍     已经拿到 13.40 倍",
        "把加速器变成 0 拍          56,178 拍     还能再快  1.46 倍",
        "                                        天花板    19.58 倍",
    ], size=14, hi=(3,))

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "加速器已经只占 31.5%。把它做到无穷快，整个程序也只能再快 1.46 倍。",
           color=RED, fill=RED_DIM, size=14.5)
    T.foot(s, FOOT)

    # ======================================================== 39 天花板
    s = T.blank(prs)
    y = T.head(s, "天花板是 19.58 倍，不是无穷", kicker="任务 6a", accent=ACC)

    yc = y + Inches(0.12)
    T.stat(s, M, yc, Inches(3.7), "13.40×", "现在拿到的", color=INK, size=54,
           sub="1,099,949 → 82,058")
    T.stat(s, M + Inches(4.05), yc, Inches(3.7), "1.46×", "加速器归零还能再快",
           color=ACC, size=54, sub="82,058 → 56,178")
    T.stat(s, M + Inches(8.1), yc, Inches(3.7), "19.58×", "这个程序的上限",
           color=RED, size=54, sub="1,099,949 → 56,178")

    T.txt(s, M, y + Inches(1.86), Inches(11.8), Inches(1.4),
          [[("Amdahl 定律的分母不会自己消失。", 21, True, INK)],
           [("那 56,178 拍是 CPU 自己的活：取数、重量化、写回。"
             "这一部分从头到尾一拍没少。", 17, False, INK)],
           [("要突破 19.58 倍，只能继续往硬件里搬东西，"
             "而不是把已经搬走的做得更快。", 17, False, INK)]], spacing=1.46)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "实验五的结论是「瓶颈会搬家」。本次实验的结论是：搬到最后，"
           "剩下的全是你没搬的那部分。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 40 两个方向
    s = T.blank(prs)
    y = T.head(s, "两条路，只有一条能抬天花板", kicker="任务 6a", accent=ACC)

    cw = (CONTENT_W - Inches(0.3)) / 2
    for k, (tag, ttl, body, res, col) in enumerate([
        ("方向 A", "把加速器的时间藏起来",
         "STATUS 改成非阻塞 + 双缓冲：CPU 一边算下一批，加速器一边算这一批。",
         "上限 1.461 倍　永远碰不到 19.58", INK),
        ("方向 B", "把 CPU 的活也搬走",
         "重量化搬进硬件，T_CPU 的 56,178 拍直接变小。",
         "天花板本身被抬高", ACC),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, y, cw, Inches(2.36),
               fill=DIM if col == ACC else PAPER_DIM)
        T.txt(s, xx + Inches(0.28), y + Inches(0.22), cw - Inches(0.56),
              Inches(1.7),
              [[(tag, 13, True, col)],
               [(ttl, 20, True, col)],
               [(body, 14.5, False, INK)]], spacing=1.4)
        T.txt(s, xx + Inches(0.28), y + Inches(1.88), cw - Inches(0.56),
              Inches(0.34), [(res, 14, True, col, True)])

    T.txt(s, M, y + Inches(2.62), Inches(11.8), Inches(0.78),
          [[("A 是把时间藏起来，B 是把时间消掉。", 20, True, INK)],
           [("藏起来的那部分还在分母里；消掉的那部分才真的没了。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "两条都写进报告才算完整。只写 A 的，任务 7 的 8 分拿不满。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 41 punch
    T.punch(prs,
            [("加速器已经只占三成。", False),
             ("把它做到无穷快，", False),
             ("程序也只能再快 1.46 倍。", True)],
            sub="Amdahl 定律的第三幕：优化到最后，剩下的全是没优化的那部分。",
            accent=ACC)

    # ======================================================== 42 IOMMU
    s = T.blank(prs)
    y = T.head(s, "如果加上地址翻译，要多付多少", kicker="思考题", accent=ACC)

    T.code(s, M, y, Inches(12.0), [
        "每个样本 :  25 个权重页 + 1 个输入页  +  1 个中间页 + 1 个输出页",
        "8 个样本 :  8 x (25 + 1)  +  8 x (1 + 1)   =  224 次翻译",
        "代价     :  224 x 30 拍  =  6,720 拍  =  jobCycles 的 17.4%",
    ], size=14, hi=(2,))

    T.table(s, M, y + Inches(1.42), CONTENT_W, [
        ["怎么把这 17.4% 省回来", "效果"],
        ["加速器自己带一个 IOTLB", "流式访问局部性好，命中后接近 0"],
        ["改用 2 MB 大页", "224 次 → 32 次，960 拍，只剩 +2.5%"],
        ["翻译与取数流水重叠", "翻译藏在上一次读的影子里"],
    ], col_w=[Inches(5.0), Inches(6.833)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.44),
        hi_rows=(2,), hi_fill=DIM)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "本次实验声明的模型局限第一条就是「完美地址翻译」。"
           "报告里不声明这一条，过程分要扣。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 43 面积怎么花
    s = T.blank(prs)
    y = T.head(s, "如果再给你一倍的面积", kicker="思考题", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["花在哪", "本次实测的收益", "值不值"],
        ["pe 从 32 加到 64", "1.00008 倍", "不值：带宽早就满了"],
        ["在途请求从 8 加到 16", "1.000 倍", "不值：队列早就够了"],
        ["加一块片上暂存", "当前配置约 1.0 倍", "L2 只有 32 kB 时能救回 3.92 倍"],
        ["重量化搬进硬件 + 双缓冲", "1.46 倍，并抬高天花板", "值：唯一能动分母的"],
    ], col_w=[Inches(4.0), Inches(3.3), Inches(4.533)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.5),
        mono_cols=(1,), hi_rows=(4,), hi_fill=GREEN_DIM)

    T.txt(s, M, y + Inches(2.80), Inches(11.8), Inches(0.78),
          [[("前两项在这个配置下等于白花。", 20, True, INK)],
           [("面积要花在「当前的瓶颈」上——而当前的瓶颈是那颗没被卸载的 CPU。",
             16, False, INK_SOFT)]], spacing=1.44)

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "另一个必答点：macs_per_byte 与硬件无关——分子分母都只由算法和数据布局决定。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 44 瓶颈搬家
    s = T.blank(prs)
    y = T.head(s, "五个实验，瓶颈搬了六次家", kicker="小结", accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["实验", "当时的瓶颈", "怎么解决的"],
        ["二　流水线", "结构冲突与数据前递", "加旁路"],
        ["三　分支预测", "预测失败的惩罚", "换预测器"],
        ["四　乱序执行", "IQ 满、LQ 满", "调窗口大小"],
        ["五　加一条指令", "指令数，然后是取指带宽", "加 dotp8，再对齐循环体"],
        ["六　加速器（前半）", "总线带宽", "换挂载点、开 batch"],
        ["六　加速器（后半）", "没被卸载的那颗 CPU", "还没解决 → 实验七"],
    ], col_w=[Inches(3.0), Inches(4.2), Inches(4.633)],
        head_fill=INK, size=14, head_size=13, row_h=Inches(0.42),
        hi_rows=(6,), hi_fill=RED_DIM)

    T.txt(s, M, y + Inches(2.90), Inches(11.8), Inches(0.7),
          [[("每一步都是对的，每一步都换来一个新瓶颈。", 20, True, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "性能优化没有「做完」这个状态，只有「当前瓶颈在哪」。这是整门课的主线。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 45 局限与复现
    s = T.blank(prs)
    y = T.head(s, "报告里必须写清楚的两件事", kicker="附录", accent=ACC)

    T.txt(s, M, y, Inches(5.6), Inches(0.34),
          [[("模型的局限", 19, True, RED)]])
    T.bullets(s, M, y + Inches(0.46), Inches(5.6), [
        [("加速器直接用物理地址，没有 IOMMU（真实系统 +17.4%）",
          13.5, False, INK)],
        [("STATUS 是阻塞读；真实硬件上是轮询或中断", 13.5, False, INK)],
        [("加速器与 CPU 同一时钟域，没有跨时钟开销", 13.5, False, INK)],
        [("没有 DMA 描述符、没有驱动、没有上下文切换", 13.5, False, INK)],
    ], size=13.5, gap=Inches(0.58), marker=RED, marker_size=Inches(0.11))

    xr = Inches(6.9)
    T.txt(s, xr, y, Inches(5.68), Inches(0.34),
          [[("怎么判你的数", 19, True, ACC)]])
    T.bullets(s, xr, y + Inches(0.46), Inches(5.68), [
        [("种子是你的学号后四位，周期差 <0.3% 一律算对",
          13.5, False, INK)],
        [("噪声地板 0.1%：pe 32→64 的 0.008% 按「无差异」判",
          13.5, False, INK)],
        [("三条常数线：macs 813,056、insts 84,665、CPU 拍数 ±1.3%",
          13.5, False, INK)],
        [("唯一的逐位要求：任务 3 的 pe=32 行 = 任务 5 的 batch=1 行",
          13.5, False, INK)],
    ], size=13.5, gap=Inches(0.58), marker=ACC, marker_size=Inches(0.11))

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(0.7),
          [[("你的数字和参考解答不会一模一样，这是正常的。", 20, True, INK)]])

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "判的是内部自洽：你的解释要跟你自己的数对得上，不必跟参考解答对得上。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 46 判分
    s = T.blank(prs)
    y = T.head(s, "分怎么给", kicker="评分", accent=ACC)

    T.table(s, M, y, Inches(7.3), [
        ["板块", "内容", "分"],
        ["A", "任务 1　正确性", "15"],
        ["B", "任务 2　纸面预测", "7"],
        ["C", "任务 3　挂载点 × 算力", "15"],
        ["D", "任务 4　Little 定律", "10"],
        ["E", "任务 5　batch", "18"],
        ["F", "任务 6　三个意外", "20"],
        ["G", "任务 7　一页纸", "8"],
        ["Q", "思考题", "7"],
        ["X / Z", "附加分 / 反向扣分", "+10 / −10"],
    ], col_w=[Inches(1.3), Inches(4.7), Inches(1.3)],
        head_fill=INK, size=13, head_size=12.5, row_h=Inches(0.34),
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
        hi_rows=(6,), hi_fill=DIM)

    xr = Inches(8.5)
    T.txt(s, xr, y, Inches(4.08), Inches(0.34),
          [[("一票否决：两处 checksum", 18, True, RED)]])
    T.txt(s, xr, y + Inches(0.40), Inches(4.08), Inches(0.62),
          [[("任务 1 的四格表、任务 5 的八行。对不上或没贴 → 全卷作废。",
             13.5, False, INK)]], spacing=1.32)

    T.txt(s, xr, y + Inches(1.16), Inches(4.08), Inches(0.34),
          [[("五条封顶", 18, True, ACC)]])
    T.bullets(s, xr, y + Inches(1.58), Inches(4.08), [
        [("事后补填预测 → B 记 0", 13, False, INK)],
        [("不用 stall_frac 分段 → C ≤ 7", 13, False, INK)],
        [("没画 Roofline 图 → E ≤ 10", 13, False, INK)],
        [("只答 6a、不答 6b/6c → F ≤ 8", 13, False, INK)],
        [("没写模型局限 → G ≤ 4", 13, False, INK)],
    ], size=13, gap=Inches(0.42), marker=ACC, marker_size=Inches(0.11))

    T.note(s, M, y + Inches(3.62), CONTENT_W,
           "E + F = 38 分，全在「验证」和「解释」上，不在跑数据上。"
           "跑完全部扫描约 40 分钟，写清楚为什么要两小时。",
           color=ACC, fill=PAPER_DIM, size=14.5, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 47 一页纸
    s = T.blank(prs, dark=True)
    T.txt(s, M, Inches(0.85), CONTENT_W, Inches(0.44),
          [("实验六　一页纸", 15, True, ACC)])
    T.txt(s, M, Inches(1.32), CONTENT_W, Inches(0.72),
          [("带走这五句", 36, True, PAPER)])

    lines = [
        ("指令少 68.5 倍，程序只快 11.66 倍。",
         "41% 的拍数 CPU 在阻塞读上空转，剩下的代码 IPC 只有 1.521。"),
        ("能加的都加满了，还是不动。",
         "pe 翻倍快 0.008%，在途翻倍一拍不省。瓶颈不在加速器里面。"),
        ("挂载点决定路径，一致性协议决定数据从哪来。",
         "挂在内存总线上的加速器，820,352 字节全部来自别人的脏行。"),
        ("batch=2 最快，batch=8 更慢。",
         "加速器停在 25,800 拍不动，变慢的是旁边那颗 CPU。"),
        ("天花板是 19.58 倍。",
         "把加速器做到 0 拍，也只能再快 1.46 倍。剩下的只能继续往硬件里搬。"),
    ]
    yy = Inches(2.42)
    for k, (a, b) in enumerate(lines):
        yl = yy + Inches(0.82) * k
        T.rect(s, M, yl + Inches(0.08), Inches(0.05), Inches(0.5), ACC)
        T.txt(s, M + Inches(0.3), yl, Inches(11.4), Inches(0.72),
              [[(a, 18, True, PAPER)],
               [(b, 13.5, False, WHITE_DIM)]], spacing=1.34)

    T.txt(s, M, SLIDE_H - Inches(0.95), CONTENT_W, Inches(0.4),
          [("下一次：实验七　给定预算，整机怎么配最优——600 A 的面积怎么花",
            13, False, WHITE_DIM)])

    return prs


if __name__ == "__main__":
    prs = build()
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    print("wrote %s  (%d slides)" % (out, len(prs.slides._sldIdLst)))
