# -*- coding: utf-8 -*-
"""实验三操作步骤。不覆盖 labs/lab3/幻灯片.pptx。

    python _tools/ppt/steps_lab3.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验三　操作步骤"
SEED = '"8 <学号后四位>"'


def build():
    d = Deck(3, FOOT)
    d.cover(
        "修改 gem5：\n替换策略与预取器",
        "要交的决定：不把 L1D 加到 128kB，能不能拿到同样的性能。\n"
        "带上实验二的配置提案。这次要改 C++ 并重新编译。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "两处不做就判 0",
                "先复现 LRU 的病态，再把自己的策略装进 gem5，最后和预取比面积。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1", "先填预测，再扫 14 个策略 + 对照组", "20", "预测表、lab3_nopath.csv"],
        ["2 ★", "加 CssysRP：先等同 LRU，再等同 MRU", "45", "与 lru / mru 逐位相同"],
        ["3 ★★", "L1 上 8 个策略为何无效", "45", "假设 → 统计量 → L2 判决"],
        ["4", "六个预取器", "20", "lab3_pf.csv"],
        ["5 ★", "预取 vs 加容量，改写实验二提案", "20", "lab3_pf_vs_size.csv"],
        ["6", "pchase 上看预取的流量", "10", "lab3_pf_pchase.csv"],
    ], [1.1, 5.8, 1.1, 3.3], row_h=0.40, size=13, aligns=[L, L, L, L])
    s.callout("没有任务 1c 的对照组，任务 1 记 0。没有「cssys 与 lru 逐位相同」，任务 2 记 0。",
              kind="warn")

    s = d.slide("还没有 qnn 就先编译", "改替换策略之前，基线二进制要在",
                "仓库里没有可执行文件。qnn 缺了先 make；gem5.opt 缺了先全量编译。")
    s.code([
        "cd ~/cssys",
        "test -x gem5/build/RISCV/gem5.opt || (cd gem5 && scons build/RISCV/gem5.opt -j8)",
        "cd bench && make && cd ..",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn bench/bin/riscv/pchase",
    ])
    s.why("任务 1 先用现成的 qnn 和 pchase。任务 2 才改 C++ 再增量编译。第一次全量编译要几十分钟，已经有 gem5.opt 就不要在这里重编。")

    s = d.slide("本次的病态基线", "64kB / 4 路。差异不到 0.1% 就写「无差别」",
                "这次的病态就设在 64kB、4 路：工作集装不下，LRU 会反复踢掉马上要用的块。")
    s.code([
        "cd ~/cssys && export GEM5_BIN=$PWD/gem5/build/RISCV/gem5.opt",
        "# --cpu o3 --l1d-size 64kB --l1d-assoc 4",
        "# --l1d-repl  --l2-repl   lru fifo random mru lip bip rrip brrip nru drrip ship …",
        "# --l1d-pf / --l2-pf      none tagged stride bop ampm isb",
    ])
    s.steps([
        "指导书示例写 --bench-args 8。课堂上改成下面这种，带学号后四位。",
        "第一次新增 SimObject 的编译大约 5～6 分钟。编译时去读任务 4，不要干等。",
        "编译报错从最上面第一条 error: 看，后面几十条多半是它的回声。",
    ])
    s.why("病态基线是 64kB / 4 路：约 1568 个 64B 块要反复扫描，Cache 只有 1024 个位置。循环扫描时 LRU 会把马上要用的开头踢掉，命中率可以到 0。差异不到 0.1% 就写无差别，这次会有很多这样的格子。")

    s = d.slide("任务 1 · 动手前先填这张表", "填完再跑。事后补的预测不算",
                "先写你以为谁会赢。跑完再对，事后补的预测不算。")
    s.table([
        ["问题", "你的预测"],
        ["64kB/4 路，lru 的 l1d_mshr_misses 大约多少？（1568 块 × 8 遍）", ""],
        ["mru 比 lru 好还是差？大约差多少？", ""],
        ["random 呢？", ""],
        ["lip / bip / rrip / brrip / ship 这一组会怎样？", ""],
        ["相联度从 2 提到 16，lru 的失效数怎么变？", ""],
    ], [8.6, 2.6], row_h=0.48, size=13, aligns=[L, L])
    s.why("先写预测再跑。1568×8 是「每块每次扫描都失效」的上界。甲类策略按「多久没用」踢人（LRU 及其变体），乙类按插入位置赌「新块是不是马上再用」。这次要看的是：在这种扫描上，哪一类根本没生效。")

    s = d.slide("任务 1 · 三条命令都要跑", "1c 是对照组，不能省",
                "三条都要跑：14 个策略、相联度，以及把病态消掉的 128kB 对照。")
    s.code([
        "python3 framework/sweep.py --name lab3_repl --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l1d-size 64kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=lru,fifo,secondchance,treeplru,lfu,random,mru,\\",
        "      lip,bip,rrip,brrip,nru,drrip,ship --jobs 8",
        "python3 framework/sweep.py --name lab3_assoc --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3 --l1d-size 64kB\" \\",
        "  --vary l1d-assoc=2,4,8,16 --vary l1d-repl=lru,mru --jobs 8",
        "python3 framework/sweep.py --name lab3_nopath --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l1d-size 128kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=lru,random,mru,bip --jobs 4",
    ], size=12)

    s = d.slide("任务 1 · 写进报告", "14 个策略分成有效 / 无效两堆",
                "把 14 个策略分成有效和无效，并对照病态消失之后排名变不变。")
    s.steps([
        "report 的列：cycles ipc l1d_misses l1d_mshr_misses l1d_mshr_mpki。相联度和对照组只看 cycles 和 l1d_mshr_misses。",
    ])
    s.ask([
        "哪几个有效，哪几个完全无效？和指导书 §1.4 的甲/乙两类对照，你看出什么？",
        "用 §1.2 的公式算 OPT（1568 块里能常驻 1024 块）。每个有效策略拿到了 OPT 可能收益的百分之几？",
        "相联度实验符合你的预测吗？不符合，是预测错了还是模型错了？",
        "对照组：病态消失之后，MRU 还比 LRU 好吗？只写「MRU 比 LRU 好」而没有这一段，任务 1 记 0。",
    ])
    s.why("128kB 装得下那 1568 块，循环扫描的病就没了。这时候 MRU 常常反而更差。报告里只写「MRU 比 LRU 好」，把特例说成了通例。")

    s = d.slide("任务 2a · 15 分钟", "复制 LRU，先做到逐位相同",
                "先复制一份 LRU，改名注册。验收标准是和原来的 LRU 逐位相同。")
    s.code([
        "cd gem5/src/mem/cache/replacement_policies/",
        "cp lru_rp.hh cssys_rp.hh && cp lru_rp.cc cssys_rp.cc",
    ])
    s.steps([
        "两个文件里：LRU → Cssys，LRURP → CssysRP，头文件卫哨改成 CSSYS，params/LRURP.hh 改成 params/CssysRP.hh。",
        "ReplacementPolicies.py 末尾加上一页里的类。",
        "SConscript：sim_objects 列表里加 'CssysRP'，再加一行 Source('cssys_rp.cc')。",
        "framework/cssys_se.py 的 REPLACEMENT_POLICIES 加 \"cssys\": CssysRP, 。",
        "然后 cd gem5 && scons build/RISCV/gem5.opt -j8 。",
    ])
    s.why("先做到和 LRU 逐位相同，再改行为。不相同就说明改名或注册改错了，后面所有「我的策略更好」都没有意义。新增 SimObject 会重编大约 150 个文件，编译的几分钟去读任务 4。")

    s = d.slide("任务 2a · 要加进 Python 的这一段", "类名、头文件路径不要改",
                "Python 里注册这个类，编译之后用命令确认它和 LRU 是同一个结果。")
    s.code([
        "class CssysRP(BaseReplacementPolicy):",
        "    type = \"CssysRP\"",
        "    cxx_class = \"gem5::replacement_policy::Cssys\"",
        "    cxx_header = \"mem/cache/replacement_policies/cssys_rp.hh\"",
    ], size=15)
    s.h3("验收：cycles 必须和 lru 逐位相同")
    s.code([
        "python3 framework/sweep.py --name lab3_mine --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l1d-size 64kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=lru,cssys --jobs 2",
        "python3 framework/report.py results/lab3_mine.csv cycles l1d_mshr_misses",
    ], size=13)
    s.callout("不相同就先改到相同，再做 2b。", kind="warn")

    s = d.slide("任务 2b · 15 分钟", "getVictim() 里把 < 改成 >",
                "只改比较方向，让它去踢最近用过的。跑出来必须和自带的 MRU 一样。")
    s.steps([
        "只改 cssys_rp.cc 这一个字符，重新编译。增量编译大约 3 分钟，时间几乎都在链接。",
        "验收对象换成 gem5 自带的 mru，必须逐位相同。",
    ])
    s.code([
        "python3 framework/sweep.py --name lab3_mine2 --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l1d-size 64kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=mru,cssys --jobs 2",
    ])
    s.why("把 < 改成 > 只是把「踢最久没用的」换成「踢最近用过的」。Cache 刚上电时路是空的，空路时间戳是 0：找最小值会先选空路，找最大值会跳过它们，先去踢一条有数据的路。所以 MRU 比 LRU 多了几行处理空路。对不上就去读 mru_rp.cc 的 getVictim()。")

    s = d.slide("任务 2c · 15 分钟", "把比较方向做成参数，免得每次都重编",
                "把「踢 LRU 还是踢 MRU」做成参数。编一次，后面用命令行切换。")
    s.steps([
        "ReplacementPolicies.py 的 CssysRP 里加 evict_mru = Param.Bool(False, \"...\")。",
        "hh 里加 const bool evictMru; ，构造函数里 evictMru(p.evict_mru)。",
        "getVictim() 里：better = evictMru ? (c_tick > v_tick) : (c_tick < v_tick);",
        "cssys_se.py 再加 \"cssys_mru\": lambda: CssysRP(evict_mru=True),",
        "改了 Python 参数声明，这次编译会久一点。",
    ])
    s.code([
        "python3 framework/sweep.py --name lab3_mine3 --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l1d-size 64kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=lru,cssys,mru,cssys_mru --jobs 4",
    ])
    s.text("四行必须两两相等：lru=cssys，mru=cssys_mru。报告里写一句：这个参数的代价是什么？",
           size=15, bold=True)

    s = d.slide("任务 3 · 先排除「策略没装上」", "然后 10 分钟不要碰键盘",
                "先确认策略真的装上了。然后读插入和命中的代码，写出为什么 L1 上没效果。")
    s.code([
        "grep -A3 'replacement_policy' \\",
        "    out/sweeps/lab3_repl/p007_l1d-repl-lip/config.ini",
    ])
    s.steps([
        "你应看到 type=BIPRP、btp=0。策略已经生效，所以不是没装上。",
        "读 bip_rp.cc 的 reset()：btp=0 时把 lastTouchTick 设成 1，也就是插进来就是最老。",
        "读 lru_rp.cc 的 touch()：一次命中就把 lastTouchTick 覆写成当前时刻。",
        "dot_i8 逐字节扫 w1[j]。一个 64B 的块，第一次失效装入后，还有 63 个字节命中同一块。",
        "把假设写进报告，并写出它预言了哪个可以测量的量。",
    ])
    s.why("LIP 插入时把块标成最老，赌它不会被再用。但 dot_i8 逐字节扫描，一个 64B 的块装进来之后还有 63 次命中。LRU 的 touch() 一次命中就把时间戳覆写成现在。插入位置还没来得及起作用，就被块内复用擦掉了。")

    s = d.slide("任务 3b · 20 分钟", "给 CssysRP 加统计量，再编译",
                "给自己的策略加两个数：每装进一次被命中几次，第一次命中要多久。")
    s.steps([
        "CssysReplData 增加 insertTick 和 refCount，构造时清零。",
        "加 CssysStats，必须写成 mutable。计 insertions、touches、首次命中延迟。",
        "Formula：refsPerInsertion = touches / insertions，以及 avgFirstTouchDelay。",
        "touch() 里 if (refCount == 0) 记首次命中延迟；reset() 里记 insertTick 并 insertions++。",
        "编译约 3 分钟。stats.txt 有三段，看第二段。",
    ])
    s.code([
        "grep 'replacement_policy' \\",
        "    out/sweeps/lab3_mine4/p000_l1d-repl-cssys/stats.txt",
    ], size=14)
    s.text("看第二段。avgFirstTouchDelay ÷ 500 = 周期。refsPerInsertion 远大于 1，说明块被踢之前已经反复用过，插入位置被块内复用擦掉了。",
           size=14)

    s = d.slide("任务 3c · 15 分钟 · 判决", "同一批策略挂到装不下的 L2 上",
                "同一批策略改挂到同样装不下的 L2 上，看排名会不会反过来。")
    s.code([
        "python3 framework/sweep.py --name lab3_l2repl --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --l2-size 64kB --l2-assoc 4\" \\",
        "  --vary l2-repl=lru,fifo,treeplru,lfu,random,mru,lip,bip,\\",
        "      rrip,brrip,nru,drrip,ship --jobs 8",
        "python3 framework/report.py results/lab3_l2repl.csv \\",
        "    cycles ipc l2_accesses l2_mshr_misses l2_miss_rate",
    ], size=13)
    s.steps([
        "再挂到 L2：--l2-repl cssys。记下 l2cache 的 refsPerInsertion。",
    ])

    s = d.slide("任务 3 · 写进报告", "L1 的冠军和 L2 的冠军不一定是同一个",
                "把 L1 和 L2 两张表并排，用 refsPerInsertion 解释排名为什么反了。")
    s.why("L1 把块内那 63 次命中都吸收了，L2 每收到一个块往往只被引用一次左右，插入时设下的优先级才活得到被替换。所以同一套策略、同样的 64kB/4 路，L1 和 L2 的排名会反过来。LFU 的 touch() 是累加不是覆写，所以它在 L1 上仍然有效。")
    s.ask([
        "哪个策略在 L1 最好，哪个在 L2 最好？同一个程序、同样 64kB/4 路，排名为什么反过来？",
        "用你测到的 refsPerInsertion（L1 和 L2）解释这个反转。",
        "mru 在 L1 排前三，在 L2 几乎没用。它的 touch() 把刚命中的块变成了什么？L2 上一个块往往只命中一次，接下来会发生什么？",
        "加分：lfu 在 L1 最好，它的 reset() 也是插进来就最低优先级。去比 touch()：一个覆写，一个累加。",
        "加分：读 brrip_rp.cc 的 reset()。btp=100 和 btp=3 各把块插在哪？",
    ])

    s = d.slide("任务 4 · 20 分钟", "回到 32kB / 2 路，只加预取器",
                "容量回到默认，只换预取器。看周期变多少，真实流量变多少。")
    s.code([
        "python3 framework/sweep.py --name lab3_pf --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary l1d-pf=none,tagged,stride,bop,ampm,isb --jobs 6",
        "python3 framework/report.py results/lab3_pf.csv cycles ipc \\",
        "  l1d_misses l1d_mshr_mpki l1d_pf_issued l1d_pf_useful \\",
        "  l1d_pf_accuracy l1d_pf_coverage",
    ])
    s.ask([
        "五个预取器的 cycles 差多少，accuracy 差多少？准确率是收益指标还是代价指标？",
        "l1d_misses 从约 20 万掉到几千，l1d_mshr_mpki 几乎没变。用指导书 §1.8 解释。",
        "isb 发了约 120 次预取、一次都没用上。为什么这个负载上没戏？",
        "加预取器之后 l1d_mlp 会变成 0.27。去看 stats.py 里 MLP 的定义，这个口径在什么前提下才成立。",
    ])

    s = d.slide("任务 5 · 20 分钟 · ★交付物", "32kB+stride 对 128kB+不预取",
                "把「小 Cache 加预取」和「直接加大 Cache」放在一起，重写实验二的提案。")
    s.code([
        "python3 framework/sweep.py --name lab3_pf_vs_size --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary l1d-size=32kB,64kB,128kB --vary l1d-pf=none,stride --jobs 6",
        "python3 framework/report.py results/lab3_pf_vs_size.csv \\",
        "    cycles ipc l1d_mshr_mpki l1d_pf_accuracy",
    ])
    s.ask([
        "32kB+stride 和 128kB+none 的 cycles 放一起。面积差多少，性能差多少？",
        "两者的 l1d_mshr_mpki 差多少？哪一种在多核共享 L2 时更糟？",
        "128kB 上再加 stride，性能还有变化吗？为什么？",
        "重写实验二的配置提案。结论变了，写是哪条新证据推翻的；没变，写为什么这些新数据不够推翻它。只重复「还是 128kB」记 0。",
    ])

    s = d.slide("任务 6 · 10 分钟", "换 pchase，看预取的流量代价",
                "换一个没有顺序扫描的负载，看预取是不是只增加流量、不加快程序。")
    s.code([
        "python3 framework/sweep.py --name lab3_pf_pchase --bench pchase \\",
        "  --bench-args \"256 200000 <学号后四位>\" --base \"--cpu o3\" \\",
        "  --vary l1d-pf=none,tagged,stride,ampm --jobs 4",
        "python3 framework/report.py results/lab3_pf_pchase.csv \\",
        "  cycles ipc l1d_mshr_mpki l1d_pf_issued l1d_pf_useful \\",
        "  l1d_pf_accuracy dram_bytes",
    ], size=13)
    s.ask([
        "性能变了吗？l1d_mshr_mpki 变了多少倍？",
        "性能不变、流量涨到约 3 倍，在手机、数据中心、多核共享带宽里各不可接受在哪？",
        "你会给预取器加一个什么样的关闭条件？用任务 4 或任务 6 里的哪个统计量做判据？",
    ])

    s = d.slide("思考题 · 写进报告", "第 6 题的预测，实验四要验收",
                "把「LRU 什么时候好」和「换成顺序核排名变不变」写清楚。第 6 题实验四要收。")
    s.why("LRU 命中率为 0，缺的前提是「工作集小于 Cache，或者访问有重用」。随机替换硬件便宜，最坏情况也没有 LRU 这种扫描病态。把 CPU 换成 timing 之后，失效数的排名和周期数的排名可以不是同一件事：顺序核把访存代价放大，策略之间的周期差可能掉进噪声。")
    s.steps([
        "LRU 命中率精确为 0，缺了什么前提？写一个它最好的访问模式、一个最差的。",
        "random 打败了 LRU、FIFO、TreePLRU 和 8 个论文策略。从硬件代价、可预测性、最坏情况各说一句。",
        "把「插入位置型策略适合 LLC、不适合 L1」改写成一个事先能判的量。",
        "真实芯片里「可配置」的代价是什么？举两个做成可配置的 Cache 参数。",
        "实验二的 AMAT 为什么不够？本次有没有「失效率不变但性能大变」或反过来的情况？",
        "预测：CPU 从 o3 换成 timing，任务 1 的排名会变吗？先写下来。",
    ], size=14.5)

    s = d.slide("交什么 · 做不到就扣光该题", "源码、三次验收、全部 CSV",
                "必须交对照组、和 LRU 逐位相同的验收，以及任务 3 那条从假设到判决的链。")
    s.table([
        ["内容", "分"],
        ["任务 1 预测表（动手前）+ 实测 + 差异", "15"],
        ["cssys_rp 源码 + 三处注册的 diff + 两次验收", "20"],
        ["任务 3：假设 → 统计量 → 判决", "30"],
        ["任务 4 / 5 / 6 的表和分析", "25"],
        ["思考题", "10"],
    ], [8.4, 1.4], row_h=0.38, size=14, aligns=[L, L])
    s.callout("禁止：把 <0.1% 当结论；不报 1c 就说 MRU 更好；用 l1d_miss_rate 论证流量。",
              kind="warn")

    return d.save(out_path(3))


if __name__ == "__main__":
    build()
