# 实验六前置补丁：让 gem5 的 RISC-V SE 模式认识页表里的 uncacheable 标志。
#
# 不打这个补丁，加速器的 MMIO 寄存器访问会出两类错：
#   1) 被 L1 数据 Cache 截住 —— 写 GO 出不去、读 STATUS 永远命中旧值；
#   2) 在乱序核上被投机重排 —— 读 STATUS 跑到写 GO 前面去，
#      于是"等加速器算完"这一步直接被跳过，第二条命令撞上还在忙的加速器。
# 所以要同时设 UNCACHEABLE(别进 Cache) 和 STRICT_ORDER(别重排、别投机)。
#
# x86 和 ARM 的路径都是这么写的（src/arch/x86/tlb.cc:251 等处
# 一律是 `Request::UNCACHEABLE | Request::STRICT_ORDER`），只有 RISC-V 漏了。
#
# 用法：  python3 patch_riscv_tlb.py [gem5根目录]     # 默认 ./gem5
# 这个脚本是幂等的，可以重复执行；也能把旧版本(只设了 UNCACHEABLE)升上来。
#
# ★ 打完补丁必须重新编译 gem5：
#     cd gem5 && scons build/RISCV/gem5.opt -j8
#   只有 tlb.cc 一个文件要重编，剩下的时间全在链接上，实测 2 分 53 秒。
import io
import os
import sys

GEM5 = sys.argv[1] if len(sys.argv) > 1 else "gem5"
TLB = os.path.join(GEM5, "src", "arch", "riscv", "tlb.cc")

MARK = "cssys 实验六"

OLD = """        Addr vaddr = getValidAddr(req->getVaddr(), tc, mode);
        Addr paddr;

        if (!p->pTable->translate(vaddr, paddr))
            return std::make_shared<GenericPageTableFault>(req->getVaddr());

        req->setPaddr(paddr);

        return NoFault;"""

NEW = """        Addr vaddr = getValidAddr(req->getVaddr(), tc, mode);

        /* ---- cssys 实验六：让 SE 模式认识 uncacheable 页 -----------------
           gem5 的 x86/ARM 在 SE 模式下会把页表项里的 Uncacheable 位传给
           访存请求，RISC-V 这条路径漏了——它只调 translate() 取物理地址，
           把页属性整个丢掉了。少了这一步会出两类错：

             UNCACHEABLE 没设 -> 写 GO 停在 L1 出不去，读 STATUS 命中旧值；
             STRICT_ORDER 没设 -> 乱序核会把读 STATUS 投机到写 GO 前面执行。
                 两条访问地址不同(0x28 vs 0x20)，LSQ 的访存序违例检查只看
                 地址重叠，抓不到这一次；于是"等算完"被静默跳过。

           x86 对设备内存一律是 UNCACHEABLE | STRICT_ORDER，我们照抄。
           lookup() 一次同时拿到物理页号和页属性，比原来还少查一次表。 */
        const EmulationPageTable::Entry *pte = p->pTable->lookup(vaddr);
        if (!pte)
            return std::make_shared<GenericPageTableFault>(req->getVaddr());

        if (pte->flags & EmulationPageTable::Uncacheable)
            req->setFlags(Request::UNCACHEABLE | Request::STRICT_ORDER);

        req->setPaddr(pte->paddr + p->pTable->pageOffset(vaddr));

        return NoFault;"""

# v1 补丁只设了 UNCACHEABLE。整块换掉，保证服务器上的源码和发给学生的一模一样。
V1 = """        Addr vaddr = getValidAddr(req->getVaddr(), tc, mode);

        /* ---- cssys 实验六：让 SE 模式认识 uncacheable 页 -----------------
           gem5 的 x86/ARM 在 SE 模式下会把页表项里的 Uncacheable 位传给
           访存请求，RISC-V 这条路径漏了——它只调 translate() 取物理地址，
           把页属性整个丢掉了。结果是：对加速器 MMIO 寄存器的写会停在 L1
           里出不去，读 STATUS 会一直命中 L1 拿到旧值。
           lookup() 一次同时拿到物理页号和页属性，比原来还少查一次表。 */
        const EmulationPageTable::Entry *pte = p->pTable->lookup(vaddr);
        if (!pte)
            return std::make_shared<GenericPageTableFault>(req->getVaddr());

        if (pte->flags & EmulationPageTable::Uncacheable)
            req->setFlags(Request::UNCACHEABLE);

        req->setPaddr(pte->paddr + p->pTable->pageOffset(vaddr));

        return NoFault;"""

if not os.path.isfile(TLB):
    sys.exit("找不到 %s —— 第一个参数应当是 gem5 的根目录" % TLB)

with io.open(TLB, encoding="utf-8") as fh:
    src = fh.read()

if MARK in src:
    if NEW in src:
        print("already patched (v2), nothing to do")
        sys.exit(0)
    if src.count(V1) == 1:
        with io.open(TLB, "w", encoding="utf-8") as fh:
            fh.write(src.replace(V1, NEW))
        print("upgraded v1 -> v2 (added STRICT_ORDER)")
        sys.exit(0)
    print("ERROR: 打过补丁但认不出版本，请手工检查 " + TLB)
    sys.exit(1)

n = src.count(OLD)
if n != 1:
    print("ERROR: anchor found %d times, expected 1" % n)
    sys.exit(1)

with io.open(TLB, "w", encoding="utf-8") as fh:
    fh.write(src.replace(OLD, NEW))
print("patched OK (v2)")
