# -*- coding: utf-8 -*-
"""实验四《乱序执行与分支预测》讲课用 PPT。

    python _tools/ppt/lab4.py            → labs/lab4/幻灯片.pptx

所有数字来自 labs/lab4/参考解答.md，改数据请同步改那一处。
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
                   "..", "..", "labs", "lab4", "幻灯片.pptx")

ACC = T.LAB_ACCENT[4]          # 橙
FOOT = "实验四　乱序执行与分支预测"


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
    T.cover(prs, 4,
            "乱序执行与分支预测",
            "核心问题：加宽发射、加大 ROB、换预测器，哪个划算\n"
            "一台 8 发射的乱序核跑不过 2 发射的——同一份机器码，只是数据换了一组",
            "计算机系统综合设计实验　·　4 学时　·　含课本模型的实测验证")

    # ======================================================== 01 立题
    T.punch(prs,
            [("乱序核有三张表。", False),
             ("谁满了，谁就是瓶颈。", True),
             ("把它加大，瓶颈立刻搬到下一张，", False),
             ("而且会绕一圈搬回来。", True)],
            sub="这就是瓶颈迁移。本次实验将完整观察它转过一圈，并回到起点。",
            accent=ACC)

    # ======================================================== 02 今天的决策
    s = T.blank(prs)
    y = T.head(s, "本次实验要做的决策", kicker="任务", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("实验二、三的资源都投在核外。本次换一个方向："
             "资源只能投在核内，共四个选项：", 17, False, INK)]])

    cw = (CONTENT_W - Inches(0.9)) / 4
    yc = y + Inches(0.66)
    for k, (ttl, body) in enumerate([
        ("加发射宽度", "每拍取、发、退更多指令"),
        ("加 ROB", "允许更多指令同时在飞"),
        ("加 LQ / IQ", "在飞的 load 和待发指令"),
        ("换分支预测器", "预测更准，减少无效执行"),
    ]):
        xx = M + (cw + Inches(0.3)) * k
        T.card(s, xx, yc, cw, Inches(1.42))
        T.txt(s, xx + Inches(0.22), yc + Inches(0.24), cw - Inches(0.44),
              Inches(1.0),
              [[(ttl, 17, True, ACC)],
               [(body, 13.5, False, INK)]], spacing=1.4)

    T.txt(s, M, y + Inches(2.34), Inches(11.8), Inches(1.0),
          [[("问：对 qnn 来说，这四样里哪一样是瓶颈？", 21, True, INK)],
           [("四项全部加大，只换来 +20.7%。资源用尽，瓶颈仍在。",
             17, False, INK_SOFT)]], spacing=1.42)

    T.note(s, M, y + Inches(3.36), CONTENT_W,
           "本次实验还要用课本的手推结果与模拟器实测相互对照。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 03 §01
    T.section(prs, "01", "乱序核提供的是什么",
              "在动手之前，先把三张表和一条判据说清楚", accent=ACC)

    # ======================================================== 04 顺序核为什么慢
    s = T.blank(prs)
    y = T.head(s, "它提供的是重叠，不是速度", kicker="补课 1.1", accent=ACC)

    T.code(s, M, y, Inches(7.6), [
        "a = mem[p];   /* L1 失效，要等 ~20 拍 */",
        "b = a + 1;    /* 确实依赖 a，必须等待 */",
        "c = x * y;    /* 与 a 无依赖，却仍需等待 */",
        "d = x + y;    /* 同上                   */",
    ], size=14, hi=(2, 3))

    T.txt(s, Inches(8.55), y + Inches(0.1), Inches(4.03), Inches(1.5),
          [[("乱序核的作用", 19, True, ACC)],
           [("把 c、d 提前算完，", 15, False, INK)],
           [("使那 20 拍不被浪费。", 15, False, INK)]], spacing=1.42)

    T.txt(s, M, y + Inches(1.92), Inches(11.8), Inches(1.0),
          [[("乱序核不缩短任何一次访存的延迟。", 20, False, INK)],
           [("它只是在等待期间执行其他指令。", 20, True, RED)]], spacing=1.42)

    T.note(s, M, y + Inches(3.10), CONTENT_W,
           "顺序核中，一条指令阻塞，其后的全部指令随之阻塞。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 05 三张表
    s = T.blank(prs)
    y = T.head(s, "三张表，释放的时刻不一样", kicker="补课 1.2　★★",
               accent=ACC)

    T.table(s, M, y, CONTENT_W, [
        ["表", "装什么", "什么时候占用", "什么时候释放", "周转"],
        ["ROB", "全部在飞的指令", "进入 rename 级", "按程序序提交时", "慢"],
        ["IQ", "还没发射的指令", "进入 rename 级", "发射出去就释放", "快"],
        ["LQ / SQ", "在飞的 load / store", "进入 rename 级", "提交时", "慢"],
    ], col_w=[1.5, 3.3, 2.6, 3.0, 1.433], size=13.5, head_size=12.5,
        row_h=Inches(0.52), hi_rows=(3,), hi_fill="FBEADD")

    T.txt(s, M, y + Inches(2.44), Inches(11.8), Inches(1.0),
          [[("一条卡在失效上的 load，会一直占着 1 个 ROB 和 1 个 LQ 表项，"
             "直到数据回来并提交。", 16, False, INK)],
           [("一次长延迟访存，冻结的是 ROB 和 LQ，不是 IQ。",
             20, True, RED)]], spacing=1.42)

    T.note(s, M, y + Inches(3.66), CONTENT_W,
           "这一条是任务 2 的全部依据。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 06 FullEvents
    s = T.blank(prs)
    y = T.head(s, "判定瓶颈只有一条判据", kicker="补课 1.3　★★", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("三张表任何一张满了，rename 级即停顿，整条前端随之阻塞。"
             "gem5 将它们分开计数：", 15.5, False, INK)]])

    T.code(s, M, y + Inches(0.60), Inches(6.5), [
        "rob_full_events      iq_full_events",
        "lq_full_events       sq_full_events",
    ], size=14)

    T.card(s, Inches(7.6), y + Inches(0.60), Inches(4.98), Inches(0.94),
           fill="FBEADD")
    T.txt(s, Inches(7.9), y + Inches(0.74), Inches(4.4), Inches(0.7),
          [[("谁最大，谁就是瓶颈。", 19, True, ACC)]],
          anchor=MSO_ANCHOR.MIDDLE)

    T.txt(s, M, y + Inches(1.78), Inches(11.8), Inches(1.0),
          [[("加大它，性能提升；加大其余的，一个周期都不省。",
             18, False, INK)],
           [("它一旦归零，瓶颈立即转移到下一张表 —— 这就是瓶颈迁移。",
             18, True, RED)]], spacing=1.42)

    T.note(s, M, y + Inches(3.00), CONTENT_W,
           "FullEvents 是事件数不是周期数：只比同一张表，不要跨表比绝对值。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 07 MLP
    s = T.blank(prs)
    y = T.head(s, "MLP：乱序核真正提供的能力", kicker="补课 1.4　★",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.5),
          [[("l1d_mlp", 22, True, ACC, True),
            ("　＝　", 22, False, INK),
            ("l1d_misses ÷ l1d_mshr_misses", 22, True, INK, True)]])

    T.txt(s, M, y + Inches(0.66), Inches(11.8), Inches(0.44),
          [[("一次真正的下级访问，被多少条 load 分摊。", 18, False, INK)]])

    cw = (CONTENT_W - Inches(0.43)) / 2
    yc = y + Inches(1.30)
    for k, (ttl, val, l1, l2, col, fill) in enumerate([
        ("o3　乱序核", "15.597", "可同时容纳十几个失效。",
         "这是延迟隐藏的定量表述。", ACC, "FBEADD"),
        ("timing　顺序阻塞核", "1.000", "一次只能等待一个失效。",
         "misses 与 mshr_misses 逐条相等。", GREEN, GREEN_DIM),
    ]):
        xx = M + (cw + Inches(0.43)) * k
        T.card(s, xx, yc, cw, Inches(2.16), fill=fill)
        T.txt(s, xx + Inches(0.34), yc + Inches(0.24), cw - Inches(0.68),
              Inches(1.7),
              [[(ttl, 17, True, col)],
               [(val, 46, True, col, True)],
               [(l1, 14, False, INK)],
               [(l2, 14, False, INK)]], spacing=1.22)

    T.note(s, M, y + Inches(3.66), CONTENT_W,
           "MLP 不是 Cache 的属性，而是核的属性。同一个 Cache，换核相差 15 倍。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 08 punch
    T.punch(prs,
            [("乱序核既不重排也不消灭访存流量。", False),
             ("它只是把等待叠起来。", True)],
            sub="所以 MLP 是本次实验的解释变量：MLP 不涨，周期数就不会降。",
            accent=ACC)

    # ======================================================== 09 §02
    T.section(prs, "02", "任务 1　发射宽度",
              "宽度 ×8，IPC 提升几倍？差额去了哪里？", accent=ACC)

    # ======================================================== 10 宽度实测
    s = T.blank(prs)
    y = T.head(s, "宽度 ×8，IPC 只涨 5.31 倍", kicker="任务 1　实测",
               accent=ACC)

    T.table(s, M, y, Inches(8.5), [
        ["width", "cycles", "IPC", "IPC/width", "最大的 FullEvents"],
        ["1", "5,833,900", "0.9944", "0.994", "一张表都没满"],
        ["2", "3,341,821", "1.7360", "0.868", "IQ 2,958"],
        ["4", "1,711,469", "3.3897", "0.847", "LQ 10,315"],
        ["8", "1,099,658", "5.2756", "0.660", "LQ 207,625"],
    ], col_w=[1.1, 1.8, 1.3, 1.4, 2.9], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(0, 1, 2, 3), hi_rows=(4,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.LEFT])

    T.stat(s, Inches(9.45), y + Inches(0.34), Inches(3.13), "66.3%",
           "宽度的兑现率", color=ACC, size=44,
           sub="宽度为 1 时 IPC ≈ 0.994，\n每一拍都已用满。\n此后每翻一倍降一档。")

    T.txt(s, M, y + Inches(2.56), Inches(11.8), Inches(0.5),
          [[("宽度 1 时四张表全是 0 —— ", 16.5, False, INK),
            ("没有瓶颈信号本身就是一个结论：瓶颈是宽度自己。",
             16.5, True, RED)]])

    T.note(s, M, y + Inches(3.26), CONTENT_W,
           "得出「模型不准」结论的，通常是没有查 FullEvents。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 11 加宽度买到了什么
    s = T.blank(prs)
    y = T.head(s, "加宽度得到的不是访存更快", kicker="任务 1　解释",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("宽度从 1 到 8，四行的指令数完全相同（5,801,400）。"
             "访存一侧的变化如下：", 16, False, INK)]])

    for k, (val, lab, sub, col) in enumerate([
        ("12,823", "l1d_mshr_misses", "四行恒定，一次不多\n也一次不少。", INK),
        ("×4.00", "l1d_mlp　3.903 → 15.597", "同时等待的 load\n增加到四倍。", ACC),
        ("LQ", "瓶颈的新位置", "207,625 次 LQ 满，\nIQ 只有 71,066。", RED),
    ]):
        T.stat(s, M + Inches(4.05) * k, y + Inches(0.72), Inches(3.7),
               val, lab, color=col, size=46, sub=sub)

    T.txt(s, M, y + Inches(2.86), Inches(11.8), Inches(1.0),
          [[("真正发到 L2 的访问一次都没有增加。变化的只是"
             "「每一次下级访问背后有多少条 load」。", 16, False, INK)],
           [("加宽度得到的不是访存更快，而是更多访存同时等待。",
             19, True, RED)]], spacing=1.42)

    T.foot(s, FOOT)

    # ======================================================== 12 punch
    T.punch(prs,
            [("「没有瓶颈信号」", False),
             ("本身就是一个结论。", True),
             ("它说明限制来自结构上限，不是资源竞争。", False)],
            sub="常见误判是「统计出错」。四张表全为 0，恰恰说明宽度本身就是那道墙。",
            accent=ACC)

    # ======================================================== 13 §03
    T.section(prs, "03", "瓶颈迁移：它会换位置",
              "任务 2 —— 三张表轮流放开，观察瓶颈转移到哪里", accent=ACC)

    # ======================================================== 14 ROB 逐位相同
    s = T.blank(prs)
    y = T.head(s, "ROB 加到 192 以后，逐位相同", kicker="任务 2a　ROB",
               accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("固定 width 8，只扫 ROB。看 rob_full_events 何时归零：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.60), Inches(8.5), [
        ["rob", "cycles", "rob_full_events", "相对上一档"],
        ["32", "2,510,543", "647,375", "—"],
        ["64", "1,578,791", "341,889", "−37.11%"],
        ["128", "1,100,056", "2,625", "−30.32%"],
        ["192", "1,099,658", "0", "−0.036%"],
        ["384", "1,099,658", "0", "0.000%"],
    ], col_w=[1.2, 2.3, 2.6, 2.4], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3), hi_rows=(5,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.60), Inches(3.13), "0",
           "192 → 384 省下的周期", color=ACC, size=54, mono=False,
           sub="1,099,658 对 1,099,658。\n不是四舍五入相同，\n是逐位相同。")

    T.txt(s, M, y + Inches(3.42), Inches(11.8), Inches(1.0),
          [[("rob_full_events 在 192 已经归零。归零之后这张表不再是瓶颈，"
             "继续加大没有任何收益。", 16.5, False, INK)],
           [("满信号归零的那一档，就是这张表的够用点。",
             19.5, True, RED)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 15 两个访存数字
    s = T.blank(prs)
    y = T.head(s, "两个访存数字，给出两个结论", kicker="任务 2a　口径陷阱",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("ROB 从 32 加到 384，同一份 stats 中两个访存数字的走向相反：",
             16, False, INK)]])

    T.stat(s, M, y + Inches(0.70), Inches(5.4), "×3.17",
           "l1d_misses　63,069 → 200,001", color=RED, size=44,
           sub="表面上像是「缺失激增」。")
    T.stat(s, M + Inches(6.4), y + Inches(0.70), Inches(5.4), "12,823",
           "l1d_mshr_misses　五行恒定", color=GREEN, size=44,
           sub="真正发到 L2 的访问未增加。")

    T.code(s, M, y + Inches(2.42), Inches(11.8), [
        "l1d_mlp  =  l1d_misses / l1d_mshr_misses",
        "rob =  32 :    63,069 / 12,823 =  4.918",
        "rob = 384 :   200,001 / 12,823 = 15.597",
    ], size=13.5, hi=(0,))

    T.txt(s, M, y + Inches(3.88), Inches(11.8), Inches(0.5),
          [[("分母恒定，分子上升 —— 上升的是 MLP，不是访存量。",
             19, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 16 LQ 天花板
    s = T.blank(prs)
    y = T.head(s, "LQ 的收益有个天花板，写在参数里", kicker="任务 2b　LQ",
               accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("固定 width 8，只扫 LQ 深度。看 lq_full_events 何时归零：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.60), Inches(8.5), [
        ["lq", "cycles", "lq_full_events", "l1d_mlp", "mlp ÷ lq"],
        ["8", "2,705,999", "1,654,627", "3.989", "0.499"],
        ["16", "1,660,362", "547,987", "7.831", "0.489"],
        ["32", "1,099,658", "207,625", "15.597", "0.487"],
        ["64", "1,014,232", "0", "15.597", "0.244"],
        ["128", "1,014,232", "0", "15.597", "0.122"],
    ], col_w=[1.0, 1.9, 2.1, 1.7, 1.8], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3, 4), hi_rows=(4,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.60), Inches(3.13), "20",
           "tgts_per_mshr", color=ACC, size=50,
           sub="一个 MSHR 最多挂 20 条 load。\n15.597 已达到它的 78%。")

    T.txt(s, M, y + Inches(3.40), Inches(11.8), Inches(1.0),
          [[("LQ 未满之前，MLP 约为 LQ 的一半；LQ 一旦不再满，"
             "MLP 即停在 15.597 不再上升。", 16.5, False, INK)],
           [("加 LQ 得到的是并发度，而并发度的上限由 MSHR 决定。",
             19.5, True, RED)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 17 IQ 对照组
    s = T.blank(prs)
    y = T.head(s, "同一组 IQ 扫描，两个结论", kicker="任务 2c　必做对照",
               accent=ACC)

    T.txt(s, M, y, CONTENT_W, Inches(0.44),
          [[("同一组 iq 扫描跑两遍，唯一区别是第二遍先加了 --lq 64：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.58), CONTENT_W, [
        ["iq", "不放开 LQ　cycles", "逐段", "先放开 lq=64　cycles", "逐段"],
        ["16", "2,387,471", "—", "2,387,471", "—"],
        ["32", "1,444,321", "−39.50%", "1,444,338", "−39.50%"],
        ["64", "1,099,658", "−23.86%", "1,014,232", "−29.79%"],
        ["128", "1,099,357", "−0.027%", "976,819", "−3.69%"],
    ], col_w=[1.1, 2.9, 1.9, 3.0, 2.933], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3, 4), hi_rows=(4,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(2.96), Inches(11.8), Inches(1.5),
          [[("iq 64 → 128：不放开 LQ 时仅 −0.027%（噪声地板以下），"
             "先放开 LQ 后为 −3.69%。", 16.5, False, INK)],
           [("两组的 iq_full_events 都降到同一个 31,614。"
             "变的不是 IQ，而是 IQ 之后是否仍然阻塞。", 15.5, False, INK_SOFT)],
           [("同一次扫描，两个结论差 100 倍以上。", 20, True, RED)]],
          spacing=1.40)
    T.foot(s, FOOT)

    # ======================================================== 18 punch
    T.punch(prs,
            [("资源 A 的收益，", False),
             ("取决于资源 B 有没有先放开。", True),
             ("一次只放开一个瓶颈。", False)],
            sub="否则测到的是另一个资源的上限 —— 这就是 2c 对照组必做的原因。",
            accent=ACC)

    # ======================================================== 19 ROB 第二轮
    s = T.blank(prs)
    y = T.head(s, "同一个区间，第一轮 0%，第二轮 −5.50%",
               kicker="任务 2.4　二次扫描", accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("在 --lq 64 --iq 128 之上，再扫一遍 ROB：", 16, False, INK)]])

    T.table(s, M, y + Inches(0.62), Inches(8.5), [
        ["rob", "cycles", "rob_full", "lq_full", "相对上一档"],
        ["192", "976,819", "68,147", "0", "—"],
        ["256", "923,129", "182", "60,859", "−5.50%"],
        ["384", "923,129", "0", "60,957", "0.000%"],
        ["512", "923,129", "0", "60,957", "0.000%"],
    ], col_w=[1.1, 1.9, 1.7, 1.7, 2.1], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(0, 1, 2, 3, 4), hi_rows=(2,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.36), Inches(3.13), "0.000%",
           "任务 2a：rob 192 → 384", color=INK_SOFT, size=32,
           sub="当时 LQ 仍在阻塞，\n加大 ROB 没有收益。")
    T.stat(s, Inches(9.45), y + Inches(1.88), Inches(3.13), "−5.50%",
           "任务 2.4：rob 192 → 256", color=ACC, size=32,
           sub="先放开 LQ 和 IQ 之后，\n同一区间开始产生收益。")

    T.txt(s, M, y + Inches(3.44), Inches(11.8), Inches(1.0),
          [[("这一档不是「ROB 又变重要了」，而是 LQ 和 IQ 让开之后，"
             "轮到 ROB 成为限制。", 16.5, False, INK)],
           [("同一参数区间的收益，取决于在什么时刻去测量它。",
             19.5, True, RED)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 20 闭环
    s = T.blank(prs)
    y = T.head(s, "瓶颈转了一圈，回到原点", kicker="任务 2　小结", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("每一步都放开当时最大的那张表，观察下一步最大的变成哪一张：",
             16.5, False, INK)]])

    chain = [
        ("① LQ", "基线 w=8", "207,625", RED),
        ("② IQ", "--lq 64", "130,426", ACC),
        ("③ ROB", "--iq 128", "68,147", GOLD),
        ("④ LQ", "--rob 256", "60,859", RED),
        ("⑤ IQ", "--lq 128", "58,489", ACC),
    ]
    cw = (CONTENT_W - Inches(0.34) * 4) / 5
    yc = y + Inches(0.62)
    for k, (name, cond, val, col) in enumerate(chain):
        xx = M + (cw + Inches(0.34)) * k
        T.card(s, xx, yc, cw, Inches(1.86))
        T.txt(s, xx, yc + Inches(0.16), cw, Inches(0.46),
              [(name, 24, True, col)], align=PP_ALIGN.CENTER)
        T.txt(s, xx, yc + Inches(0.68), cw, Inches(0.32),
              [(cond, 12.5, False, INK_SOFT, True)], align=PP_ALIGN.CENTER)
        T.txt(s, xx, yc + Inches(1.06), cw, Inches(0.44),
              [(val, 17, True, INK, True)], align=PP_ALIGN.CENTER)
        T.txt(s, xx, yc + Inches(1.46), cw, Inches(0.30),
              [("次满", 11.5, False, INK_SOFT)], align=PP_ALIGN.CENTER)
        if k < 4:
            T.txt(s, xx + cw, yc + Inches(0.62), Inches(0.34), Inches(0.5),
                  [("→", 17, True, INK_SOFT)], align=PP_ALIGN.CENTER)

    T.txt(s, M, y + Inches(2.76), Inches(11.8), Inches(1.6),
          [[("每一步都确有收益，但每一步都把瓶颈转交给了下一张表。",
             16.5, False, INK)],
           [("第 ④ 步之后 LQ 再次满，第 ⑤ 步之后 IQ 再次成为最大项。",
             16.5, False, INK)],
           [("整整一圈的累计收益，只有 +20.74%。", 20, True, RED)]],
          spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 21 punch
    T.punch(prs,
            [("五步之后，瓶颈又回到了 IQ。", False),
             ("这不是操作失误，", False),
             ("而是乱序核的结构决定的。", True)],
            sub="瓶颈迁移没有终点。真正要问的是：整整一圈的累计收益是多少？",
            accent=ACC)

    # ======================================================== 22 §04
    T.section(prs, "04", "与课本模型对照",
              "任务 3、4 —— 手算给出 4/7，实测给出 6/7，差异从何而来", accent=ACC)

    # ======================================================== 23 2bit 状态机
    s = T.blank(prs)
    y = T.head(s, "2 bit 饱和计数器：四个状态一条规则", kicker="补课 1.6　★",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("gem5 的 local 预测器，每个分支一个 2 bit 计数器：",
             16.5, False, INK)]])

    cw = (CONTENT_W - Inches(0.36) * 3) / 4
    yc = y + Inches(0.60)
    for k, (nm, bits, pred, col, fill) in enumerate([
        ("SN", "00", "预测　不跳", RED, RED_DIM),
        ("WN", "01", "预测　不跳", RED, RED_DIM),
        ("WT", "10", "预测　跳", GREEN, GREEN_DIM),
        ("ST", "11", "预测　跳", GREEN, GREEN_DIM),
    ]):
        xx = M + (cw + Inches(0.36)) * k
        T.card(s, xx, yc, cw, Inches(1.66), fill=fill)
        T.txt(s, xx, yc + Inches(0.18), cw, Inches(0.5),
              [(nm, 28, True, col, True)], align=PP_ALIGN.CENTER)
        T.txt(s, xx, yc + Inches(0.76), cw, Inches(0.34),
              [(bits, 15, True, INK, True)], align=PP_ALIGN.CENTER)
        T.txt(s, xx, yc + Inches(1.16), cw, Inches(0.34),
              [(pred, 14, False, INK)], align=PP_ALIGN.CENTER)

    T.txt(s, M, y + Inches(2.52), Inches(11.8), Inches(1.1),
          [[("跳了 +1（封顶 11），没跳 −1（封底 00）。预测 = 最高位。",
             17, False, INK)],
           [("要连续错两次，预测方向才会翻转。", 19.5, True, RED)]],
          spacing=1.42)

    T.note(s, M, y + Inches(3.66), CONTENT_W,
           "这既是它抗噪声的来源，也是它的固有局限。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 24 手推 4/7
    s = T.blank(prs)
    y = T.head(s, "手推 T T T N N N N：每 7 次错 4 次", kicker="任务 4　手算",
               accent=ACC)

    T.txt(s, M, y, Inches(7.4), Inches(0.44),
          [[("稳态循环：SN→WN→WT→ST→WT→WN→SN，共 7 拍。",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.56), Inches(7.4), [
        ["#", "真实", "计数器（前）", "预测", "结果"],
        ["1", "T", "SN　00", "N", "✗ 错"],
        ["2", "T", "WN　01", "N", "✗ 错"],
        ["3", "T", "WT　10", "T", "✓ 对"],
        ["4", "N", "ST　11", "T", "✗ 错"],
        ["5", "N", "WT　10", "T", "✗ 错"],
        ["6", "N", "WN　01", "N", "✓ 对"],
        ["7", "N", "SN　00", "N", "✓ 对"],
    ], col_w=[0.8, 1.3, 2.2, 1.4, 1.7], size=13, head_size=12,
        row_h=Inches(0.36), hi_rows=(1, 2, 4, 5), hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER] * 5)

    T.stat(s, Inches(8.50), y + Inches(0.56), Inches(4.08), "4 / 7",
           "稳态下每 7 次错 4 次", color=ACC, size=46,
           sub="= 57.14%。这是课本模型给出的预测，\n仅针对 branchy 中的这一条 if。")

    T.card(s, Inches(8.50), y + Inches(2.40), Inches(4.08), Inches(1.06),
           fill="FBEADD")
    T.txt(s, Inches(8.72), y + Inches(2.56), Inches(3.64), Inches(0.8),
          [[("折算到 branchy 的全部提交分支", 13, True, INK)],
           [("4/7 × 204,800/409,701 = 28.571%", 13.5, True, ACC, True)]],
          spacing=1.35)

    T.txt(s, M, y + Inches(3.68), Inches(11.8), Inches(0.5),
          [[("记住这个 28.571%，下一页用它与 gem5 实测结果对照。",
             18.5, True, INK)]])
    T.foot(s, FOOT)

    # ======================================================== 25 对质
    s = T.blank(prs)
    y = T.head(s, "手算得 28.571%，实测得 42.849%", kicker="任务 4　对照　★★",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("branchy mode 2（周期 7），local 预测器，默认 width 8。"
             "将预测值与实测值并列：", 16, False, INK)]])

    for k, (val, lab, sub, col) in enumerate([
        ("28.571%", "手算的预测值", "课本的 2 bit 状态机推演，\n每 7 次错 4 次。",
         INK_SOFT),
        ("42.849%", "gem5 实测 bp_miss_rate",
         "同一个 pattern，\n同一个 local 预测器。", RED),
        ("1.500", "实测 ÷ 预测", "不是 1.03，也不是 1.2，\n而是一个整齐的分数。",
         ACC),
    ]):
        T.stat(s, M + Inches(4.05) * k, y + Inches(0.76), Inches(3.7),
               val, lab, color=col, size=44, sub=sub)

    T.txt(s, M, y + Inches(2.60), Inches(11.8), Inches(1.6),
          [[("1.500 = 6/7 ÷ 4/7。分母相同，分子由 4 变为 6。",
             17, False, INK)],
           [("反算：42.849% × 409,701 = 175,554 次；÷ 204,800 = 85.72%。",
             17, False, INK)],
           [("状态机推演本身正确，错的是「每 7 次错几次」中的分子。",
             20, True, RED)]], spacing=1.40)
    T.foot(s, FOOT)

    # ======================================================== 26 假设
    s = T.blank(prs)
    y = T.head(s, "模型没错，是 k 错了", kicker="任务 4　假设", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("能同时解释「推演逐条正确」和「实测是 6/7」的，只有一个假设：",
             16.5, False, INK)]])

    cw = (CONTENT_W - Inches(0.5)) / 2
    yc = y + Inches(0.56)
    for k, (ttl, body, col, fill) in enumerate([
        ("假设", "2 bit 计数器只在分支提交时更新。"
                "被 squash 掉的那次误预测，它无法观测到。", ACC, "FBEADD"),
        ("可检验的推论", "机器越宽，一次误预测时在飞的指令越多，"
                        "未被学习的就越多 —— 同一 pattern 的 k 应随宽度上升。",
         GREEN, GREEN_DIM),
    ]):
        xx = M + (cw + Inches(0.5)) * k
        T.card(s, xx, yc, cw, Inches(1.72), fill=fill)
        T.txt(s, xx + Inches(0.34), yc + Inches(0.24), cw - Inches(0.68),
              Inches(1.3),
              [[(ttl, 17, True, col)],
               [(body, 14.5, False, INK)]], spacing=1.36)

    T.txt(s, M, y + Inches(2.56), Inches(11.8), Inches(1.1),
          [[("这个假设可以被证伪：若 k 不随宽度变化，它即被推翻。",
             17, False, INK)],
           [("任务 4d 就是这个判决实验。", 20, True, RED)]], spacing=1.42)

    T.note(s, M, y + Inches(3.72), CONTENT_W,
           "可证伪，才构成假设；否则只是猜测。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")
    T.foot(s, FOOT)

    # ======================================================== 27 判决实验
    s = T.blank(prs)
    y = T.head(s, "机器越宽，同一个 pattern 错得越多",
               kicker="任务 4d　判决　★★", accent=ACC)

    T.txt(s, M, y, CONTENT_W, Inches(0.44),
          [[("branchy mode 2 + local，只扫宽度。k 由 bp_miss_rate 反算：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.56), CONTENT_W, [
        ["width", "cycles", "bp_miss_rate", "折算 k / 7", "squashed 指令",
         "squashed ÷ committed"],
        ["1", "3,686,981", "28.571%", "4 / 7", "789,706", "0.519"],
        ["2", "2,750,898", "35.710%", "5 / 7", "1,228,954", "0.808"],
        ["3", "3,014,072", "42.849%", "6 / 7", "2,281,931", "1.500"],
        ["4", "3,101,663", "42.849%", "6 / 7", "3,568,956", "2.345"],
        ["6", "3,013,686", "42.849%", "6 / 7", "5,148,067", "3.383"],
        ["8", "2,955,335", "42.849%", "6 / 7", "6,758,153", "4.441"],
    ], col_w=[1.1, 2.0, 2.0, 1.5, 2.2, 3.033], size=13, head_size=12,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3, 4, 5), hi_rows=(1,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.txt(s, M, y + Inches(3.74), Inches(11.8), Inches(0.5),
          [[("width = 1 实测 28.571%，与手算完全一致；宽度增加后，"
             "k 从 4 上升到 6。", 18.5, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 28 对照组
    s = T.blank(prs)
    y = T.head(s, "是否窄机器本身就更准确？", kicker="任务 4d　对照组　★",
               accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("同一台机器扫宽度，只换数据：mode 2 有规律，mode 0 无规律。",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.58), Inches(8.5), [
        ["width", "mode 2　周期 7", "mode 0　随机数据"],
        ["1", "28.571%", "24.617%"],
        ["2", "35.710%", "24.495%"],
        ["3", "42.849%", "24.788%"],
        ["4", "42.849%", "24.458%"],
        ["6", "42.849%", "24.581%"],
        ["8", "42.849%", "24.861%"],
    ], col_w=[1.5, 3.5, 3.5], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2),
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.50), Inches(3.13), "0.403pp",
           "随机数据的全部极差", color=INK_SOFT, size=38,
           sub="不单调：1→2 降，2→3 升，\n3→4 又降。没有趋势。")

    T.txt(s, Inches(9.45), y + Inches(2.40), Inches(3.13), Inches(1.1),
          [[("若窄机器本身更准确，", 13.5, False, INK)],
           [("随机数据上应出现相同趋势。", 13.5, False, INK)],
           [("实测没有。", 15, True, RED)]], spacing=1.35)

    T.txt(s, M, y + Inches(3.76), Inches(11.8), Inches(0.5),
          [[("唯一随宽度变化的是 mode 2 —— 即具有规律、可被学习的 pattern。",
             18.5, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 29 8 打不过 2
    s = T.blank(prs)
    y = T.head(s, "8 发射的核，跑不过 2 发射的",
               kicker="任务 4d　判决结果　★★★", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("把 mode 2 那一列的周期数画出来（越短越快）：",
             16, False, INK)]])

    hbars(s, M, y + Inches(0.62), Inches(8.5), [
        ("width 1", 3686981, INK_SOFT, "3,686,981"),
        ("width 2", 2750898, GREEN, "2,750,898"),
        ("width 3", 3014072, ACC, "3,014,072"),
        ("width 4", 3101663, RED, "3,101,663"),
        ("width 6", 3013686, ACC, "3,013,686"),
        ("width 8", 2955335, ACC, "2,955,335"),
    ], bar_h=Inches(0.34), gap=Inches(0.16), label_w=Inches(1.5),
        val_w=Inches(1.85), label_size=13.5, value_size=12.5)

    for k, (val, lab, col) in enumerate([
        ("2,750,898", "width 2　最快", GREEN),
        ("+12.75%", "width 4 比它慢", RED),
        ("+7.44%", "width 8 比它慢", ACC),
    ]):
        yy = y + Inches(0.62) + Inches(0.98) * k
        T.txt(s, Inches(9.45), yy, Inches(3.13), Inches(0.5),
              [(val, 26, True, col, True)])
        T.txt(s, Inches(9.45), yy + Inches(0.44), Inches(3.13), Inches(0.32),
              [(lab, 12.5, True, INK)])

    T.txt(s, M, y + Inches(3.68), Inches(11.8), Inches(0.5),
          [[("同一份机器码，同一个 CPU。把机器变宽，程序反而变慢。",
             19.5, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 30 源码
    s = T.blank(prs)
    y = T.head(s, "为什么 k 会变：证据在两个文件里", kicker="任务 4e　源码",
               accent=ACC)

    T.code(s, M, y + Inches(0.32), Inches(5.66), [
        "// src/cpu/pred/2bit_local.cc",
        "void LocalBP::update(ThreadID tid, Addr pc,",
        "        bool taken, void *hist,",
        "        bool squashed, ...)",
        "{",
        "    if (squashed) {",
        "        return;      // 误预测时不更新",
        "    }",
    ], size=12, hi=(5, 6))

    T.code(s, Inches(6.92), y + Inches(0.32), Inches(5.66), [
        "// src/cpu/o3/fetch.cc   (~941)",
        "// 仅 commit 送来的信号会触发 update",
        "branchPred->update(",
        "    fromCommit->commitInfo[tid].doneSeqNum,",
        "    tid);",
    ], size=12, hi=(2,))

    T.txt(s, Inches(6.92), y + Inches(2.34), Inches(5.66), Inches(1.0),
          [[("squash 掉的那条路径上，计数器不更新。", 15.5, False, INK)],
           [("它只从「已经提交」的分支中学习。", 15.5, True, ACC)]],
          spacing=1.42)

    T.txt(s, M, y + Inches(3.60), Inches(11.8), Inches(0.5),
          [[("机器越宽，在飞的误预测越多，未被学习的就越多 —— k 由 4/7 升至 6/7。",
             19, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 31 punch
    T.punch(prs,
            [("2 bit 计数器", False),
             ("只在分支提交时更新。", True),
             ("在飞的那些误预测，它一次都学不到。", False)],
            sub="这就是手算的 4/7 和实测的 6/7 之间，那 1.500 倍的全部来源。",
            accent=ACC)

    # ======================================================== 32 §05
    T.section(prs, "05", "同一个部件，两个负载两种价值",
              "任务 3、5、6 —— 分支预测器的价值由负载数据决定", accent=ACC)

    # ======================================================== 33 qnn 噪声
    s = T.blank(prs)
    y = T.head(s, "在 qnn 上，五个预测器全是噪声", kicker="任务 3a",
               accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("只改 --bp，其余参数与基线 width 8 完全一致：", 16, False, INK)]])

    T.table(s, M, y + Inches(0.58), Inches(8.5), [
        ["预测器", "cycles", "bp_miss_rate"],
        ["local", "1,099,337", "0.171%"],
        ["bimode", "1,102,270", "0.202%"],
        ["tournament", "1,099,658", "0.175%"],
        ["tage", "1,098,099", "0.165%"],
        ["ltage", "1,097,675", "0.158%"],
    ], col_w=[3.0, 2.8, 2.7], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2),
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.52), Inches(3.13), "0.417%",
           "最差到最好的周期差", color=INK_SOFT, size=40,
           sub="噪声地板是 0.1%。\n这张表上没有一行\n是可以解释的。")

    T.txt(s, M, y + Inches(3.36), Inches(11.8), Inches(1.0),
          [[("qnn 里 99.8% 的分支都是那两层规整的循环，任何预测器都能命中。",
             16.5, False, INK)],
           [("在 qnn 上更换分支预测器没有任何收益。低于噪声地板的差异不构成结论。",
             19.5, True, RED)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 34 三组数据
    s = T.blank(prs)
    y = T.head(s, "同一份机器码，三组数据", kicker="任务 3b　branchy",
               accent=ACC)

    T.txt(s, M, y, CONTENT_W, Inches(0.44),
          [[("同一个 branchy 可执行文件，只改运行时传入的数据模式：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.62), CONTENT_W, [
        ["数据模式", "local", "bimode", "tournament", "tage"],
        ["mode 0　随机", "1,915,438", "1,928,302", "1,244,425", "843,916"],
        ["mode 1　排序", "230,909", "227,346", "227,388", "227,068"],
        ["mode 2　周期 7", "2,955,335", "235,300", "235,010", "235,071"],
    ], col_w=[3.033, 2.2, 2.2, 2.2, 2.2], size=13.5, head_size=12.5,
        row_h=Inches(0.50), mono_cols=(1, 2, 3, 4), hi_rows=(3,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])

    T.note(s, M, y + Inches(2.88), CONTENT_W,
           "mode 只改数组内容，机器码逐字节相同。",
           color=ACC, fill=PAPER_DIM, size=15, icon="※")

    T.txt(s, M, y + Inches(3.72), Inches(11.8), Inches(0.5),
          [[("同一个 local：最好 230,909，最差 2,955,335。差 12.8 倍。"
             "变的只有数据。", 19, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 35 12.58 倍
    s = T.blank(prs)
    y = T.head(s, "mode 2：local 慢了 12.58 倍", kicker="任务 3b　判决　★★",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("周期 7 的模式，2 bit 本地历史无法捕获；带全局历史的可直接命中：",
             16, False, INK)]])

    hbars(s, M, y + Inches(0.70), Inches(8.5), [
        ("local", 2955335, RED, "2,955,335"),
        ("bimode", 235300, GREEN, "235,300"),
        ("tournament", 235010, GREEN, "235,010"),
        ("tage", 235071, GREEN, "235,071"),
    ], bar_h=Inches(0.40), gap=Inches(0.22), label_w=Inches(1.7),
        val_w=Inches(1.85), label_size=13.5, value_size=12.5)

    T.stat(s, Inches(9.45), y + Inches(0.62), Inches(3.13), "12.58×",
           "local ÷ tournament", color=ACC, size=44,
           sub="同一台 CPU，同一份机器码。\n只是把数组换成了周期 7。")

    T.txt(s, Inches(9.45), y + Inches(2.30), Inches(3.13), Inches(1.0),
          [[("误预测率", 13, True, INK)],
           [("local        42.849%", 13, True, RED, True)],
           [("tournament    0.016%", 13, True, GREEN, True)]], spacing=1.3)

    T.txt(s, M, y + Inches(3.52), Inches(11.8), Inches(0.5),
          [[("预测器的价值不由参数表决定，而由输入数据的特征决定。",
             19.5, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 36 宽度×预测器
    s = T.blank(prs)
    y = T.head(s, "宽度的收益，要由预测器来兑现", kicker="任务 5　宽度 × 预测器",
               accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("branchy mode 0 随机数据，local 与 tage 各扫一遍宽度：",
             16, False, INK)]])

    T.table(s, M, y + Inches(0.62), Inches(8.5), [
        ["width", "local ÷ tage", "local squashed", "每次误预测丢弃"],
        ["1", "1.52×", "667,154", "6.6 条"],
        ["2", "1.61×", "1,011,707", "10.1 条"],
        ["4", "1.99×", "2,198,665", "21.9 条"],
        ["8", "2.27×", "4,391,563", "43.1 条"],
    ], col_w=[1.4, 2.3, 2.5, 2.3], size=13.5, head_size=12.5,
        row_h=Inches(0.44), mono_cols=(0, 1, 2), hi_rows=(4,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.40), Inches(3.13), "1.76×",
           "local：w1 → w8", color=INK_SOFT, size=32,
           sub="宽度增至 8 倍，\n性能仅提升 1.76 倍。")
    T.stat(s, Inches(9.45), y + Inches(1.96), Inches(3.13), "2.63×",
           "tage：w1 → w8", color=GREEN, size=32,
           sub="同样的宽度，\n更换预测器可兑现更多。")

    T.txt(s, M, y + Inches(3.56), Inches(11.8), Inches(0.5),
          [[("预测器不准，加大宽度只会放大无效执行：width 8 每次误预测丢弃 43.1 条。",
             19, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 37 BTB
    s = T.blank(prs)
    y = T.head(s, "BTB 只要 32 项就够了", kicker="任务 6　BTB", accent=ACC)

    T.txt(s, M, y, Inches(8.5), Inches(0.44),
          [[("固定 tournament 预测器，只扫 BTB 项数：", 16, False, INK)]])

    T.table(s, M, y + Inches(0.60), Inches(8.5), [
        ["btb 项数", "cycles", "bp_miss_btb", "bp_miss_predictor"],
        ["4", "1,119,576", "2,355", "1,125"],
        ["8", "1,101,610", "497", "1,183"],
        ["16", "1,100,548", "165", "1,361"],
        ["32", "1,100,029", "17", "1,422"],
        ["4096", "1,099,658", "10", "1,432"],
    ], col_w=[1.7, 2.2, 2.1, 2.5], size=13.5, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3), hi_rows=(4,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT])

    T.stat(s, Inches(9.45), y + Inches(0.54), Inches(3.13), "17",
           "整个 qnn 的活跃静态分支", color=ACC, size=50,
           sub="32 项直接映射的 BTB\n即可容纳。再大仅减少\n7 次冲突。")

    T.txt(s, M, y + Inches(3.38), Inches(11.8), Inches(1.0),
          [[("bp_miss_predictor 从头到尾几乎不动（1,125 → 1,432）："
             "BTB 增大不会提升方向预测的准确度。", 16.5, False, INK)],
           [("btb_hit_rate 衡量「是否查得到」，bp_miss_btb 衡量「是否因此出错」。",
             18, True, ACC)]], spacing=1.42)
    T.foot(s, FOOT)

    # ======================================================== 38 §06
    T.section(prs, "06", "全部加大，总收益是多少",
              "任务 7 —— 把五步收益叠加，检验能否翻倍", accent=ACC)

    # ======================================================== 39 全都加
    s = T.blank(prs)
    y = T.head(s, "全部加大，合计只有 +20.74%", kicker="任务 7　★★", accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.4),
          [[("把前面每一步的最优取值全部叠加，与基线 width 8 对比：",
             16, False, INK)]])

    for k, (val, lab, sub, col) in enumerate([
        ("+20.74%", "IPC　5.2756 → 6.3699", "资源全部翻倍之后的\n全部收益。", ACC),
        ("−17.18%", "周期　1,099,658 → 910,749", "累计降幅仅此而已。", GREEN),
        ("IQ", "最后剩下的瓶颈", "58,489 次满，\n此时为最大满信号。", RED),
    ]):
        T.stat(s, M + Inches(4.05) * k, y + Inches(0.54), Inches(3.7),
               val, lab, color=col, size=38, sub=sub)

    T.table(s, M, y + Inches(2.24), CONTENT_W, [
        ["满信号", "基线 width 8", "任务 7 全开", "读法"],
        ["lq_full_events", "207,625", "0", "彻底消失"],
        ["iq_full_events", "71,066", "58,489", "上升为最大满信号"],
        ["rob_full_events", "0", "126", "开始出现"],
        ["mispredicts", "1,442", "305", "来自 tage_sc_l"],
    ], col_w=[2.7, 2.4, 2.3, 4.433], size=13, head_size=12.5,
        row_h=Inches(0.40), mono_cols=(0, 1, 2), hi_rows=(2,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT,
                PP_ALIGN.LEFT])
    T.foot(s, FOOT)

    # ======================================================== 40 阶梯
    s = T.blank(prs)
    y = T.head(s, "五步阶梯：每一步的收益来源", kicker="任务 7　分解",
               accent=ACC)

    T.txt(s, M, y, CONTENT_W, Inches(0.44),
          [[("每一步都在前一步的基础上叠加，不回退：", 16, False, INK)]])

    T.table(s, M, y + Inches(0.56), CONTENT_W, [
        ["步", "加大的资源", "cycles", "相对上一步", "新的最大满信号"],
        ["0", "基线 width 8", "1,099,658", "—", "lq_full 207,625"],
        ["1", "--lq 64", "1,014,232", "−7.77%", "iq_full 130,426"],
        ["2", "--iq 128", "976,819", "−3.69%", "rob_full 68,147"],
        ["3", "--rob 256", "923,129", "−5.50%", "lq_full 60,859"],
        ["4", "--lq 128 --sq 64 --int-regs 512", "924,501", "+0.15%",
         "iq_full 58,110"],
        ["5", "--bp tage_sc_l", "910,749", "−1.49%", "iq_full 58,489"],
    ], col_w=[0.8, 4.0, 2.0, 2.0, 3.033], size=13, head_size=12.5,
        row_h=Inches(0.42), mono_cols=(0, 1, 2, 3, 4), hi_rows=(5,),
        hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT,
                PP_ALIGN.RIGHT, PP_ALIGN.LEFT])

    T.txt(s, M, y + Inches(3.74), Inches(11.8), Inches(0.5),
          [[("第 4 步加大的资源最多，收益却为负 —— 这些资源并不是瓶颈。",
             18.5, True, RED)]])
    T.foot(s, FOOT)

    # ======================================================== 41 设计建议
    s = T.blank(prs)
    y = T.head(s, "如果只能改一处，改哪里", kicker="任务 7　设计建议",
               accent=ACC)

    T.txt(s, M, y, Inches(11.8), Inches(0.44),
          [[("交付物必须包含这一节，且每一条都要有 stats 支撑：",
             16.5, False, INK)]])

    cw = (CONTENT_W - Inches(0.4) * 2) / 3
    yc = y + Inches(0.66)
    # 卡片正文手动断成两段：让每行都在标点处收尾，避免「代价」被拆开。
    for k, (ttl, l1, l2, col, fill) in enumerate([
        ("先改 LQ", "207,625 次满，一步 −7.77%。", "代价仅 32 个表项。",
         RED, RED_DIM),
        ("IQ 最后再动", "唤醒 / 选择逻辑约 O(N²)，", "代价最高的表正是最后的瓶颈。",
         ACC, "FBEADD"),
        ("宽度不必再加", "width 8 的兑现率只有 66.3%，", "继续加宽没有收益。",
         GREEN, GREEN_DIM),
    ]):
        xx = M + (cw + Inches(0.4)) * k
        T.card(s, xx, yc, cw, Inches(1.74), fill=fill)
        T.txt(s, xx + Inches(0.34), yc + Inches(0.24), cw - Inches(0.68),
              Inches(1.3),
              [[(ttl, 17, True, col)],
               [(l1, 14, False, INK)],
               [(l2, 14, False, INK)]], spacing=1.4)

    T.txt(s, M, y + Inches(2.72), Inches(11.8), Inches(1.6),
          [[("这一整圈走完，累计 +20.74%。资源还可继续加大，但曲线已经平坦。",
             17, False, INK)],
           [("若要再快一倍，只能减少指令数本身：", 17, False, INK)],
           [("把 dot_i8 的整个内积循环替换为一条指令。—— 这就是实验五。",
             21, True, RED)]], spacing=1.40)
    T.foot(s, FOOT)

    # ======================================================== 42 判分
    s = T.blank(prs)
    y = T.head(s, "交什么，怎么判", kicker="评分", accent=ACC)

    T.txt(s, M, y, Inches(7.4), Inches(0.44),
          [[("五个板块共 100 分，另设附加分与反向扣分：", 16, False, INK)]])

    T.table(s, M, y + Inches(0.56), Inches(7.4), [
        ["板块", "内容", "分"],
        ["A", "任务 1 + 2　三张表扫描与瓶颈迁移", "25"],
        ["B", "任务 3　预测器横评（含 branchy）", "15"],
        ["C", "任务 4　手算对照与判决实验", "30"],
        ["D", "任务 5 / 6 / 7　宽度×预测器、BTB、全开", "20"],
        ["E", "思考题", "10"],
        ["F", "附加分", "+10 上限"],
        ["G", "反向扣分", "−10 下限"],
    ], col_w=[0.9, 4.9, 1.6], size=13, head_size=12.5,
        row_h=Inches(0.38), hi_rows=(3,), hi_fill="FBEADD",
        aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT])

    T.card(s, Inches(8.50), y + Inches(0.56), Inches(4.08), Inches(3.06),
           fill=RED_DIM)
    T.txt(s, Inches(8.78), y + Inches(0.76), Inches(3.52), Inches(0.44),
          [("一票否决", 18, True, RED)])
    for k, t in enumerate([
        "2c 缺对照组 → 该 10 分不计",
        "任务 4 缺随机对照组 → C 板块 0 分",
        "缺任务 3a → B 板块减半",
        "交付物缺设计建议 → D ≤ 10 分",
    ]):
        T.txt(s, Inches(8.78), y + Inches(1.30) + Inches(0.55) * k,
              Inches(3.52), Inches(0.44), [(t, 13.5, False, INK)])

    T.txt(s, M, y + Inches(3.84), Inches(11.8), Inches(0.5),
          [[("按分析质量给分，不按「跑通」给分。数据不一致不扣分，"
             "无法给出解释才扣分。", 17, False, INK)]])
    T.foot(s, FOOT)

    # ======================================================== 43 一页纸
    s = T.blank(prs, dark=True)
    y = T.head(s, "一页纸", kicker="实验四", dark=True, accent=ACC)

    for k, t in enumerate([
        "乱序核有三张表：ROB、IQ、LQ / SQ。谁的 Full 事件最多，谁就是瓶颈。",
        "放开一张，瓶颈转移到下一张，并且会绕回原点。全部加大合计 +20.74%。",
        "一次只放开一个资源，否则测到的是另一个部件的上限。",
        "l1d_misses 增加 3.17 倍，l1d_mshr_misses 完全不变 —— 增加的是 MLP。",
        "2 bit 计数器只在提交时更新：机器越宽，学不到的越多，k 由 4/7 升至 6/7。",
        "8 发射慢于 2 发射。预测器的价值由数据决定，不由参数表决定。",
    ]):
        yy = y + Inches(0.20) + Inches(0.58) * k
        T.txt(s, M, yy, Inches(0.5), Inches(0.44),
              [("%02d" % (k + 1), 15, True, ACC, True)])
        T.txt(s, M + Inches(0.62), yy, Inches(11.2), Inches(0.44),
              [(t, 15.5, False, "E6E9EC")])

    T.txt(s, M, y + Inches(3.76), Inches(11.8), Inches(0.55),
          [[("下一次：把 dot_i8 的整个内积循环，替换为一条指令。",
             20, True, ACC)]])
    T.foot(s, FOOT, dark=True)

    return prs


if __name__ == "__main__":
    prs = build()
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    print("wrote %s  (%d slides)" % (out, len(prs.slides._sldIdLst)))
