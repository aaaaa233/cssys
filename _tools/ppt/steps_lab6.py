# -*- coding: utf-8 -*-
"""实验六操作步骤。不覆盖 labs/lab6/幻灯片.pptx。

    python _tools/ppt/steps_lab6.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验六　操作步骤"
SEED = '"8 0xNNNN"'


def build():
    d = Deck(6, FOOT)
    d.cover(
        "软硬件协同 II：加速器集成",
        "要交的决定：接在哪、算力多大、outstanding 多深、软件配合什么。\n"
        "带上实验五的那页建议。编译约 3 分钟，用来做任务 2。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "每跑完一批都要核对 checksum",
                "先让加速器算对，再决定接在哪、算力多大、软件怎么配合。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1 ★", "装加速器、打 TLB 补丁、核对 fence", "35", "四格 checksum 表"],
        ["2 ★", "编译期间把 Roofline 三个坐标算完", "15", "2×4 预测表"],
        ["3 ★★", "挂载点 × pe", "35", "lab6_where_pe"],
        ["4", "outstanding，反推延迟", "25", "lab6_out"],
        ["5 ★★", "batch，把点画上 Roofline", "30", "lab6_batch"],
        ["6 ★★", "Amdahl、L2 交叉、没去内存", "25", "三个意外"],
        ["7 ★", "一页纸，四个决定", "15", "不超过 400 字"],
    ], [1.2, 5.4, 1.1, 3.4], row_h=0.38, size=13, aligns=[L, L, L, L])
    s.callout("checksum 必须等于同一个 seed 下基线 qnn 的值。错了就停。测量统一用 --cpu o3。卡在算力还是带宽，只看 accel_stall_frac。",
              kind="warn")

    s = d.slide("基线 qnn 还没有就先编", "加速器二进制是下一步才编的",
                "仓库里没有可执行文件。qnn 先有，qnn_accel 等任务 1a 的 make accel。")
    s.code([
        "cd ~/cssys",
        "test -x gem5/build/RISCV/gem5.opt || (cd gem5 && scons build/RISCV/gem5.opt -j8)",
        "test -x bench/bin/riscv/qnn || (cd bench && make && cd ..)",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn",
    ])
    s.why("没有 gem5.opt 时，任务 1a 的 scons 是全量编译，要几十分钟，不是 3 分钟。qnn 的 md5 现在记下来。make accel 不会改这个文件。")

    s = d.slide("任务 1a · 装上，打补丁，编译", "编译的 3 分钟去做任务 2",
                "装上加速器并给 MMIO 打上不可缓存。编译的 3 分钟去做任务 2。")
    s.code([
        "cp gem5/src/arch/riscv/tlb.cc gem5/src/arch/riscv/tlb.cc.bak",
        "python3 labs/lab6/src/install_dotp8_accel.py gem5",
        "python3 labs/lab6/src/patch_riscv_tlb.py gem5",
        "cd gem5 && scons build/RISCV/gem5.opt -j8 && cd ..",
        "cd bench && make accel && cd ..",
        "md5sum bench/bin/riscv/qnn",
        "diff gem5/src/arch/riscv/tlb.cc.bak gem5/src/arch/riscv/tlb.cc",
    ], size=14)
    s.callout("基线 qnn 的 md5 应仍是 f2825f24ce6bb3941f732bfb77cf2dbe。变了就是改错文件了。",
              kind="warn")
    s.ask([
        "补丁改了几行？它把 translate() 换成 lookup()，为什么反而少查一次页表？",
        "UNCACHEABLE 和 STRICT_ORDER 各防什么？一个防 Cache，一个防乱序核的投机执行。",
    ])

    s = d.slide("五个二进制", "nofence 是反面教材，只少了一条 fence",
                "先跑通主版本，checksum 必须和同一个种子下的基线 qnn 相同。")
    s.table([
        ["二进制", "用途"],
        ["qnn_accel", "主版本，batch=1"],
        ["qnn_accel_b2 / b4 / b8", "算术强度 ×2 / ×4 / ×8"],
        ["qnn_accel_nofence", "只去掉那条 fence"],
    ], [4.2, 7.0], row_h=0.42, size=15, aligns=[L, L])
    s.text("新参数：--accel off|l2bus|membus ，--accel-pe ，--accel-outstanding ，--accel-start-lat ，--accel-addr（默认 0x40000000，必须和二进制一致）。",
           size=14)
    s.h3("任务 1b · 先跑通这一条")
    s.code([
        "G=gem5/build/RISCV/gem5.opt",
        "$G --outdir=out/lab6/t1 framework/cssys_se.py \\",
        "   --cmd bench/bin/riscv/qnn_accel --options " + SEED + " \\",
        "   --cpu o3 --accel l2bus --accel-pe 32 | grep checksum",
    ], size=13)

    s = d.slide("任务 1c · ★ 四格都要填", "少一条 fence，只在乱序核上算错",
                "两个 CPU、两个二进制，四格 checksum 都要填。看哪一格悄悄算错。")
    s.code([
        "for c in timing o3; do",
        "  for b in qnn_accel qnn_accel_nofence; do",
        "    echo \"== cpu=$c $b\"",
        "    $G --outdir=out/lab6/nf_${c}_${b} framework/cssys_se.py \\",
        "       --cmd bench/bin/riscv/$b --options " + SEED + " \\",
        "       --cpu $c --accel l2bus --accel-pe 32 | grep checksum",
        "  done",
        "done",
    ], size=13)
    s.table([
        ["", "qnn_accel 有 fence", "qnn_accel_nofence"],
        ["timing 顺序", "", ""],
        ["o3 乱序", "", ""],
    ], [2.4, 4.6, 4.2], row_h=0.42, size=14, aligns=[L, L, L], hi_rows=(2,))

    s = d.slide("任务 1c · 写进报告", "这是本次最高的采点之一",
                "解释为什么只有乱序核会算错，以及 volatile 为什么没拦住。")
    s.why([
        "volatile 只保证本线程不会把这几次访问优化掉，不保证乱序核上「store 之后、另一条地址的 load」按程序顺序发生。RISC-V 的 RVWMO 对这种情况没有顺序保证，要靠 fence。",
        "顺序核按程序顺序执行，所以少一条 fence 在 timing 上 checksum 仍是对的。这个错没有报错、没有崩溃，只有 checksum 变了。",
    ])
    s.ask([
        "四格里只有一格是错的。哪一格？",
        "为什么顺序核上没事？用一句话说顺序核和乱序核在这里的区别。",
        "accel_layer() 里六个寄存器写全是 volatile。volatile 保证了什么，为什么没防住这个错误？",
        "这是 gem5 的 bug 还是程序的 bug？查 RVWMO 对「store 后跟一条不同地址的 load」有没有顺序保证。",
        "这个错误没有任何报错。验收流程里必须有什么？",
    ])

    s = d.slide("任务 1d · 选做，多一次编译", "看完一定要把补丁打回去",
                "撤掉 TLB 补丁再跑两个 CPU。看完一定要把补丁打回去并重新编译。")
    s.code([
        "cd gem5 && git checkout -- src/arch/riscv/tlb.cc \\",
        "    && scons build/RISCV/gem5.opt -j8 && cd ..",
        "for c in timing o3; do",
        "  $G --outdir=out/lab6/nopatch_$c framework/cssys_se.py \\",
        "     --cmd bench/bin/riscv/qnn_accel --options " + SEED + " \\",
        "     --cpu $c --accel l2bus --accel-pe 32 | grep checksum",
        "  grep '^system.accel.jobs' out/lab6/nopatch_$c/stats.txt",
        "done",
        "python3 labs/lab6/src/patch_riscv_tlb.py gem5",
        "cd gem5 && scons build/RISCV/gem5.opt -j8 && cd ..",
    ], size=12)

    s = d.slide("任务 1d · 写进报告", "两种 bug，同一个错的 checksum",
                "两种错的 checksum 可以一样。用 accel.jobs 把它们分开。")
    s.why("没打 TLB 补丁时，MMIO 地址被当成普通内存，写进了 Cache，设备一条命令都收不到，system.accel.jobs 是 0。少 fence 时设备收到了命令，只是软件看见的完成顺序错了。两种错的 checksum 可以是同一个数，分开它们要看 jobs，不能只看 checksum。uncacheable 防的是进 Cache，strict order 防的是乱序核上的投机。")
    s.ask([
        "system.accel.jobs 是多少？加速器收到了几条命令？jobs=0 就是 MMIO 写没出 L1。",
        "1c 和 1d 的错误 checksum 是同一个数。只看 checksum 能分开这两种错吗？要看哪个统计量？",
        "1c 只在 o3 上出现，1d 两个 CPU 都出现。各是被什么机制触发的？",
    ])

    s = d.slide("任务 2 · 编译期间做完", "先算屋顶，再跑任何一次性能仿真",
                "先在纸上算算术强度和两条总线的屋顶，再跑任何一次性能仿真。")
    s.ask([
        "一个样本多少次乘加？8 个样本呢？784×128 + 128×10。",
        "batch=1 时加速器要搬多少字节？别忘了第一层的 x（784B）和第二层的 h（128B）。",
        "由上两问算出 batch=1 的算术强度 I。",
        "查 L2XBar 和 SystemXBar 的 width（字节/周期）。命令在下一行。",
        "P = min(Pmax, Bmax × I)。预测 pe = 8/16/32/64 时，两个挂载点各自的 MAC/周期，填 2×4 的表。",
        "从哪一档 pe 开始，两个挂载点会出现可测的差异？写下预测，任务 3 验证。事后补的预测记 0。",
    ])
    s.code([
        "grep -n -A3 'class L2XBar\\|class SystemXBar' \\",
        "    gem5/src/mem/XBar.py | grep -E 'class|width'",
    ], size=14)
    s.why("每周期乘加 = min(pe, 带宽 × 算术强度)。batch=1 时每个字节只用一次，先撞上斜边。")

    s = d.slide("任务 3 · 35 分钟 · ★★", "先确认 8 个点只有一个 checksum",
                "挂载点和 pe 一起扫。先确认 8 个点的 checksum 只有一个值。")
    s.code([
        "python3 framework/sweep.py --name lab6_where_pe \\",
        "    --bench qnn_accel --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" \\",
        "    --vary accel=l2bus,membus --vary accel-pe=8,16,32,64 --jobs 8",
        "grep -h checksum out/sweeps/lab6_where_pe/*/run.log | sort -u",
    ], size=13)
    s.text("要看的列：cycles、accel_job_cycles、accel_macs_per_cycle、accel_bytes_per_cycle、accel_stall_frac、accel_job_frac。",
           size=14)
    s.ask([
        "把实测 MAC/周期填到任务 2 那张 2×4 表旁边。预测对了几格？",
        "pe 8→16、16→32、32→64，两个挂载点各快了多少？pe=64 比 32 快多少说明了什么？",
        "用 accel_stall_frac 把 8 个点分成算力受限和带宽受限。",
    ])

    s = d.slide("任务 3 · 写进报告", "带宽屋顶，以及 IPC 为什么掉了",
                "用 stall_frac 把 8 个点分成算力受限和带宽受限，并解释 IPC 为什么掉。")
    s.why("accel_stall_frac 高，加速器在等数据，pe 再加大周期也几乎不动。stall_frac 接近 0，才是算力不够。指令数可以掉到大约 1/68，周期掉得少得多，因为 CPU 在读 STATUS 时空等，那些周期里几乎没有指令提交，IPC 就低了。")
    s.ask([
        "两个挂载点的实测带宽屋顶（bytes/周期的饱和值）是多少？各达到总线宽度的百分之几？",
        "pe=32 时，整个 ROI 相对实验一基线 qnn 的加速比是多少？accel_job_frac 是多少？两个数放一起说明什么？",
        "指令数掉到大约 1/68，加速比远没有这么多，IPC 也掉了。用一句话解释 IPC 为什么掉。",
    ])

    s = d.slide("任务 4 · 25 分钟", "pe 固定 64，让算力绝不成为瓶颈",
                "算力固定拉满，只改同时在飞的请求数，看带宽在哪一档拐平。")
    s.code([
        "python3 framework/sweep.py --name lab6_out \\",
        "    --bench qnn_accel --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --accel-pe 64\" \\",
        "    --vary accel=l2bus,membus \\",
        "    --vary accel-outstanding=1,2,4,8,16,32 --jobs 12",
    ], size=14)
    s.ask([
        "画 accel_bytes_per_cycle 对 outstanding 的两条曲线。",
        "从 outstanding=1 反推两个挂载点的往返延迟 L。一次请求是 64 字节，L = 64 / B。",
        "用 Little 定律预测 outstanding=2 和 4 的带宽，和实测比，误差多少？",
    ])

    s = d.slide("任务 4 · 写进报告", "拐点在哪，你为什么停在那里",
                "从 outstanding=1 反推延迟，算出拐点，并说明你为什么停在那里。")
    s.why("Little 定律：在飞的请求数 N = 带宽 × 往返延迟。一次请求是 64 字节，所以 outstanding=1 时带宽 B = 64 / L，反推 L = 64 / B。N 超过 L × Bmax / 64 之后总线已经打满，再加 outstanding 只增加面积。pe 固定 64，是为了让算力绝不成为瓶颈，测到的才是纯带宽。")
    s.ask([
        "曲线在哪个 outstanding 拐平？用 N* = L × Bmax / 64 算拐点，和图一致吗？",
        "超过拐点再加 outstanding 有没有用？",
        "两个挂载点的 outstanding 该定多少？答案一样吗？多做的每一项都占面积，你为什么停在那里？",
    ])

    s = d.slide("任务 5 · 30 分钟 · ★★", "8 个点的 checksum 必须全等于基线",
                "换 batch，把同一组权重摊到更多输入上。8 个点的 checksum 仍须相同。")
    s.code([
        "python3 framework/sweep.py --name lab6_batch \\",
        "    --bench qnn_accel --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --accel-pe 32\" \\",
        "    --vary bench=qnn_accel,qnn_accel_b2,qnn_accel_b4,qnn_accel_b8 \\",
        "    --vary accel=l2bus,membus --jobs 8",
    ], size=13)
    s.text("--vary bench= 换的是二进制，不传给 gem5。batch 改了处理顺序，不该改每个样本看到的随机数。checksum 变了就是这件事没做对。",
           size=14)
    s.ask([
        "填：算术强度、bytes/周期、MAC/周期、stall_frac、accel_job_cycles、cycles。",
        "8 个点画到你自己的 Roofline 上（横轴 I，纵轴 MAC/周期），加上两条斜边和一条水平屋顶。点应贴着某一条边。",
        "batch 1→2，accel_job_cycles 少了多少？看 accel_bytes 变成了几分之几。",
    ])

    s = d.slide("任务 5 · 写进报告", "挂载点什么时候值钱",
                "把 8 个点画上 Roofline，说清「接在哪」什么时候还值钱。")
    s.why("batch 变大，同一份权重要服务更多输入，每个字节上的乘加变多。stall_frac 从零点几掉到接近 0 的时候，两条总线谁宽已经不大影响周期。batch 再加大，CPU 那边的收尾开始占时间，周期不一定继续降。")
    s.ask([
        "batch=4 和 8 上，两个挂载点还差多少？和 batch=1 比。「接在哪」什么时候值钱，什么时候不值钱？",
        "stall_frac 从 batch=1 掉到 batch=2，工作点发生了什么变化？",
        "cycles 从 batch=1 到 8 是单调下降的吗？最快是哪一档？为什么继续加 batch 反而变慢？",
    ])

    s = d.slide("任务 6a · Amdahl", "用任务 5 里最快的那个配置",
                "把最快那次切成加速器和 CPU 两半，看加速器再快还有没有用。")
    s.text("T加速器 = accel_job_cycles 。TCPU = cycles − accel_job_cycles 。",
           size=16, bold=True)
    s.why("加速器快到 0，ROI 还剩 TCPU。这就是总加速比的上界。TCPU 里是 infer_batch() 之外的收尾，外加阻塞读 STATUS 的空转。空转不一定必须：若完成改为中断或轮询间隙夹别的工作，CPU 那一半还能再切。")
    s.ask([
        "两个数各是多少，各占百分之几？",
        "假设加速器快到 0 周期，ROI 还剩多少？相对现在还能再快几倍？相对实验一的软件基线，总加速比的上界是多少？",
        "TCPU 里是什么代码？去 qnn.c 里看 infer_batch() 之外还剩什么。",
        "下一步给两个不同方向的方案，各能拿到那个上界的多少。STATUS 是阻塞读，CPU 在加速器干活时空转。这必须这样吗？",
    ])

    s = d.slide("任务 6b · L2 装不下的时候", "先写猜测，再看数据",
                "把 L2 从装得下权重砍到装不下。先猜谁变慢，再看两条曲线在哪交叉。")
    s.code([
        "python3 framework/sweep.py --name lab6_l2 \\",
        "    --bench qnn_accel --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --accel-pe 32\" \\",
        "    --vary accel=l2bus,membus \\",
        "    --vary l2-size=32kB,64kB,128kB,256kB,512kB --jobs 10",
    ], size=13)
    s.text("权重一共约 99KB。看数据之前先写下：32kB 变慢，你认为慢在 CPU 还是慢在加速器。",
           size=15)
    s.ask([
        "画 cycles 对 l2-size 的两条曲线。它们在哪里交叉？和 99KB 是什么关系？",
        "l2=32kB 时哪个挂载点更快？和 256kB 时的结论相反吗？",
    ])

    s = d.slide("任务 6b · 写进报告", "先把 10 行都拆成两半",
                "10 行都拆成加速器和 CPU。看变慢的到底是谁。")
    s.why("走 l2bus 的读会在 L2 里分配一行，12,000 多次流式读灌进一个只有几百行的 L2，把 CPU 还要用的行冲掉。走 membus 的读只被 L2 snoop 一下，不分配。所以 L2 装不下权重时，「更好的挂载点」可以变成更慢的那个。先猜变慢的是 CPU 还是加速器，再看 TCPU 那一列几乎不动。")
    s.ask([
        "10 行全部拆成 T加速器 和 TCPU。列出 10 个 TCPU，它变化了百分之几？和你事先的猜测不一致，就写原来错在哪。",
        "CPU 那一半几乎没动，变慢的是谁？看 l2_misses：l2bus 在 32kB 约 8903，membus 约 35。走 l2bus 的读会在 L2 里分配一行，走 membus 的只被 snoop、不分配。",
        "一句话：加速器挂到 L2 旁边，只在什么条件下是对的？",
    ])

    s = d.slide("任务 6c · 它根本没去内存", "看 ROI，也就是第二段统计",
                "对一下加速器读了多少字节、DRAM 实际读了多少。看数是从哪来的。")
    s.code([
        "awk '/Begin Simulation Statistics/{n++} n==2' \\",
        "    out/sweeps/lab6_where_pe/p006_*/stats.txt | grep -E \\",
        "    'accel.bytesRead|membus.snoopTraffic|dram.bytesRead::total'",
    ], size=12)
    s.ask([
        "bytesRead 约 82 万，DRAM 只有约 1920。这 80 万字节从哪来？看 snoopTraffic。",
        "「接到内存总线 = 从内存取数」是错的。正确的说法是什么？它影响任务 3 的结论吗？",
        "这是模型的缺陷还是真实行为？权重是 CPU 初始化时写进去的，当时在 Cache 里是什么状态？",
        "6c 有一个没说出口的前提。看 membus 在 l2=32kB 时的 dram_bytes（约 44 万）和 256kB 时的（约 1920）。前提是什么？不成立时会怎样？",
    ])
    s.why("接到内存总线不等于从 DRAM 取数。权重还在 Cache 里，读被 snoop 满足。L2 只有 32kB 时这个前提不成立。")

    s = d.slide("任务 7 · ★ 一页纸，不超过 400 字", "四个决定，每个都引用今天的数",
                "用今天的数定四件事：pe、接哪条总线、outstanding、软件必须配合什么。")
    s.why("pe 写到任务 3 里 stall_frac 掉下去的那一档。总线写明只在 batch 还小、还在等带宽的时候有差别。outstanding 写任务 4 曲线拐平的那一档。软件写两件：batch，以及乱序核上那条 fence。")
    s.steps([
        "pe 定多少？为什么停在那里（任务 3）。",
        "接在哪条总线上？这个决定值多少，以及在什么前提下才值（任务 5 第 4 问、任务 6b）。",
        "outstanding 做多深（任务 4）。",
        "软件必须配合的两件事：一件是性能（任务 5），一件是正确性（任务 1c）。",
        "最后加一句「我们没有建模的东西」，至少两条。",
    ])

    s = d.slide("交什么", "没有 checksum 的性能表不算数",
                "每张性能表都要带 checksum。没有它，这张表不算数。")
    s.table([
        ["板块", "分", "考什么"],
        ["任务 1 正确性", "15", "四格表 + 第 3～10 问，一票否决"],
        ["任务 2 纸面预测", "7", "编译期间写完，要有计算过程"],
        ["任务 3 挂载点 × pe", "15", "用 accel_stall_frac 下结论"],
        ["任务 4 Little", "10", "反推延迟、拐点、为什么停"],
        ["任务 5 batch", "18", "Roofline 图 + 挂载点何时值钱"],
        ["任务 6 三个意外", "20", "6b 第 7、9 问和 6c 第 12 问"],
        ["任务 7 一页纸", "8", "六张表压成四个决定"],
        ["思考题", "7", "含给实验七的预测"],
    ], [3.2, 1.0, 6.8], row_h=0.36, size=13, aligns=[L, L, L])

    return d.save(out_path(6))


if __name__ == "__main__":
    build()
