# -*- coding: utf-8 -*-
"""实验五操作步骤。不覆盖 labs/lab5/幻灯片.pptx。

    python _tools/ppt/steps_lab5.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验五　操作步骤"
SEED = '"8 0xNNNN"'


def build():
    d = Deck(5, FOOT)
    d.cover(
        "软硬件协同 I：自定义指令",
        "要交的决定：加上 dotp8 之后，程序快几倍。\n"
        "gem5 只安排编译一次，约 7 分钟。编译开始就去做任务 4，不要干等。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "checksum 对不上，后面全部不算",
                "先把指令数算死，再改译码器。编译的 7 分钟用来写 C，不要干等。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1 ★", "先算账：指令数预测到个位", "15", "动手前写下的那个数"],
        ["2", "在 decoder.isa 里找空 opcode", "15", "custom-0 的两个编码"],
        ["3", "写译码器，开始编译", "40", "scons 通过"],
        ["4", "与编译并行：改 DOTP8_ACC==9", "30", "反汇编 + may_alias 的 diff"],
        ["5 ★", "七个二进制的 checksum", "5", "七行逐位相同"],
        ["6 ★★", "主表、延迟扫描、66 字节", "55", "三组单变量对照"],
        ["7 ★", "回答硬件团队的三个问题", "20", "三张表"],
    ], [1.2, 5.2, 1.1, 3.8], row_h=0.38, size=13, aligns=[L, L, L, L])
    s.callout("0xNNNN 换成学号后四位。小于 0.1% 写成没有差异。该逐位相同的地方差 1 个周期就是错。和别人只比比值，不比绝对值。",
              kind="warn")

    s = d.slide("基线 qnn 还没有就先编", "有了就不要重编它",
                "仓库里没有 bench/bin/riscv/qnn。没有 gem5.opt 时，后面的 scons 是全量。")
    s.code([
        "cd ~/cssys",
        "test -x gem5/build/RISCV/gem5.opt || (cd gem5 && scons build/RISCV/gem5.opt -j8)",
        "test -x bench/bin/riscv/qnn || (cd bench && make && cd ..)",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn",
    ])
    s.why("make 只编标量基线。dotp8 那六个对照在任务 3 编译开始之后再 make dotp8。qnn 的 md5 从这一步记下来，后面变了就是改错文件了。没有 gem5.opt 时，scons 要几十分钟，不是指导书里那 7 分钟。")

    s = d.slide("只改两个文件", "基线 qnn 一个字节都不许动",
                "只改译码器和 qnn.c 里 ACC==9 那一支。基线 qnn 的 md5 不能变。")
    s.steps([
        "gem5/src/arch/riscv/isa/decoder.isa ：任务 3 加约 12 行。先备份。",
        "bench/src/qnn.c ：只改 #elif DOTP8_ACC == 9 那个分支。",
        "编完做 md5sum bench/bin/riscv/qnn ，和实验一的记录对一下。变了就是改错文件了。",
    ])
    s.code([
        "cp gem5/src/arch/riscv/isa/decoder.isa \\",
        "   gem5/src/arch/riscv/isa/decoder.isa.bak",
        "cd bench && make dotp8 && make dotp8my && cd ..",
        "cd gem5 && time scons build/RISCV/gem5.opt -j8 && cd ..",
    ])
    s.text("性能测量一律 --cpu o3 --dotp8-lat 3。--dotp8-lat 只对 o3 有效，atomic / timing 眼里每条指令都是 1 拍。",
           size=14)
    s.why("decoder.isa 是所有 CPU 共用的，改一处，atomic 和 o3 都认识这条指令。但延迟只有 o3 有功能单元的概念。checksum 用 atomic 是为了快，性能必须用 o3，否则每条指令都是 1 拍，延迟扫描没有意义。")

    s = d.slide("六个对照，三组单变量", "认不出这三组，任务 6 拿不到高分",
                "这六个二进制每次只差一个变量：累加器个数，或者循环体字节数。")
    s.table([
        ["二进制", "宏", "累加器", "展开", "拿它和谁比"],
        ["qnn", "标量基线", "1", "无", "一切的分母"],
        ["qnn_dotp8my", "DOTP8_ACC=9 你写的", "你定", "你定", "你自己的实现"],
        ["qnn_dotp8", "ACC=1", "1", "无", "主表、延迟"],
        ["qnn_dotp8u4", "ACC=1 展开 4", "1", "4×", "对 x4：只差累加器个数"],
        ["qnn_dotp8x2", "ACC=2", "2", "2×", "延迟扫描"],
        ["qnn_dotp8x4", "ACC=4", "4", "4× 共 66B", "对 x4c：只差 6 字节"],
        ["qnn_dotp8x4c", "ACC=4 紧凑", "4", "4× 共 60B", "对 x4"],
    ], [2.5, 2.6, 1.4, 2.2, 2.6], row_h=0.36, size=12, aligns=[L] * 5)
    s.why("展开、累加器个数、循环体跨不跨 64 字节，三件事缠在一起就分不清谁在起作用。u4 和 x4 只差累加器个数，x4 和 x4c 只差 6 字节。任务 6 就用这两对。")

    s = d.slide("任务 1a · 1b · 先算，不许写代码", "内循环占了多少",
                "先反汇编数内循环，再算它占全部指令的百分之几。先不要写代码。")
    s.code([
        "riscv64-linux-gnu-objdump -d --no-show-raw-insn \\",
        "    bench/bin/riscv/qnn | awk '/<dot_i8>:/{f=1} f{print} f&&/ret/{exit}'",
    ], size=13)
    s.ask([
        "从循环头到回边分支一共几条指令？一次迭代干几次乘加？循环体多少字节？地址间隔就是指令长度，别漏掉最后一条。",
        "每个样本的乘加次数 = 784×128 + 128×10 = 101632。8 个样本一共多少次？",
        "内循环一共贡献多少条指令？实验四基线 insts 是 5801400。内循环占百分之几？",
        "Amdahl 上界：内循环变成 0 条指令，指令数最多降到几分之一？",
    ])
    s.why("784×128 + 128×10 = 101632 次乘加，乘 8 个样本。基线内循环大约 7 条指令做 1 次乘加，所以内循环占掉 ROI 里绝大部分指令。dotp8 一条顶 8 次乘加。指令数的上界现在就能算死，周期数不会按同样的比例降。")

    s = d.slide("任务 1c · ★ 这个数会被逐条验收", "写在纸上，签个名，再往下做",
                "预测改写后的总指令数，精确到条。写在纸上再往下做。")
    s.steps([
        "假设改写后的循环体条数和基线一样，只是每次迭代干 8 次乘加。",
        "预测总指令数 = 非循环部分 + 新迭代数 × 每迭代条数。",
        "非循环部分 = 5801400 − 你第 4 问的内循环指令数。",
        "再预测一个你多半会猜错的数：周期数会降到几分之一。签名。任务 6a 验收。",
    ])
    s.callout("预测可以精确到个位。任务 6a 对不上就回来重算，不要用实测去改预测。",
              kind="warn")
    s.why("假设改写后仍是「两条 load + 一条运算 + 指针递增 + 回边」，只是每次迭代做 8 次乘加。总指令数 = 非循环部分 + 新的迭代数 × 每迭代条数。非循环部分 = 5801400 − 你算出的内循环指令数。周期数会降到几分之一，这个数多半会猜错，先签名。")

    s = d.slide("任务 2 · 15 分钟", "找一个空的 opcode",
                "在译码器里找空槽。看清 custom-3 已经被 ROI 那条伪指令占了。")
    s.code([
        "awk 'NR>1 && /^        0x[0-9a-f]+: /' \\",
        "    gem5/src/arch/riscv/isa/decoder.isa | head -40",
    ], size=14)
    s.ask([
        "抄下已被占用的 OPCODE5。32 个槽位空了几个？四个 custom 槽位哪几个还空着？",
        "custom-3（0x1e）被 M5Op 占了。打开 bench.h 的 ROI_BEGIN，再看 formats/m5ops.isa。m5_reset_stats 和你要加的 dotp8，实现机制差在哪，设计意图差在哪？",
        "gem5 占用 custom-3，对「你的二进制能在哪些机器上跑」意味着什么？",
        "本次用 custom-0，funct3=0，funct7=0。写在 decode OPCODE5 里的数是 ____，写在 .insn 里的数是 ____。为什么不一样？",
    ])
    s.why("custom-3 已被实验一的 ROI 伪指令占了。dotp8 用空着的 custom-0。译码器里的编号和 .insn 里的 opcode 不是同一个数。")

    s = d.slide("任务 3a · 写进 decoder.isa", "插在 decode OPCODE5 第一个分派前面",
                "在 custom-0 里加 dotp8：8 个 int8 相乘，累加到 rd 原来的值上。")
    s.steps([
        "按 OPCODE5 的数值顺序放。语义：rd += 8 个 int8 乘积之和，rd 既是源也是目的。",
        "先把 Rd 现在的值读出来，再循环 8 次。字节用 (int8_t)(Rs1_ud >> (k*8))，不要用 Rs1_sd。",
        "累加用 int64_t。最后写回 Rd。OpClass 写 SimdMultAccOp。",
    ])
    s.code([
        "0x02: decode FUNCT3 {",
        "  format ROp {",
        "    0x0: dotp8({{",
        "      /* 读 Rd；8 次取字节、转 int8_t、乘、累加；写回 Rd */",
        "    }}, SimdMultAccOp);",
        "  }",
        "}",
    ], size=14)

    s = d.slide("任务 3a · 写代码之前先回答", "写错就是再等 7 分钟",
                "三个问题答完再编译。编译一开始就去写任务 4 的 C 代码。")
    s.ask([
        "为什么必须用 Rs1_ud 再转 int8_t？用 Rs1_sd 做有符号右移会发生什么？",
        "局部变量为什么用 int64_t？最坏 8 个 127×(−128)，再乘 98 次迭代，int32 会不会溢出？",
        "SimdMultAccOp 如果不写会怎样？用指导书 §1.5 回答。",
    ])
    s.h3("编译一开始就切到任务 4")
    s.code([
        "cd gem5 && time scons build/RISCV/gem5.opt -j8 2>&1 | tail -5 && cd ..",
    ], size=13)
    s.text("报错看 decoder.isa 的行号。常见三种：{{ }} 没配对、少逗号、format 的花括号没闭合。第二次增量编译通常 1～2 分钟。",
           size=14)
    s.why("Rs1_ud 是无符号，右移补 0，再转成 int8_t 才得到 −128～127。用有符号右移，高字节的符号位会污染低字节。8 个 127×(−128) 再乘几十次迭代，累加用 int32 会溢出，所以局部变量用 int64_t。不写 SimdMultAccOp，这条指令就进不了乘法功能单元，延迟参数也不起作用。")

    s = d.slide("任务 4 · 与编译并行", "只改 DOTP8_ACC == 9",
                "只改 ACC==9 那一支，用 DOTP8 宏把内循环换成这条新指令。")
    s.steps([
        "打开 bench/src/qnn.c，找到 #elif DOTP8_ACC == 9。里面现在是标量循环。",
        "改成用文件顶部的 DOTP8(acc, va, vb)。n 是 8 的倍数，不用写尾巴。",
        "cd bench && make dotp8my && cd ..",
        "参考实现 ACC=1/2/4 你看得见。分不在这几行，在 4b 和 4c。",
    ])
    s.callout("qnn_dotp8my 的 md5 和 qnn 一样：你没改到 == 9 那个分支，它默认就是标量循环。",
              kind="warn")
    s.why("DOTP8() 用 .insn 让汇编器发出一条它不认识的指令。objdump 印成 .4byte，是因为反汇编器的 opcode 表里还没有 dotp8 这个名字。模拟器认识、汇编器能发出，中间还差工具链那一环。n 是 8 的倍数，不用写尾巴。")

    s = d.slide("任务 4b · 把 may_alias 拿掉再编一次", "看反汇编，不要信传说",
                "拿掉 may_alias 重编，diff 反汇编。无论有没有差别都要贴进报告。")
    s.code([
        "riscv64-linux-gnu-objdump -d --no-show-raw-insn \\",
        "    bench/bin/riscv/qnn_dotp8my \\",
        "  | awk '/<dot_i8>:/{f=1} f{print} f&&/ret/{exit}' > /tmp/with.txt",
        "# 去掉 may_alias，make dotp8my，再导出 /tmp/without.txt",
        "diff /tmp/with.txt /tmp/without.txt",
    ], size=13)
    s.ask([
        "diff 有区别吗？无论有没有，都把结果贴进报告。",
        "严格别名是让编译器假设两个指针不重叠，从而重排读写。这个循环里有写吗？没有写，它能从「不重叠」里赚到什么？",
        "如果循环里加一条 a[i] = 0，你预期结论会变吗？不必真跑。",
    ])
    s.callout("验证完把 may_alias 加回去。它在语言层面仍然是对的，只是这份代码上看不到后果。",
              kind="info")

    s = d.slide("任务 4c · 手工拆那条 .4byte", "确认寄存器就是 GCC 分配的那三个",
                "把循环里那条 .4byte 拆成字段，核对 rs1、rs2、rd 是不是编译器分配的。")
    s.code([
        "riscv64-linux-gnu-objdump -d --no-show-raw-insn \\",
        "    bench/bin/riscv/qnn_dotp8my \\",
        "  | awk '/<dot_i8>:/{f=1} f{print} f&&/ret/{exit}'",
    ], size=14)
    s.ask([
        "把循环体里那个 0xXXXXXXXX 拆成指导书 §1.2 的六个字段，列成表。",
        "对照同一段里 ld 用的寄存器，确认 rs1 / rs2 / rd 就是 %1 / %2 / %0。",
        "objdump 为什么印 .4byte 而不是 dotp8？汇编器和模拟器都认识了，还差哪一环？",
    ])

    s = d.slide("任务 5 · 5 分钟 · ★一票否决", "七行 checksum 必须逐位相同",
                "七个二进制各跑一次功能。checksum 必须逐位相同，否则不许测性能。")
    s.code([
        "for v in qnn qnn_dotp8my qnn_dotp8 qnn_dotp8u4 \\",
        "         qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do",
        "  printf \"%-14s \" $v",
        "  gem5/build/RISCV/gem5.opt --outdir=/tmp/ck framework/cssys_se.py \\",
        "    --cmd bench/bin/riscv/$v --options " + SEED + " \\",
        "    --cpu atomic 2>/dev/null | grep checksum",
        "done",
    ], size=13)
    s.callout("用 atomic 是因为这里只验正确性。对不上不许往下测。最常见是字节没做有符号扩展，其次是 n/8 写成了 n。报告里必须贴出这七行。没有这七行，全卷作废。",
              kind="warn")
    s.why("七个二进制做的是同一件计算，checksum 必须逐位相同。算错的加速比没有意义。整数加法满足结合律，拆成多个累加器不改变结果；如果是浮点，结合律不成立，checksum 就会分叉。")

    s = d.slide("任务 6a · 15 分钟 · 主表", "七个版本都用 --dotp8-lat 3",
                "七个版本都用 3 拍延迟测一遍。先对指令数，再比周期和访存。")
    s.code([
        "for v in qnn qnn_dotp8my qnn_dotp8 qnn_dotp8u4 \\",
        "         qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do",
        "  python3 framework/sweep.py --name lab5_$v --bench $v \\",
        "    --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --dotp8-lat 3\" --jobs 1",
        "done",
    ], size=14)
    s.text("report 看 insts、cycles、ipc、l1d_mshr_misses，以及取指停顿。",
           size=14)
    s.ask([
        "qnn_dotp8 的 insts 和你任务 1c 预测的那条数，一条不差吗？差了就回去重算。",
        "陷阱一：指令比和加速比差多少？IPC 从多少掉到多少？7 倍指令是怎么变成大约 3 倍性能的？",
        "l1d_mshr_misses 六行各是多少？换了指令集，发到 L2 的访存次数变了吗？",
        "rob_full_events 应全是 0。用实验四的判据说这意味着什么。",
    ])

    s = d.slide("任务 6b · 先看这一对", "展开相同，只差累加器个数",
                "u4 和 x4 展开一样，只差几个累加器。看指令少的那个是不是更慢。")
    s.table([
        ["版本", "累加器", "展开", "指令数", "周期数"],
        ["qnn_dotp8u4", "1", "4×", "少", ""],
        ["qnn_dotp8x4", "4", "4×", "差不多", ""],
    ], [2.8, 1.8, 1.6, 2.2, 2.6], row_h=0.44, size=15, aligns=[L] * 5,
       hi_rows=(1, 2))
    s.why("两个版本展开次数、指令数、访存量都差不多，唯一的差别是累加器个数。单累加器时，下一条 dotp8 必须等上一条写回，周期下界 ≈ 总迭代次数 × lat。多累加器把这条链拆开，硬件延迟才隐藏得住。指令更少的那个，可以更慢。")
    s.ask([
        "指令少的那个，跑得快还是慢？慢了百分之几？报告里必须写明唯一的变量是累加器个数。",
        "手算 qnn_dotp8 的周期下界：dot_i8 被调用几次（每样本 128+10，共 8 个样本）？两种调用的迭代次数（784/8 和 128/8）分开算。总迭代 × lat = 下界。",
        "下界占实测周期的百分之多少？写成：有 ____% 的时间在等上一条 dotp8。",
    ])

    s = d.slide("任务 6b · 延迟扫描是判决实验", "主表的 lat=3 必须和这里逐位相同",
                "把延迟从 1 扫到 8。看单累加器是不是最吃延迟。")
    s.code([
        "for v in qnn_dotp8 qnn_dotp8x2 qnn_dotp8x4c; do",
        "  python3 framework/sweep.py --name lab5_lat_$v --bench $v \\",
        "    --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "    --vary dotp8-lat=1,2,3,4,6,8 --jobs 6",
        "  python3 framework/report.py results/lab5_lat_$v.csv cycles ipc",
        "done",
    ], size=13)
    s.ask([
        "延迟敏感度 = lat=8 的周期 ÷ lat=1 的周期。三个版本各是多少？为什么单累加器最敏感？",
        "看 lat=1 那一行。三个版本的周期应在 5% 以内。写成一句关于软硬件分工的话。",
        "lat=1 的物理含义是什么？8 路 int8 乘加树真能一拍算完吗？用 lat=1 报告加速比，你在向谁隐瞒什么？不许只报这个数。",
    ])

    s = d.slide("任务 6c · 先量循环体字节数", "66B 和 60B，其它全部相同",
                "x4 和 x4c 只差 6 个字节。先量循环体，再看它有没有跨过 64 字节边界。")
    s.code([
        "for v in qnn_dotp8x4 qnn_dotp8x4c; do",
        "  echo \"--- $v ---\"",
        "  riscv64-linux-gnu-objdump -d --no-show-raw-insn \\",
        "      bench/bin/riscv/$v \\",
        "    | awk '/<dot_i8>:/{f=1} f{print} f&&/ret/{exit}'",
        "done",
    ], size=14)
    s.ask([
        "4× 展开的主循环：回边地址 + 指令长度 − 循环头地址。循环头是不是 64 字节对齐？",
        "66 字节那个循环，最后一条指令跨过了哪个地址边界？画一张图。",
        "主表里这两行：指令少了百分之几，周期少了百分之几，取指停顿差几倍？",
        "少 9.8% 的指令换来少约 15.8% 的周期。和陷阱一方向相反，区别在哪？",
        "跑得快的那个 LQ 更满。瓶颈原来在哪，解决之后搬到了哪？",
    ])

    s = d.slide("任务 7 · 问题 1 和 2", "每个数都要写来自哪张表哪一列",
                "用今天的表回答硬件：这条指令值不值得做，以及该做成几拍。")
    s.table([
        ["口径", "数值", "依据"],
        ["指令数降到几分之一", "", ""],
        ["周期数降到几分之一（lat=3）", "", ""],
        ["差额被什么吃掉", "", ""],
        ["发到 L2 的访存次数变化", "", ""],
        ["最好的软件比最差的快多少", "", ""],
    ], [4.6, 2.4, 4.2], row_h=0.36, size=13, aligns=[L, L, L])
    s.text("问题 2：硬件说 lat=1 做不到，lat=3 要加一级流水，lat=6 现在就能做。用延迟扫描填下表，从 3 退到 6 损失多少。",
           size=14)
    s.table([
        ["软件版本", "lat=1", "lat=3", "lat=6", "从 3 退到 6"],
        ["qnn_dotp8", "", "", "", ""],
        ["qnn_dotp8x2", "", "", "", ""],
        ["qnn_dotp8x4c", "", "", "", ""],
    ], [2.8, 1.8, 1.8, 1.8, 2.6], row_h=0.36, size=13, aligns=[L] * 5)

    s = d.slide("任务 7 · 写进报告的三句话", "不许用「应该」「大概」",
                "分软件版本回答延迟该做到几拍，并指出下一步的瓶颈在取数。")
    s.why("软件若用 4 个累加器，延迟从 6 改到 3，周期往往动得很少，那一级流水可以省下来。硬件若只能给 lat=6，软件又写成单累加器，依赖链会把加速吃掉一大块。最快的版本上 l1d_mshr_misses 没变，数据还是靠 ld 取进来的。")
    s.ask([
        "软件保证用 4 累加器时，还需要硬件把延迟从 6 降到 3 吗？省下的那级流水可以拿去干什么？",
        "硬件只能给 lat=6、软件坚持单累加器，相对基线还有加速比吗？去看数。",
        "把上面两问收成一句关于软硬件协同的话，单独成段。",
        "最快的版本瓶颈是谁？主表里 l1d_mshr_misses 在所有版本上是同一个数。再加一条 dotp16 能解决这个瓶颈吗？",
        "要突破这堵墙，硬件必须有一项 dotp8 没有的能力。是什么？这就是实验六要做的事。",
    ])

    s = d.slide("交什么", "七行 checksum 没有，全卷作废",
                "没有七行相同的 checksum，后面的加速比全部不算。")
    s.table([
        ["内容", "分"],
        ["任务 1 的算账（含个位预测）+ 任务 2", "15"],
        ["译码器 + 三个写之前的问答 + 4b/4c", "20"],
        ["任务 5 的七行 checksum", "5"],
        ["任务 6 三个陷阱", "40"],
        ["任务 7 三问", "10"],
        ["思考题", "10"],
    ], [8.4, 1.4], row_h=0.36, size=14, aligns=[L, L])
    s.callout("必须交：动手前的指令数预测、依赖链下界的手算、66/60 字节的边界图、4b 的 diff、全部 CSV 和 decoder.isa 片段。禁止用 lat=1 报加速比而不加说明，禁止只报最好的那个版本。",
              kind="warn")

    return d.save(out_path(5))


if __name__ == "__main__":
    build()
