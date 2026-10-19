# -*- coding: utf-8 -*-
"""实验二操作步骤。不覆盖 labs/lab2/幻灯片.pptx。

    python _tools/ppt/steps_lab2.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验二　操作步骤"
SEED = '"8 <学号后四位>"'


def build():
    d = Deck(2, FOOT)
    d.cover(
        "存储层次设计空间探索",
        "要交的决定：面积花在更大的 L1D、更高的相联度、更大的块，还是 L2。\n"
        "每一页只干一步。小于 0.1% 写成「没有差异」。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "最后交一份配置提案",
                "一次改一个参数。最后交你的配置，每个参数都写为什么不选旁边那个。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1", "扫 L1D 容量，再关一次延迟模型", "40", "lab2_size.csv、两条曲线"],
        ["2 ★", "相联度 × LRU / Random", "50", "assoc.csv 和 repl.csv"],
        ["3 ★", "块大小；16B 崩了用实验验证", "40", "lab2_line.csv"],
        ["4", "只改 MSHR 个数", "25", "lab2_mshr.csv"],
        ["5", "只改 L2 容量", "25", "lab2_l2.csv"],
        ["6 ★", "四个维度各选一个值，必须实测", "40", "不超过 400 字的提案"],
    ], [1.1, 5.6, 1.2, 3.4], row_h=0.40, size=14, aligns=[L, L, L, L])
    s.callout("论证流量看 l1d_mshr_mpki，不要拿 l1d_miss_rate 下结论。", kind="warn")

    s = d.slide("还没有 qnn 就先编译", "实验一编过就可以跳过",
                "仓库里没有可执行文件。缺了就按这几行编，有了就跳过。")
    s.code([
        "cd ~/cssys",
        "test -x gem5/build/RISCV/gem5.opt || (cd gem5 && scons build/RISCV/gem5.opt -j8)",
        "cd bench && make && cd ..",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn bench/bin/riscv/pchase",
    ])
    s.why("make 一次编出 qnn、gemm、pchase、branchy、stream。gem5 第一次是全量编译，要几十分钟；已经有 gem5.opt 就不要重编。本次还要用 pchase 和 stream。")

    s = d.slide("命令怎么写", "基线就是这一行，相对基线都相对它",
                "后面说「相对基线」，都是相对这一行默认配置，不要自己换基准。")
    s.code([
        "cd ~/cssys && export GEM5_BIN=$PWD/gem5/build/RISCV/gem5.opt",
        "# 基线：--cpu o3 --l1d-size 32kB --l1d-assoc 2 --l1d-mshrs 4",
        "#       --cacheline 64 --l2-size 256kB",
    ])
    s.table([
        ["参数", "这次会动它"],
        ["--l1d-size", "容量，必须让组数是 2 的幂"],
        ["--l1d-assoc / --l1d-repl", "相联度；lru random fifo rrip …"],
        ["--l1d-mshrs", "MSHR 个数"],
        ["--cacheline", "块大小，L1I / L1D / L2 一起变"],
        ["--l2-size", "L2 容量"],
        ["--auto-latency on|off", "命中延迟是否随容量涨"],
    ], [3.4, 7.8], row_h=0.38, size=14, aligns=[L, L])

    s = d.slide("任务 1 · 40 分钟 · 先跑", "容量：找到那个拐点",
                "只改 L1D 容量，从 8kB 扫到 256kB，看周期在哪一档最少。")
    s.code([
        "python3 framework/sweep.py --name lab2_size \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" \\",
        "    --vary l1d-size=8kB,16kB,32kB,64kB,128kB,256kB --jobs 6",
        "python3 framework/report.py results/lab2_size.csv \\",
        "    cycles ipc l1d_miss_rate l1d_mpki l1d_mshr_mpki l1d_mlp",
    ])
    s.steps(["图：横轴容量用对数刻度，纵轴画周期数。"])
    s.why("默认开着 auto-latency：以 32kB / 3 周期为基准，容量每翻一番，命中延迟 +1。8kB 到 64kB 时装不下约 98KB 的 w1，失效几乎不变，多付的只有延迟，所以 Cache 变大反而变慢。128kB 才装得下，曲线在这里拐。")

    s = d.slide("任务 1 · 填表", "重点看 mshr_mpki，不是 miss_rate",
                "填周期和 mshr_mpki。变大反而变慢的那一段，先看失效有没有变。")
    s.table([
        ["容量", "周期数", "IPC", "miss_rate", "mpki", "mshr_mpki"],
        ["8kB", "", "", "", "", ""],
        ["16kB", "", "", "", "", ""],
        ["32kB 基线", "", "", "", "", ""],
        ["64kB", "", "", "", "", ""],
        ["128kB", "", "", "", "", ""],
        ["256kB", "", "", "", "", ""],
    ], [2.0, 1.8, 1.4, 2.0, 1.6, 2.4], row_h=0.34, size=13,
       aligns=[L] * 6, hi_rows=(4, 5))
    s.ask([
        "周期最少的是哪一档？比 32kB 快多少？",
        "8kB→64kB 周期往上走。这一段 mshr_mpki 变了吗？收益是什么，代价是什么？",
        "128kB 处发生了什么突变？用工作集大小解释。",
        "256kB 又变慢了。为什么？",
    ])

    s = d.slide("任务 1（b）· 关掉延迟模型再跑", "两条曲线画在同一张图上",
                "同一组容量再跑一遍，只是关掉「越大越慢」的延迟。看你会不会选错。")
    s.code([
        "python3 framework/sweep.py --name lab2_size_nolat \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --auto-latency off\" \\",
        "    --vary l1d-size=8kB,16kB,32kB,64kB,128kB,256kB --jobs 6",
    ])
    s.ask([
        "关掉之后曲线是什么形状？只看这条曲线，你会选多大？",
        "开、关两条里，哪一条更接近真实芯片？为什么？",
        "模拟器没建模的东西，会以什么方式进到你的结论里？",
    ])
    s.why("关掉 auto-latency 之后，容量变大没有延迟惩罚，曲线往往会一路往上。真实芯片里大 Cache 更慢。这条没建模的代价，会直接变成你选出来的「最优容量」。")

    s = d.slide("任务 2 · 50 分钟 · ★★ · 先跑", "相联度：先别套课本",
                "容量和相联度一起扫。重点看 64kB：路数变多，失效是不是变少。")
    s.code([
        "python3 framework/sweep.py --name lab2_assoc \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" \\",
        "    --vary l1d-size=32kB,64kB,128kB --vary l1d-assoc=1,2,4,8 --jobs 12",
        "python3 framework/report.py results/lab2_assoc.csv \\",
        "    cycles ipc l1d_miss_rate l1d_mshr_mpki",
    ])
    s.why("课本说相联度越高，冲突失效越少。3C 模型这句话的前提是：替换策略不会制造新的失效。qnn 把约 98KB 的 w1 从头扫到尾再扫一遍。64kB 的 LRU 扫回开头时，留着的是刚用过的尾部，马上要用的开头已经被踢掉了。")

    s = d.slide("任务 2 · 填 mshr_mpki", "重点看 64kB 那一行",
                "把 64kB 那一行和课本对照：相联度高，冲突失效应该更少。")
    s.table([
        ["容量", "1 路", "2 路", "4 路", "8 路"],
        ["32kB", "", "", "", ""],
        ["64kB", "", "", "", ""],
        ["128kB", "", "", "", ""],
    ], [2.2, 2.2, 2.2, 2.2, 2.2], row_h=0.48, size=16,
       aligns=[L] * 5, hi_rows=(2,))
    s.ask([
        "64kB 时，1 路的失效比 2/4/8 路少还是多？符合「相联度越高冲突越少」吗？",
        "3C 说提高相联度只会减少冲突失效。你的数据和它矛盾吗？这句话隐含了什么前提？",
    ])

    s = d.slide("任务 2（b）· 换成随机替换", "1 路时 LRU 和 Random 必须相同",
                "64kB 上把 LRU 换成随机。先看 1 路两列是不是完全一样。")
    s.code([
        "python3 framework/sweep.py --name lab2_repl \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --l1d-size 64kB\" \\",
        "    --vary l1d-assoc=1,2,4,8 --vary l1d-repl=lru,random --jobs 8",
    ])
    s.table([
        ["相联度", "LRU mshr_mpki", "LRU 周期", "Random mshr_mpki", "Random 周期"],
        ["1", "", "", "", ""],
        ["2", "", "", "", ""],
        ["4", "", "", "", ""],
        ["8", "", "", "", ""],
    ], [1.6, 2.6, 2.0, 3.0, 2.2], row_h=0.40, size=14,
       aligns=[L] * 5, hi_rows=(1,))
    s.callout("1 路两列不一样：配置错了，先排查再往下做。", kind="warn")

    s = d.slide("任务 2（b）· 写进报告", "解释 LRU 为什么会输",
                "说明 qnn 这种从头扫到尾的访问，为什么 LRU 会比随机更差。")
    s.why("1 路没有选择，LRU 和 Random 必须相同，这是自检。Random 不记得「最近用过谁」，循环扫描时不会专踢马上要用的那一段，所以相联度提高时失效可以单调下降。LRU 在这种访问上会输。真实 L1 很少用课本上的完美 LRU。")
    s.ask([
        "Random 下，相联度提高时失效单调下降吗？LRU 呢？",
        "dot_i8(w1[j], xbuf, 784) 一次扫过多长？每个样本把约 98KB 的 w1 从头扫到尾，再扫一遍。64KB 的 Cache 用 LRU，扫回开头时留着的是哪一段？马上要用的是哪一段？",
        "什么样的访问模式不该用 LRU？查一张真实处理器的 L1 替换策略，为什么不是课本上的 LRU？",
    ])

    s = d.slide("任务 3（a）· 先填预测，再跑", "块大小：预测列不许看结果",
                "先按「总字节数不变」把失效数算出来，再跑 16B 到 256B。")
    s.table([
        ["块大小", "预测每样本失效", "预测 mshr_mpki", "实测 mshr_mpki", "误差"],
        ["16B", "", "", "", ""],
        ["32B", "", "", "", ""],
        ["64B", "", "", "", ""],
        ["128B", "", "", "", ""],
        ["256B", "", "", "", ""],
    ], [1.6, 2.6, 2.6, 2.6, 1.6], row_h=0.40, size=14, aligns=[L] * 5)
    s.text("预测：每样本失效 ≈ 100.7KB ÷ 块大小；mshr_mpki ≈ 该数 × 8 ÷ 5.8M × 1000。",
           size=14)
    s.code([
        "python3 framework/sweep.py --name lab2_line \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" --vary cacheline=16,32,64,128,256 --jobs 5",
    ])

    s = d.slide("任务 3（a）（b）· 写进报告", "失效降了，周期为什么不跟着降",
                "对一下预测和实测，再解释失效降了十几倍、周期为什么没跟着降。")
    s.ask([
        "预测准吗？误差多少？块大小翻倍时 mshr_mpki 是什么规律？总字节数变了吗？",
        "失效数从 16B 到 256B 降了约 16 倍，周期降了几倍？为什么不成比例？",
    ])
    s.h3("接着填性能")
    s.table([
        ["块大小", "周期数", "IPC", "mshr_mpki", "l1d_mlp"],
        ["16B", "", "", "", ""],
        ["32B", "", "", "", ""],
        ["64B", "", "", "", ""],
        ["128B", "", "", "", ""],
        ["256B", "", "", "", ""],
    ], [1.8, 2.2, 1.8, 2.4, 2.0], row_h=0.36, size=14, aligns=[L] * 5,
       hi_rows=(1,))

    s = d.slide("任务 3 · 16B 特别慢，先验证假设", "假设：MSHR 不够。先跑再下结论",
                "16B 特别慢。先假设是 MSHR 不够，把 MSHR 加大再跑来验证。")
    s.why("失效次数随块变大而下降，是因为搬运的总字节数差不多、每次搬得更多。16B 特别慢，先别当成「MSHR 不够」写进报告。把 MSHR 加到 16、64，若周期几乎不动、blockedCycles::no_mshrs 也接近 0，假设就被否定，再去查取指。")
    s.code([
        "python3 framework/sweep.py --name lab2_line_mshr \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" \\",
        "    --vary cacheline=16,32,64 --vary l1d-mshrs=4,16,64 --jobs 9",
        "grep 'dcache.blockedCycles::no_mshrs' \\",
        "    out/sweeps/lab2_line_mshr/*/stats.txt",
    ])
    s.ask(["这个假设成立吗？不成立的话，错在哪？"])

    s = d.slide("任务 3 · 假设被否定之后", "去查取指，不要把取指缓冲当成 bug",
                "MSHR 解释不了，就去查取指停了多少拍。块变小会拖垮取指。")
    s.code([
        "grep -E 'fetch.cacheLines|icacheStallCycles|cpu.numCycles ' \\",
        "    out/sweeps/lab2_line/p000_cacheline-16/stats.txt",
    ], size=14)
    s.why("取指缓冲是 min(64, cacheline)：一次只能从一个已经取回来的块里取指令。块变成 16B，取指就要更频繁地重新访问 I-Cache。这是数据 Cache 的参数把取指拖垮了，不是 MSHR 不够。blockedCycles::no_mshrs 若接近 0，MSHR 假设就不成立。")
    s.ask([
        "16B 的 icacheStallCycles 占总周期的百分之几？和 64B 比。",
        "取指缓冲是 min(64, cacheline)。块变小，取指就要更频繁地重新访问 I-Cache。用这个解释 16B 的崩塌。",
    ])

    s = d.slide("任务 3 · 换一个没有空间局部性的负载", "qnn 偏爱大块，不代表块可以无限大",
                "qnn 是顺序扫描。换 pchase，看大块还是不是更快。")
    s.code([
        "python3 framework/sweep.py --name lab2_line_pchase \\",
        "    --bench pchase --bench-args \"256 200000 <学号后四位>\" \\",
        "    --base \"--cpu o3\" \\",
        "    --vary l1d-size=32kB,128kB --vary cacheline=64,256 --jobs 4",
    ])
    s.ask([
        "pchase 上 256B 比 64B 更快还是更慢？32kB 和 128kB 两个容量答案一样吗？",
        "用「搬进来的字节里有多少被用到」解释 qnn 和 pchase 的差别。",
        "pchase 的 l1d_mlp 和 qnn 差很多。下一个地址是从哪来的，能提前算出来吗？",
        "多核里块变大还有一个代价，名称是什么？（假共享）",
    ])
    s.why("qnn 的 dot_i8 连续扫 784 个字节，搬进来的每个字节都会用到，空间局部性接近 100%，所以偏爱大块。pchase 没有空间局部性，大块是在搬用不到的字节。多核里还有假共享：两个核写同一块的不同字节，整块在核之间来回作废。")

    s = d.slide("任务 4 · 25 分钟", "MSHR：失效率到底是谁的属性",
                "程序和容量都不动，只改 MSHR 个数，看「失效率」会不会自己变。")
    s.code([
        "python3 framework/sweep.py --name lab2_mshr \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" --vary l1d-mshrs=1,2,4,8,16 --jobs 5",
        "python3 framework/report.py results/lab2_mshr.csv \\",
        "    cycles ipc l1d_miss_rate l1d_mshr_mpki l1d_mlp",
    ])
    s.table([
        ["MSHR", "周期数", "miss_rate", "mshr_mpki", "mlp"],
        ["1", "", "", "", ""],
        ["2", "", "", "", ""],
        ["4", "", "", "", ""],
        ["8", "", "", "", ""],
        ["16", "", "", "", ""],
    ], [1.6, 2.2, 2.4, 2.4, 1.6], row_h=0.34, size=13, aligns=[L] * 5,
       hi_rows=(1, 2))

    s = d.slide("任务 4 · 写进报告", "只改了队列深度",
                "对比 miss_rate 和 mshr_mpki，判断再加 MSHR 还划不划算。")
    s.why("好几次访问可以合并进同一个 MSHR。队列一深，miss_rate 就掉，程序却没变。mshr_mpki 计的是真正发出去的请求。对 qnn，MLP 到 4 左右就不再涨，再加 MSHR，周期基本不动。")
    s.ask([
        "miss_rate 在 MSHR=1 和 2 之间变了多少？mshr_mpki 变了吗？",
        "程序、数据、容量都没变，失效率变了十几倍。失效率是什么的属性？",
        "MSHR 从 4 加到 16，性能有提升吗？看 l1d_mlp 停在多少。",
        "对 qnn，再加 MSHR 划算吗？什么样的负载才需要更多 MSHR？",
    ])

    s = d.slide("任务 5 · 25 分钟", "L2：钱该花在哪一级",
                "只把 L2 从 128kB 加到 2MB，看周期和 DRAM 流量动不动。")
    s.code([
        "python3 framework/sweep.py --name lab2_l2 \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3\" \\",
        "    --vary l2-size=128kB,256kB,512kB,1MB,2MB --jobs 5",
        "python3 framework/report.py results/lab2_l2.csv \\",
        "    cycles ipc l2_miss_rate l2_accesses dram_bytes",
    ])
    s.ask([
        "L2 从 128kB 加到 2MB，性能变好还是变坏？幅度多少？",
        "dram_bytes 是多大？相对 ROI 里大约 160 万次访存，占多少？",
        "对 qnn，L2 起作用了吗？这块面积你会挪去干什么？",
        "什么样的负载会让 L2 变得重要？",
    ])

    s = d.slide("任务 6 · 40 分钟 · ★交付物", "四个维度各选一个，必须实测",
                "四个旋钮各定一个值，这个点必须自己跑，不能靠单维结果相加。")
    s.steps([
        "四个维度：l1d-size、l1d-assoc、cacheline、l2-size。不能只靠前面的单维扫描外推。",
        "提案里写：配置、相对基线的加速比、为什么不选另一个值。",
    ])
    s.code([
        "python3 framework/sweep.py --name lab2_final \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --l1d-size ??? --l1d-assoc ??? \\",
        "            --cacheline ??? --l2-size ???\" \\",
        "    --vary l1d-repl=lru,random --jobs 2",
    ])
    s.ask([
        "实测和单维外推一致吗？不一致就举出一对互相影响的参数。",
    ])
    s.why("块大小会牵动取指，相联度会牵动 LRU 那件事，容量会牵动命中延迟。四个单维扫描的最优点叠在一起，常常不是一起跑的结果。提案那个点得自己跑一遍。")

    s = d.slide("任务 6 · 用另一个负载验一次", "结论翻转了就要写进去",
                "用 pchase 再跑你的配置。结论翻了，就写进提案，不要藏。")
    s.code([
        "python3 framework/sweep.py --name lab2_final_x \\",
        "    --bench pchase --bench-args \"256 200000 <学号后四位>\" \\",
        "    --base \"<你的配置>\" \\",
        "    --vary l1d-size=32kB,<你选的容量> --jobs 2",
    ])
    s.why("换到 pchase 或 stream，工作集和局部性都变了，你在 qnn 上选出的容量、块大小可以整个翻过来。翻了就写进提案，这是提案的一部分，不是失败。")
    s.callout("评分看论证站不站得住。次优但把权衡讲清楚，高于碰巧选对但说不出理由。",
              kind="info")

    s = d.slide("思考题里还要再跑的两条", "写进报告，不是现在的主线",
                "一条看最优容量跟不跟延迟参数走，一条看论文里的替换策略是否兑现。")
    s.code([
        "python3 framework/sweep.py --name lab2_latsens \\",
        "    --bench qnn --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "    --vary l1d-size=8kB,32kB,128kB,256kB --vary l1-latency=2,3,5 --jobs 12",
        "python3 framework/sweep.py --name lab2_replfam \\",
        "    --bench qnn --bench-args " + SEED + " \\",
        "    --base \"--cpu o3 --l1d-size 64kB --l1d-assoc 4\" \\",
        "    --vary l1d-repl=lru,random,fifo,nru,rrip,brrip --jobs 6",
    ], size=12)
    s.steps([
        "思考题其余三问按指导书写：单一指标、ROI 预热、625 个点穷举要多久。",
        "RRIP 的实测和论文不符时，不许写成「所以没用」，也不许无视实测照抄论文。",
    ])

    s = d.slide("交什么", "三张图 + 400 字提案",
                "交三张图和一份不超过 400 字的配置提案，每个维度都要说为什么不选别的。")
    s.steps([
        "任务 1～6 的全部表格。",
        "至少三张图：容量（延迟模型开/关两条）、相联度×替换策略、块大小。",
        "配置提案不超过 400 字：四个取值、加速比、每个维度为什么不选别的。",
        "results/ 下全部 CSV。",
    ])
    s.callout("机制分析 45%（任务 2 和 3 占一大半），方法学 15%，提案 15%，数据 15%，规范 10%。",
              kind="info")

    return d.save(out_path(2))


if __name__ == "__main__":
    build()
