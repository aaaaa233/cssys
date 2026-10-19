# -*- coding: utf-8 -*-
"""实验四操作步骤。不覆盖 labs/lab4/幻灯片.pptx。

    python _tools/ppt/steps_lab4.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steps_ui import Deck, out_path
from pptx.enum.text import PP_ALIGN

L = PP_ALIGN.LEFT
FOOT = "实验四　操作步骤"
SEED = '"8 <学号后四位>"'


def build():
    d = Deck(4, FOOT)
    d.cover(
        "乱序执行与分支预测",
        "要交的决定：对 qnn，核里面哪一项才是瓶颈。\n"
        "带上实验三思考题第 6 题的预测。小于 0.1% 写成「没有差异」。",
        "计算机系统综合设计实验　·　4 学时　·　按指导书操作")

    s = d.slide("今天按这个顺序做", "任务 4 的对照组不做就判 0",
                "先看加宽把瓶颈搬到哪，再换数据和预测器，最后用手算去对实测。")
    s.table([
        ["顺序", "做什么", "分钟", "做完要有"],
        ["1", "宽度 1/2/4/8，先写预测再跑", "15", "lab4_width.csv"],
        ["2 ★", "先加 ROB，再加 LQ，最后加 IQ", "40", "瓶颈迁移图"],
        ["3 ★", "先在 qnn 上换预测器，再跑 branchy", "25", "三张 mode 的表"],
        ["4 ★★", "手算误预测率，再和实测对质", "35", "手推表 + 对照组"],
        ["5", "宽度 × local/tage", "20", "lab4_wxbp.csv"],
        ["6", "只改 BTB 表项", "10", "lab4_btb.csv"],
        ["7 ★", "有效的资源一次加满", "15", "交付物那张表"],
    ], [1.2, 5.6, 1.1, 3.2], row_h=0.38, size=13, aligns=[L, L, L, L])

    s = d.slide("还没有 qnn 就先编译", "实验一编过就可以跳过",
                "仓库里没有可执行文件。本次还要用 branchy，make 会一起编出来。")
    s.code([
        "cd ~/cssys",
        "test -x gem5/build/RISCV/gem5.opt || (cd gem5 && scons build/RISCV/gem5.opt -j8)",
        "cd bench && make && cd ..",
        "ls gem5/build/RISCV/gem5.opt bench/bin/riscv/qnn bench/bin/riscv/branchy",
    ])
    s.why("make 一次编出 qnn、gemm、pchase、branchy、stream。gem5 第一次是全量编译，要几十分钟；已经有 gem5.opt 就不要重编。本次不改 gem5 源码。")

    s = d.slide("不加参数时就是这套基线", "后面每张表的「基线」都是它",
                "不加参数就是这套默认值。后面说「加了 ROB」都是相对它。")
    s.table([
        ["参数", "默认", "本次怎么动"],
        ["--width", "8", "同时改取指/译码/重命名/发射/提交"],
        ["--rob / --iq", "192 / 64", "ROB、发射队列"],
        ["--lq / --sq", "32 / 32", "Load 队列 / Store 队列"],
        ["--int-regs", "256", "物理整数寄存器"],
        ["--bp", "tournament", "local bimode tournament tage ltage tage_sc_l"],
        ["--btb-entries", "4096", "BTB 表项"],
    ], [2.4, 2.2, 6.6], row_h=0.40, size=14, aligns=[L, L, L])
    s.callout("local 里面没有局部历史，就是一张按 PC 索引的 2 bit 计数器。任务 4 用的就是它。不要写「ROB 没用」。",
              kind="warn")
    s.why("ROB、IQ、LQ 谁的 FullEvents 不是 0，瓶颈就在谁。全是 0 说明没被表满堵住。")

    s = d.slide("任务 1 · 先填预测，再跑", "宽度 1 → 8",
                "只改发射宽度。先猜 IPC 能涨几倍、哪张表会满，再跑。")
    s.table([
        ["问题", "你的预测"],
        ["宽度 1→8，IPC 大约能涨几倍？", ""],
        ["宽度为 1 时，哪张表会满？", ""],
        ["宽度为 8 时，哪张表会满？", ""],
        ["l1d_mlp 会怎么变？为什么？", ""],
    ], [7.4, 3.8], row_h=0.42, size=15, aligns=[L, L])
    s.code([
        "python3 framework/sweep.py --name lab4_width --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary width=1,2,4,8 --jobs 4",
        "python3 framework/report.py results/lab4_width.csv cycles ipc \\",
        "  rob_full_events iq_full_events lq_full_events sq_full_events \\",
        "  l1d_mlp load_to_use squash_ratio",
    ], size=13)

    s = d.slide("任务 1 · 写进报告", "宽度涨了 8 倍，IPC 没有涨 8 倍",
                "对照 FullEvents，说清宽度从 1 加到 8，瓶颈从哪搬到了哪。")
    s.why("宽度为 1 时四张表的 FullEvents 都是 0：每拍只放进一条指令，表永远装不满，瓶颈就是宽度自己。加到 8 之后表开始满，真正买到的是同时在飞的 load，也就是 l1d_mlp，不是 8 倍的 IPC。")
    s.ask([
        "IPC 涨了几倍？少掉的那部分去哪了？",
        "宽度 1 时四张表的 FullEvents 全是 0，说明什么？rename 没被表满堵住，那它被什么堵着？",
        "l1d_mlp 从宽度 1 到 8 涨了多少倍？和 IPC 的涨幅放一起：加宽度真正买到的是什么？",
        "用一句话写：宽度从 1 加到 8，瓶颈从哪里搬到了哪里。",
    ])
    s.callout("--width 1 大约要 1 分钟，不是卡死。模拟器的快慢和被模拟机器的快慢是两回事。",
              kind="info")

    s = d.slide("任务 2a · 10 分钟", "先加 ROB。先写预测再跑",
                "只加 ROB。看 32 到 128 有没有用，192 再到 384 还有没有用。")
    s.code([
        "python3 framework/sweep.py --name lab4_rob --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary rob=32,64,128,192,384 --jobs 5",
        "python3 framework/report.py results/lab4_rob.csv cycles ipc \\",
        "  rob_full_events iq_full_events lq_full_events \\",
        "  l1d_mlp load_to_use",
    ])
    s.ask([
        "32→128 有没有收益？192→384 呢？比 cycles 的整数，不要看 IPC 的四位小数。",
        "192→384 那一行的 rob_full_events 是多少？为什么 384 没有收益？",
        "rob 从 64 加到 128：rob_full 下降，iq_full 和 lq_full 变大。瓶颈从 ____ 搬到 ____。",
    ])
    s.callout("别写「ROB 没用」。32→128 有用，192 已够。",
              kind="warn")

    s = d.slide("任务 2b · 10 分钟", "再加 LQ",
                "只加 Load 队列。看它和同时在飞的失效条数是不是一条线。")
    s.code([
        "python3 framework/sweep.py --name lab4_lq --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary lq=8,16,32,64,128 --jobs 5",
        "python3 framework/report.py results/lab4_lq.csv cycles ipc \\",
        "  lq_full_events sq_full_events iq_full_events rob_full_events \\",
        "  l1d_mlp load_to_use l1d_misses",
    ], size=13)
    s.ask([
        "32→64 省了多少周期，百分之几？64→128 呢？去看 lq_full_events。",
        "把 l1d_mlp 和 lq（8 / 16 / 32）画成一条线。长延迟访存冻结的是 ROB 和 LQ。",
    ])
    s.why("一次 L1 失效要等几十拍。顺序上这些拍冻结的是 ROB 和 LQ：load 不返回，就一直占着 LQ 的一项，也占着 ROB 里它后面的指令。所以 l1d_mlp 大致不会超过 LQ 的深度。LQ 已经不满之后再加大，周期就不再动。")

    s = d.slide("任务 2c · 15 分钟 · ★", "加 IQ 之前，base 里必须写 --lq 64",
                "先把 LQ 放开再加 IQ。另外去掉 --lq 64 重跑一次，作为对照。")
    s.code([
        "python3 framework/sweep.py --name lab4_iq --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3 --lq 64\" \\",
        "  --vary iq=16,32,64,128 --jobs 4",
        "python3 framework/report.py results/lab4_iq.csv cycles ipc \\",
        "  iq_full_events rob_full_events lq_full_events \\",
        "  l1d_mlp load_to_use",
    ])
    s.callout("去掉 --lq 64 再跑一次，否则 2c 不给分。",
              kind="warn")
    s.ask([
        "iq = 16 / 32 / 64 各省多少？iq = 128 时哪张表的 FullEvents 最大？",
        "画出瓶颈迁移：宽度 1 → 宽度 8 → 加 LQ 到 64 → 加 IQ 到 128，现在轮到谁？",
        "iq 64→128 只省约 3.7%，但 rob_full 从几十跳到六万多。下一步该加什么？先预测，任务 7 验收。",
    ])

    s = d.slide("任务 3a · 必须先做这个", "在 qnn 上换预测器。先做完再做 3b",
                "先只在 qnn 上换预测器，看省下的周期有没有超过噪声。")
    s.code([
        "python3 framework/sweep.py --name lab4_bp_qnn --bench qnn \\",
        "  --bench-args " + SEED + " --base \"--cpu o3\" \\",
        "  --vary bp=local,bimode,tournament,tage,ltage --jobs 5",
        "python3 framework/report.py results/lab4_bp_qnn.csv cycles ipc \\",
        "  bp_committed bp_mispredicts bp_miss_rate bp_mpki squash_ratio",
    ], size=13)
    s.ask([
        "从 local 换到 ltage，省了百分之几？这个数字超过 0.1% 了吗？用一句话写结论。",
        "bp_miss_rate 为什么这么低？qnn 的分支长什么样？",
    ])
    s.callout("顺序反过来，你会得到「分支预测器很重要」这种没有前提的结论。任务 3a 整张表都可以在噪声里，要敢于写无差别。",
              kind="warn")

    s = d.slide("任务 3b · 20 分钟", "同一份 branchy，三种数据",
                "同一份代码、三种数据，各换一遍预测器。必须先做完 3a。")
    s.code([
        "for m in 0 1 2; do",
        "  python3 framework/sweep.py --name lab4_branchy$m --bench branchy \\",
        "    --bench-args \"$m 4096 50\" --base \"--cpu o3\" \\",
        "    --vary bp=local,bimode,tournament,tage --jobs 4",
        "done",
        "for m in 0 1 2; do",
        "  echo \"--- mode $m ---\"",
        "  python3 framework/report.py results/lab4_branchy$m.csv \\",
        "    insts cycles ipc bp_committed bp_mispredicts \\",
        "    bp_miss_rate squashed_insts l1d_mpki",
        "done",
    ], size=13)

    s = d.slide("任务 3b · 写进报告", "先证明差异不是访存、不是指令数",
                "先用指令数和 L1 失效证明差异来自分支，再解释三种数据。")
    s.why("三种 mode 是同一份代码、三种数据。insts 和 l1d_mpki 差不多，差异才能算在分支预测上。local 只有 PC，没有历史：周期 7 的模式光看 PC 是同一条分支，学不会。带历史的预测器能把这 7 拍分开。mode 1 的数据排过序，分支方向很长一段不变，弱预测器也够。")
    s.ask([
        "三种 mode 的 insts 差多少？l1d_mpki 是多少？这两项过关，才能说差异来自分支预测。",
        "mode 0 上 local 的误预测率是多少？ROI 里提交了多少条分支，其中多少条是那个 if？用这个拆分解释总误预测率。",
        "mode 2 上 local 和另外三个差几倍？local 的输入只有 PC，周期 7 的模式光看 PC 能分开吗？",
        "mode 1 上四个都很好。什么样的数据不需要好预测器？「先排序再遍历」能不能当成一种软件优化？",
    ])

    s = d.slide("任务 4a · 5 分钟 · 不许看数据", "先把三个数写进报告",
                "不许看 csv。按课本把 mode 2 的误预测率手算出来，写下来。")
    s.callout("这三个数写完才允许看 lab4_branchy2.csv。事后补的手推表按 0 分。",
              kind="warn")
    s.why("两位饱和计数器：强取、弱取、弱不取、强不取。课本默认第 k 次的更新，在第 k+1 次预测之前已经生效。mode 2 每 7 次错几次，先按这个假设手算，再折算到全部已提交分支上。回边分支假设从不猜错。")
    s.steps([
        "mode 2 上，那条 if 每 7 次错几次？误预测率 = ____%。用指导书 §1.6 你填过的手推表。",
        "ROI 里一共提交多少条分支？其中 if 占多少条？（n × iters = ?）",
        "假设回边分支从不猜错，折算到全部提交的分支，bp_miss_rate 应当是 ____%。",
    ])

    s = d.slide("任务 4b · 4c · 对不上就提假设", "不许直接选一个信",
                "把手算和实测对上。对不上就写一个能用实验判决的假设。")
    s.steps([
        "看 lab4_branchy2.csv 里 local 那一行的 bp_miss_rate，和 4a 差几倍？",
        "三种可能：你算错了；gem5 错了；模型的某个前提不成立。逐个排除。",
        "先排除算错：用 bp_mispredicts ÷ (n × iters) 反算那条 if 自己的误预测率，看是不是一个整数 / 7。",
        "预测发生在取指级。更新发生在什么时候？§1.6 那句「第 k 次的更新在第 k+1 次预测前已经生效」，在 8 发射乱序核上凭什么成立？",
    ])
    s.h3("假设按这个格式写")
    s.code([
        "假设：",
        "可测量的预言：如果假设成立，那么当我 ____ 时，____ 应当 ____",
        "如果观测到 ____，则假设被否定",
    ], size=14)
    s.text("预测在取指、更新在提交。核越宽，同一条分支同时在飞的越多。能改变这个数的参数就是宽度。",
           size=14)

    s = d.slide("任务 4d · 判决实验 + 对照组", "没有 mode 0 那一组，任务 4 判 0",
                "用宽度当旋钮做判决。mode 0 那组是对照，没有就判 0。")
    s.why("mode 2 有规律，窄机器若因为在飞的分支更少而更新得及，误预测率应该更低。mode 0 是随机的，没有规律可学。没有这组对照，你只能说「窄机器预测更准」，排除不了「窄机器天生更准」这种平凡解释。")
    s.code([
        "python3 framework/sweep.py --name lab4_lag --bench branchy \\",
        "  --bench-args \"2 4096 50\" --base \"--cpu o3 --bp local\" \\",
        "  --vary width=1,2,3,4,6,8 --jobs 6",
        "python3 framework/sweep.py --name lab4_lag0 --bench branchy \\",
        "  --bench-args \"0 4096 50\" --base \"--cpu o3 --bp local\" \\",
        "  --vary width=1,2,3,4,6,8 --jobs 6",
    ], size=13)
    s.text("report 的列：cycles ipc bp_committed bp_mispredicts bp_miss_rate squashed_insts squash_ratio。对照组至少看 bp_mispredicts 和 bp_miss_rate。",
           size=14)

    s = d.slide("任务 4d · 写进报告", "变宽了，程序反而变慢",
                "把误预测率折成 k/7，并解释为什么机器变宽、程序会变慢。")
    s.why("核变宽，每拍能做的指令多了，猜错一次扔掉的也多了。squashed_insts 跟着宽度涨。更新又来不及，bp_miss_rate 也涨。两笔加起来可以盖过变宽带来的吞吐，程序就变慢了。写代价时看 squashed_insts。")
    s.ask([
        "判决组的 bp_miss_rate 折算到那条 if（除掉其它分支的占比），写成 k/7。width=1 时和你 4a 的 k 对上了吗？",
        "对照组各宽度之间的差异有没有超过 0.1%？写满三句：这说明了什么。",
        "判决组从 width=2 到 width=4，周期发生了什么？用 bp_miss_rate 和 squashed_insts 解释：宽度买到了什么，又赔掉了什么？哪个宽度最快？",
        "width=8 时 squash_ratio 是多少？写成：每提交 1 条指令，就有 ___ 条被扔掉。",
    ])

    s = d.slide("任务 4e · 5 分钟", "去源码里找更新发生在哪",
                "打开 gem5 的更新函数，确认计数器是在提交时改的，不是猜错时改的。")
    s.code([
        "sed -n '/^LocalBP::update/,/^}/p' gem5/src/cpu/pred/2bit_local.cc",
    ], size=14)
    s.why("猜错时执行级立刻 squash，这时会调一次 update，但 squashed 为真就直接 return，计数器不动。真正改计数器是在提交正确的分支时。所以更新点在提交，不在执行。这就是 4c 那个假设的源码形态。")
    s.ask([
        "if (squashed) return; 是在什么场合进来的？分支在执行级判出错，立刻 squash，这时会调一次 update。",
        "猜错时什么都不改，那计数器到底在什么时刻被改？在 gem5/src/cpu/o3/commit.cc 里搜 branchPred。",
        "把 4c 的假设改写成一句关于这段源码的话。报告最后一句用这个格式：课本假设 ____；在 ____ 的机器上不成立，因为 ____；实测误预测率从 ____ 变成 ____。",
    ])

    s = d.slide("任务 5 · 20 分钟", "宽度 × 预测器。负载是 mode 0",
                "随机数据上把宽度和预测器一起扫，看加宽买到的加速是不是一样多。")
    s.code([
        "python3 framework/sweep.py --name lab4_wxbp --bench branchy \\",
        "  --bench-args \"0 4096 50\" --base \"--cpu o3\" \\",
        "  --vary width=1,2,4,8 --vary bp=local,tage --jobs 8",
        "python3 framework/report.py results/lab4_wxbp.csv cycles ipc \\",
        "  bp_mispredicts bp_miss_rate squashed_insts squash_ratio",
    ], size=13)
    s.ask([
        "local 和 tage 在宽度 1→8 上的加速比各是多少？同样加宽 8 倍，为什么买到的不一样多？",
        "这里的 bp_miss_rate 随宽度基本不变，任务 4d 的判决组却变。为什么？变的是 squashed_insts。",
        "宽度每翻一倍，squashed_insts 大约变成几倍？这对「要不要做 16 发射」意味着什么？",
        "已经决定做到 8 发射，预测器的预算该跟着涨，还是可以不动？",
    ])

    s = d.slide("任务 6 · 10 分钟", "BTB：另一半问题",
                "方向预测器不动，只改 BTB 大小，找「够用即止」的那个拐点。")
    s.code([
        "python3 framework/sweep.py --name lab4_btb --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --bp tournament\" \\",
        "  --vary btb-entries=8,32,128,512,4096 --jobs 5",
        "python3 framework/report.py results/lab4_btb.csv cycles ipc \\",
        "  bp_mispredicts bp_miss_predictor bp_miss_btb btb_hit_rate",
    ], size=13)
    s.ask([
        "BTB=8 时，bp_miss_btb 占 bp_mispredicts 的几成？BTB=32 时呢？",
        "BTB 从 32 加到 4096，bp_miss_btb 少了多少，周期少了多少？拐点在哪？",
        "用这个拐点反推 qnn 的 ROI 里有多少条静态分支，再去 bench/src/qnn.c 里数。",
    ])

    s = d.slide("任务 7 · 15 分钟 · ★交付物", "先预测提升百分之几，再跑",
                "把今天觉得有用的资源一次加满。先写预测的提升，再跑。")
    s.code([
        "python3 framework/sweep.py --name lab4_allin --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu o3 --width 8 --rob 384 --iq 128 \\",
        "          --lq 128 --sq 64 --int-regs 512 --bp tage_sc_l\" \\",
        "  --vary l1d-size=32kB --jobs 1",
        "python3 framework/report.py results/lab4_allin.csv cycles ipc \\",
        "  rob_full_events iq_full_events lq_full_events sq_full_events \\",
        "  bp_miss_rate l1d_mlp load_to_use squash_ratio",
    ], size=12)
    s.why("一项一项加的时候，收益总被下一张满的表截住。全加上去，多半还是从一张表满换成另一张表满。qnn 那 580 万条指令一条没少。再快一截，得少发指令，实验五做的就是这个。")

    s = d.slide("任务 7 · 这张表就是本次要交的", "最后一行回答：再快一倍只能靠什么",
                "填这张表。最后一句回答：资源加满之后，再快一倍只能靠什么。")
    s.table([
        ["花在哪", "qnn 上的收益", "branchy 上的收益", "你的判断"],
        ["宽度 1→8", "", "", ""],
        ["ROB 192→384", "", "不必测", ""],
        ["LQ 32→64", "", "不必测", ""],
        ["IQ 64→128", "", "不必测", ""],
        ["local→tage_sc_l", "", "", ""],
        ["全加", "", "", ""],
    ], [3.0, 2.6, 2.8, 2.8], row_h=0.38, size=13, aligns=[L, L, L, L],
       hi_rows=(6,))
    s.ask([
        "相对什么都不加的 --cpu o3，实际提升了百分之几？和你的预测差多少？",
        "哪张表的 FullEvents 最大？钱花光之后瓶颈是谁？",
        "这些「加资源」已经见顶。再快一倍只能靠什么？这就是实验五要做的事。",
    ])

    s = d.slide("思考题 1 · 回收实验三", "其余五问按指导书写，第 6 题留给实验五",
                "用 timing 重跑实验三的替换策略，看排名按失效和按周期是不是一回事。")
    s.code([
        "python3 framework/sweep.py --name lab4_l3timing --bench qnn \\",
        "  --bench-args " + SEED + " \\",
        "  --base \"--cpu timing --l1d-size 64kB --l1d-assoc 4\" \\",
        "  --vary l1d-repl=lru,mru,random,lfu,bip --jobs 5",
        "python3 framework/report.py results/lab4_l3timing.csv \\",
        "  cycles ipc l1d_misses l1d_mshr_misses l1d_mlp",
    ], size=13)
    s.ask([
        "按失效数排名变了没有？按周期数排名呢？周期差超过 0.1% 了吗？l1d_mlp 为什么是这个值？",
        "用一句话：「哪个策略更好」和「换策略值不值得」，分别由谁决定？",
    ])

    s = d.slide("交什么", "手推表、对照组、迁移图，缺一就丢该题",
                "必须交动手前的手推表、mode 0 对照，以及「变宽反而变慢」的解释。")
    s.table([
        ["内容", "分"],
        ["任务 1+2 的预测、实测、瓶颈迁移图", "25"],
        ["任务 3 三 mode + insts / l1d_mpki 对照", "15"],
        ["任务 4：手推 → 对质 → 假设 → 判决 → 源码", "30"],
        ["任务 5/6/7，含任务 7 那张表", "20"],
        ["思考题", "10"],
    ], [8.6, 1.2], row_h=0.40, size=15, aligns=[L, L])
    s.callout("禁止：写 ROB 没有用；把 <0.1% 当结论；不报任务 3a 就说预测器很重要；用 bp_miss_rate 论证代价（代价看 squashed_insts）。",
              kind="warn")

    return d.save(out_path(4))


if __name__ == "__main__":
    build()
