#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_cssys_rp.py —— 把自己写的替换策略注册进 gem5 的构建系统。

gem5 里加一个 SimObject 要动三个地方，缺一不可：
    1. C++ 源文件                cssys_rp.{hh,cc}
    2. Python 侧的参数声明        ReplacementPolicies.py 里加一个类
    3. 构建脚本                  SConscript 里加 sim_objects 条目 + Source()

漏掉第 2 步：编译能过，但 config 脚本里 import 不到 CssysRP。
漏掉第 3 步：连 params/CssysRP.hh 都生成不出来，编译直接失败。

用法：  python3 install_cssys_rp.py <gem5根目录> <cssys_rp.hh/cc 所在目录>
脚本是幂等的，重复执行不会重复插入。
"""
import os
import shutil
import sys

PY_CLASS = '''

class CssysRP(BaseReplacementPolicy):
    type = "CssysRP"
    cxx_class = "gem5::replacement_policy::Cssys"
    cxx_header = "mem/cache/replacement_policies/cssys_rp.hh"

    evict_mru = Param.Bool(
        False, "True: evict the most recently used way (MRU); "
               "False: evict the least recently used way (LRU)"
    )
'''


def main():
    gem5 = sys.argv[1] if len(sys.argv) > 1 else "gem5"
    srcdir = sys.argv[2] if len(sys.argv) > 2 else "."
    rp = os.path.join(gem5, "src", "mem", "cache", "replacement_policies")
    if not os.path.isdir(rp):
        sys.exit(f"找不到 {rp}")

    # 1. 拷贝源文件
    for f in ("cssys_rp.hh", "cssys_rp.cc"):
        shutil.copyfile(os.path.join(srcdir, f), os.path.join(rp, f))
        print(f"[1/3] 复制 {f}")

    # 2. ReplacementPolicies.py
    pyf = os.path.join(rp, "ReplacementPolicies.py")
    text = open(pyf, encoding="utf-8").read()
    if "class CssysRP" in text:
        print("[2/3] ReplacementPolicies.py 已注册，跳过")
    else:
        open(pyf, "a", encoding="utf-8").write(PY_CLASS)
        print("[2/3] ReplacementPolicies.py 已追加 CssysRP")

    # 3. SConscript
    sc = os.path.join(rp, "SConscript")
    text = open(sc, encoding="utf-8").read()
    changed = False
    if "'CssysRP'" not in text:
        text = text.replace("'BaseReplacementPolicy', 'DuelingRP'",
                            "'BaseReplacementPolicy', 'CssysRP', 'DuelingRP'")
        changed = True
    if "Source('cssys_rp.cc')" not in text:
        text = text.replace("Source('bip_rp.cc')",
                            "Source('bip_rp.cc')\nSource('cssys_rp.cc')")
        changed = True
    if changed:
        open(sc, "w", encoding="utf-8").write(text)
        print("[3/3] SConscript 已更新")
    else:
        print("[3/3] SConscript 已是最新，跳过")

    print("\n接下来重新编译： cd %s && scons build/RISCV/gem5.opt -j8" % gem5)


if __name__ == "__main__":
    main()
