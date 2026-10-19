# -*- coding: utf-8 -*-
"""实验一操作步骤。不覆盖 labs/lab1/幻灯片.pptx。

    python _tools/ppt/steps_lab1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验一　操作步骤"
SEED = '"8 <学号后四位>"'


def build():
    d = Deck(1, FOOT)
    d.cover(
        "性能评价与仿真方法学",
        "要交的决定：后面六次实验用哪个 CPU 模型。\n"
        "每一页只干一步：命令、要填的表、报告里要写的几句话。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "六件事，做完再写声明",
                "按这个表做。前面的数后面还要用，别跳。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1", "跑通，读懂 stats.txt 的三段", "20", "四个统计量"],
        ["2", "ROI：三段占比、加大负载、相减", "30", "四张表"],
        ["3", "四个 CPU 模型各跑一遍", "30", "results/lab1_cpu.csv"],
        ["4 ★", "16kB 和 128kB，谁会让你选错", "30", "results/lab1_fid.csv"],
        ["5", "样本数 2～32，看 IPC 何时稳住", "20", "两张图"],
        ["6 选做", "换成 pchase 再做一次任务 4", "—", "lab1_fid_pchase.csv"],
    ], [1.1, 5.4, 1.1, 3.6], row_h=0.40, size=14,
       aligns=[L, L, L, L])
    s.callout("交一份报告，外加一段不超过 300 字的模型选择声明，以及 results/ 里的 CSV。",
              kind="info")

    s = d.slide("仓库里没有 qnn", "先编译 gem5 和基准程序",
                "克隆下来没有 gem5.opt，也没有 bench/bin/riscv/qnn。编完再跑。")
    s.steps([
        "需要 python3、scons、g++、riscv64-linux-gnu-gcc。缺哪个先装哪个。",
        "gem5 第一次是全量编译，要几十分钟。已经有 gem5.opt 就不要重编。",
        "make 得到 qnn、gemm、pchase、branchy、stream。noroi 和 noalign 是本次对照。",
    ])
    s.code([
        "cd ~/cssys",
        "cd gem5 && scons build/RISCV/gem5.opt -j8 && cd ..",
        "cd bench && make && make noroi && make noalign && cd ..",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn",
    ])
    s.why("ls 能列出这两个文件，编译才算完成。后面的 --cmd bench/bin/riscv/qnn 用的就是这里编出来的二进制。实验二到四继续用这批文件。实验五、六再分别 make dotp8、make accel。")

    s = d.slide("进目录 · 全程用自己的学号", "先把这三条跑通",
                "输出目录就叫 out/lab1。后面的曲线都用你自己的种子。")
    s.steps([
        "尖括号换成学号后四位，不要原样输入。seed 不同，曲线拐点会不同。",
        "小于 0.1% 的差异写成「没有差异」，不许解释。",
        "stats.py 不写段号就是第 1 段，也就是 ROI。0 是启动，2 是收尾。",
    ])
    s.code([
        "cd ~/cssys",
        "export GEM5_BIN=$PWD/gem5/build/RISCV/gem5.opt",
        "$GEM5_BIN --outdir=out/lab1 framework/cssys_se.py \\",
        "    --cmd bench/bin/riscv/qnn --options " + SEED + " --cpu o3",
        "python3 framework/stats.py out/lab1/stats.txt",
        "python3 framework/stats.py out/lab1/stats.txt 0",
    ])
    s.why("gem5 是确定性的：二进制和配置不变，结果就不变。但命令行字符串躺在初始栈上，路径多二十来个字符，栈就平移，Cache 组跟着变，周期能差几十。所以小于 0.1% 一律写成没有差异。")

    s = d.slide("后面每次扫描都用这一对", "sweep 出表，report 看列",
                "单点用 gem5，一组配置用 sweep。比方案看周期，不要只看 IPC。")
    s.code([
        'python3 framework/sweep.py --name 我的扫描 \\',
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --vary cpu=atomic,timing,minor,o3 --jobs 4",
        "python3 framework/report.py results/我的扫描.csv",
    ])
    s.callout("gem5 是单线程。--jobs 不要超过机器的核数，一个进程大约占 1GB 内存。",
              kind="warn")
    s.steps([
        "结果表在 results/<名字>.csv，原始输出在 out/sweeps/<名字>/。",
        "终端没有 stats.txt：先看 run.log，多半是 --cmd 路径错了，或 --options 没加引号。",
    ])
    s.why("两套方案比快慢，写周期数。IPC 单独看会看走眼：实验五把指令数砍掉以后，IPC 下降，周期其实少了。指令数一样的时候（只改 Cache），IPC 才能直接比。")

    s = d.slide("任务 1 · 20 分钟", "跑通，并读懂三段",
                "用 o3 把 qnn 跑通，分清 stats.txt 里三段各是哪段代码。")
    s.steps([
        "用 o3 跑 qnn，样本数 8，带上学号后四位。",
        "打开这次的 stats.txt，数有几段 Begin Simulation Statistics。",
        "用 stats.py 把第 0、1、2 段各打一遍，对照你手工找到的数。",
    ])
    s.code([
        "$GEM5_BIN --outdir=out/lab1 framework/cssys_se.py \\",
        "    --cmd bench/bin/riscv/qnn --options " + SEED + " --cpu o3",
        "python3 framework/stats.py out/lab1/stats.txt",
        "python3 framework/stats.py out/lab1/stats.txt 0",
        "python3 framework/stats.py out/lab1/stats.txt 2",
    ])
    s.text("记下：simInsts、system.cpu.numCycles、system.cpu.ipc、hostSeconds。",
           size=15, bold=True)
    s.why("两处 ROI 标记都是「转储并重置」（编码 0x8400007b，custom-3 空间里的 gem5 伪指令）。退出时再转储一次，于是 stats.txt 切成三段：第 0 段是 libc 启动，第 1 段是 ROI，第 2 段是收尾。stats.py 默认取第 1 段。")

    s = d.slide("任务 1 · 写进报告", "第 0 段启动，第 1 段 ROI，第 2 段收尾",
                "解释收尾段为什么指令很少，IPC 却只有 0.4 左右。")
    s.why("周期数 = 指令数 ÷ IPC。启动段指令占比不大，IPC 却低得多，周期占比就被放大。不划 ROI，测到的是 glibc 的启动。")
    s.table([
        ["段", "从哪到哪", "测到的是什么"],
        ["0", "程序开始 → ROI_BEGIN", "libc 启动，和算法无关"],
        ["1", "ROI_BEGIN → ROI_END", "内核，stats.py 默认取这段"],
        ["2", "ROI_END → 退出", "收尾，通常没有热循环"],
    ], [1.2, 4.2, 5.8], row_h=0.40, size=14, aligns=[L, L, L], hi_rows=(2,))
    s.ask([
        "第 2 段指令数不到一万，IPC 却只有 0.4 左右。那段代码在干什么？它有循环吗？",
    ])
    s.callout("第 0 段指令数是 0：你跑的是 _noroi，整份 stats.txt 只有一段。",
              kind="warn")

    s = d.slide("任务 2（a）· 用任务 1 那一次", "三段各占多少",
                "不用再跑。用刚才那一次，算启动和 ROI 各占多少指令、多少周期。")
    s.text("不用再跑。把任务 1 的三段填进这张表。", size=16, bold=True)
    s.table([
        ["段", "指令数", "占全程序", "周期数", "占全程序", "IPC"],
        ["第 0 段 启动", "", "", "", "", ""],
        ["第 1 段 ROI", "", "", "", "", ""],
        ["第 2 段 收尾", "", "", "", "", ""],
        ["合计", "", "100%", "", "100%", ""],
    ], [2.4, 1.6, 1.6, 1.8, 1.6, 1.2], row_h=0.42, size=14,
       aligns=[L, L, L, L, L, L], hi_rows=(2,))
    s.ask([
        "启动段占指令的百分之几，占周期的百分之几？用「周期数 = 指令数 ÷ IPC」解释为什么差这么多。",
        "如果拿全程序 IPC（合计指令 ÷ 合计周期）当 qnn 的性能，相对内核 IPC 低估多少倍？",
    ])

    s = d.slide("任务 2（b）· 再跑一次样本数 64", "加大负载能不能代替 ROI",
                "样本改成 64 再跑一次，看把负载加大能不能代替划 ROI。")
    s.code([
        "$GEM5_BIN --outdir=out/lab1_64 framework/cssys_se.py \\",
        "    --cmd bench/bin/riscv/qnn --options \"64 <学号后四位>\" --cpu o3",
        "python3 framework/stats.py out/lab1_64/stats.txt 0",
    ])
    s.table([
        ["样本数", "启动段指令", "启动段周期", "占全程序指令", "占全程序周期"],
        ["8", "", "", "", ""],
        ["64", "", "", "", ""],
    ], [1.6, 2.2, 2.2, 2.6, 2.6], row_h=0.44, size=14, aligns=[L] * 5)
    s.ask([
        "启动段的绝对开销变了吗？占比呢？不划 ROI 时，把负载加大能不能代替划 ROI？代价是什么？",
    ])
    s.why("启动段的绝对开销不随样本数变，占比会下降。加大负载能稀释它，但主机时间几乎线性增加。布局一旦不同，相减也不能代替划 ROI。")

    s = d.slide("任务 2（c）· 先跑这四个二进制", "两次测量相减靠不靠得住",
                "四个二进制只差编译选项。用它们检验「两次测量相减」靠不靠得住。")
    s.steps([
        "qnn_noroi 没有 ROI 标记，stats.txt 只有一段，就是整个程序。",
        "qnn_noalign 与 qnn 源码相同、优化相同，只是编译时没加对齐参数。",
        "全程序周期 = 该二进制所有统计段的周期数之和。",
    ])
    s.code([
        "for b in qnn qnn_noroi qnn_noalign qnn_noalign_noroi; do",
        "  echo -n \"$b  \"",
        "  $GEM5_BIN --outdir=out/c_$b framework/cssys_se.py \\",
        "      --cmd bench/bin/riscv/$b --options " + SEED + " --cpu o3 2>&1 | tail -1",
        "done",
    ])
    s.why("qnn_noroi 只少了两条伪指令，代码布局已经和 qnn 不同。O3 每周期只能从一个 64 字节对齐的块里取指令：循环体跨在边界上，每次迭代要取两次。这和 Cache 容量无关，相减会把这个假差异算进去。")

    s = d.slide("任务 2（c）· 填表，再量两个数", "地址 mod 64，以及取指停顿",
                "查出热函数落在 64 字节块的哪里，看慢的是不是「没加对齐参数」。")
    s.table([
        ["二进制", "有 ROI", "有对齐", "全程序周期", "dot_i8 mod 64", "取指停顿占比"],
        ["qnn", "有", "有", "", "", ""],
        ["qnn_noroi", "无", "有", "", "", ""],
        ["qnn_noalign", "有", "无", "", "", ""],
        ["qnn_noalign_noroi", "无", "无", "", "", ""],
    ], [3.2, 1.3, 1.3, 2.0, 2.2, 2.2], row_h=0.40, size=13,
       aligns=[L] * 6, hi_rows=(3,))
    s.code([
        "riscv64-linux-gnu-nm bench/bin/riscv/<名字> | grep dot_i8",
        "grep -E 'fetch.cacheLines|icacheStallCycles' out/c_<名字>/stats.txt",
    ], size=14)
    s.why("看地址 mod 64，不要看「有没有加对齐参数」这几个字。qnn_noalign 没加对齐参数，只要热函数碰巧落在对齐的位置，它就不慢。icacheStallCycles 占总周期的比例，是这条解释的直接证据。")

    s = d.slide("任务 2（c）· 写进报告", "先别写「加了对齐就快」",
                "先用 mod 64 把四行对一遍，再决定能不能写「加了对齐就快」。")
    s.why("相减只在两次测量的代码布局一致时成立。bench/Makefile 强制对齐，就是为了摁住这种和设计无关、却能到 3 倍的干扰。先自己写规则，再打开 Makefile 看那段注释。")
    s.ask([
        "对齐的那一对：相减法和你在 (a) 里直接读到的启动段，差多少？",
        "没对齐的那一对：全程序周期差几倍？指令数差多少？",
        "把四行的 mod 64 和周期数对应着看。qnn_noalign 没有对齐参数，它慢了吗？",
        "O3 每周期只能从一个 64 字节对齐的块里取指令。循环体跨在块边界上，每次迭代要取几次？icacheStallCycles 占总周期的百分之几？",
        "两条规则：什么时候可以相减？Makefile 为什么要强制加对齐？先写你自己的答案，再看注释。",
    ])

    s = d.slide("任务 3 · 30 分钟 · 先跑", "四个 CPU 模型",
                "同一份 qnn，四个模型各跑一遍，比谁快、谁的 IPC 像 o3。")
    s.code([
        "python3 framework/sweep.py --name lab1_cpu \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --vary cpu=atomic,timing,minor,o3 --jobs 4",
        "python3 framework/report.py results/lab1_cpu.csv \\",
        "    insts cycles ipc host_seconds host_inst_rate \\",
        "    l1d_miss_rate l1d_mshr_mpki",
    ])
    s.steps([
        "表在 results/lab1_cpu.csv。",
        "作图：横轴仿真速率（指令/秒），纵轴 IPC，四个点标上模型名。",
    ])
    s.why("atomic 把访存当成马上完成，拿来看程序跑没跑对。timing 会真的去访问 Cache，但一条访存没回来，后面全停着，延迟会被放大。minor 是顺序流水线，失效一次整条管线停住。o3 可以好几次失效叠在一起。所以前面三个跑得快，拿来选方案经常选错。")

    s = d.slide("任务 3 · 填表", "相对 o3 的 IPC 误差一起算",
                "把便宜模型的 IPC 和 o3 比，看它能不能拿来代替 o3。")
    s.table([
        ["模型", "周期数", "IPC", "主机耗时", "指令/秒", "相对 o3 的 IPC 误差"],
        ["atomic", "", "", "", "", ""],
        ["timing", "", "", "", "", ""],
        ["minor", "", "", "", "", ""],
        ["o3", "", "", "", "", ""],
    ], [1.6, 1.6, 1.3, 1.6, 1.8, 3.3], row_h=0.42, size=14,
       aligns=[L] * 6, hi_rows=(4,))
    s.ask([
        "atomic 和 minor 的 IPC 接近，主机耗时差 4 倍多。看 L1D 失效率：atomic 能代替 minor 吗？",
        "timing 和 atomic 都是一次一条指令，为什么 timing 的 IPC 低得多？",
        "o3 的 IPC 大约是 minor 的 6 倍。多发射、乱序、访存重叠各贡献了什么？这次只写定性判断。",
    ])

    s = d.slide("任务 4 · 30 分钟 · ★核心 · 先跑", "便宜的模型会不会让你选错",
                "L1 选 16kB 还是 128kB。用三个模型各答一次，看谁会让你选错。")
    s.text("设计问题：L1 数据 Cache 选 16kB 还是 128kB？以 o3 为这次的参考答案。",
           size=16, bold=True)
    s.code([
        "python3 framework/sweep.py --name lab1_fid \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --vary cpu=timing,minor,o3 --vary l1d-size=16kB,128kB --jobs 6",
        "python3 framework/report.py results/lab1_fid.csv \\",
        "    cycles ipc l1d_miss_rate l1d_mshr_mpki",
    ])
    s.why("容量翻一倍，命中要多 1 拍，见 cssys_se.py 里的 scaled_latency()。timing 不会把访存叠起来，这 1 拍会被它放大成整段都在等，它就会觉得大 Cache 更差。minor 失效一次就停住，16kB 和 128kB 在它看来差不多。o3 能把多次失效叠在一起，大 Cache 的好处才出得来。")

    s = d.slide("任务 4 · 填表", "每个模型选谁，选对了没有",
                "每个模型圈出一个容量，再对照 o3，写下选对了没有。")
    s.table([
        ["模型", "16kB 周期", "128kB 周期", "该模型选谁", "选对了吗"],
        ["timing", "", "", "", ""],
        ["minor", "", "", "", ""],
        ["o3", "", "", "", ""],
    ], [1.8, 2.2, 2.4, 2.4, 2.4], row_h=0.48, size=15,
       aligns=[L] * 5, hi_rows=(3,))
    s.ask([
        "三个模型给出了几种结论？每种结论背后的机制是什么？",
        "timing 认为大 Cache 更差。错在哪？看 scaled_latency()：容量翻倍，命中延迟 +1。",
        "minor 认为两者几乎一样。错在哪？",
        "后面六次实验你用哪个模型？只关心指令数、不关心时序的那次，会不会换一个更快的？",
    ])

    s = d.slide("任务 5 · 20 分钟 · 先跑", "样本数要多大才够",
                "样本从 2 加到 32，找 IPC 已经稳住、机器又跑得动的规模。")
    s.code([
        "for n in 2 4 8 16 32; do",
        "  $GEM5_BIN --outdir=out/scale_$n framework/cssys_se.py \\",
        "      --cmd bench/bin/riscv/qnn --options \"$n <学号后四位>\" --cpu o3 &",
        "done",
        "wait",
        "for n in 2 4 8 16 32; do",
        "  echo -n \"$n: \"",
        "  python3 framework/stats.py out/scale_$n/stats.txt | python3 -c \\",
        '  "import json,sys; d=json.load(sys.stdin); print(d[\'insts\'], round(d[\'ipc\'],4), d[\'host_seconds\'])"',
    ], size=12)
    s.why("样本太小的时候，启动和冷 Cache 还占着，IPC 会变。大到工作集开始重复，IPC 就停在平台上。主机耗时大致跟指令数走，也就是跟样本数走。工作集会随 N 涨过 Cache 的程序，缩小规模测到的是另一个程序。")

    s = d.slide("任务 5 · 画两张图", "IPC 对样本数，主机耗时对样本数",
                "用这两张图决定：后面一次扫 20 个配置，样本数选多大。")
    s.why("20 个配置、8 个核：扫描总耗时 ≈ 单点耗时 × ⌈20/8⌉。IPC 已经上了平台之后再加大样本，只增加墙钟时间，不改变结论。")
    s.ask([
        "IPC 从第几个样本数开始基本不变？变化幅度是多少？",
        "主机耗时和样本数是什么关系？",
        "一次扫描 20 个配置、机器 8 个核，你选多大的样本数？把扫描总耗时算出来。",
        "什么样的程序不能靠减小规模？想工作集和 Cache 容量的关系。",
    ])

    s = d.slide("任务 6 · 选做", "换 pchase，再做一次任务 4",
                "换成没有空间局部性的负载，看任务 4 的排序还成不成立。")
    s.code([
        "python3 framework/sweep.py --name lab1_fid_pchase \\",
        "    --bench pchase --bench-args \"256 200000 <学号后四位>\" \\",
        "    --vary cpu=timing,minor,o3 --vary l1d-size=16kB,128kB --jobs 6",
    ])
    s.why("pchase 下一步去哪，要等这一次 load 回来才知道。你在 qnn 上看到的「谁选对了 128kB」，换这个程序可能对不上。模型选择得写明是针对哪类程序。")
    s.ask([
        "换了负载以后，各模型的排序结论变了吗？如果变了，你的模型选择要加什么前提？",
    ])

    s = d.slide("思考题 · 写进报告", "四问，都要指向你自己的数",
                "用你自己的数说：误差多大还能用来选方案，仿真贵在哪里。")
    s.why("我们要的是排序还在：A 比 B 快，模型也这么说。IPC 和真机差一截，只要没把方案选反，这门课还能用。hostInstRate 大约 3×10⁵。真机上 1 秒的程序（2GHz、IPC=1）大约 2×10⁹ 条指令，o3 要仿好几个小时，所以才划 ROI、才把样本缩小。")
    s.steps([
        "「模拟器误差 20% 所以没用。」用你的数据反驳或支持，分开写绝对值和排序。",
        "hostInstRate 大约 3×10⁵。一个真机上跑 1 秒的程序（2GHz、IPC=1），o3 要仿多久？",
        "「限制样本数」和 --maxinsts N 有什么区别？哪一种更容易得出错误结论？",
        "ROI 不含权重初始化。一个需要预热才起效的大 Cache，这样划会不会对它不公平？你怎么改？",
    ])

    s = d.slide("交什么", "表、图、声明、CSV",
                "交表、图，外加一段不超过 300 字的模型选择声明。")
    s.steps([
        "任务 1～5 的全部表格和图。图要有坐标轴标签和单位。",
        "每一问的回答都指向你自己跑出来的数。",
        "不超过 300 字的模型选择声明：用哪个模型、为什么、什么情况下它会误导你。",
        "results/ 下你生成的 CSV。",
    ])
    s.why("声明里写：后面用哪个模型，你凭任务 4 的哪一列这么定，以及换到 pchase 这类程序时它会在哪选错。")
    s.callout("分析质量占 40%，跑通占 30%。一张没有解释的满表，低于一张把机制说清楚的三点图。",
              kind="info")

    return d.save(out_path(1))


if __name__ == "__main__":
    build()
