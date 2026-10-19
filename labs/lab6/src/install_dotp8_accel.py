#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_dotp8_accel.py —— 把 dotp8 加速器装进 gem5 的构建系统。

实验三你已经装过一次 SimObject（替换策略），那次要动三个地方，
因为它是塞进 gem5 已有的目录里的。这次简单得多：**新建一个目录就行。**

    gem5/src/cssys/
        Dotp8Accel.py     Python 侧的参数声明
        dotp8_accel.hh    接口
        dotp8_accel.cc    实现
        SConscript        告诉 scons 这个目录里有什么

gem5 的 src/SConscript 会**自动递归**执行 src/ 下每个子目录里的 SConscript，
所以不需要在别的地方登记。这也是给 gem5 加东西最干净的姿势：
不改任何一个已有文件，删掉目录就完全恢复原样。

用法：  python3 install_dotp8_accel.py [gem5根目录] [源文件目录]
        默认分别是 ./gem5 和脚本自己所在的目录。
脚本是幂等的，重复执行只是重新覆盖一遍。
"""
import os
import shutil
import sys

FILES = ("Dotp8Accel.py", "dotp8_accel.hh", "dotp8_accel.cc", "SConscript")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    gem5 = sys.argv[1] if len(sys.argv) > 1 else "gem5"
    srcdir = sys.argv[2] if len(sys.argv) > 2 else here

    if not os.path.isdir(os.path.join(gem5, "src")):
        sys.exit("找不到 %s/src —— 第一个参数应当是 gem5 的根目录" % gem5)

    dst = os.path.join(gem5, "src", "cssys")
    os.makedirs(dst, exist_ok=True)
    for i, f in enumerate(FILES, 1):
        s = os.path.join(srcdir, f)
        if not os.path.isfile(s):
            sys.exit("找不到 %s" % s)
        shutil.copyfile(s, os.path.join(dst, f))
        print("[%d/%d] 复制 %s" % (i, len(FILES), f))

    print("""
装好了。接下来两件事，顺序不能反：

  1) 打 TLB 补丁（不打的话 MMIO 根本走不通）：
         python3 %s %s
  2) 重新编译：
         cd %s && scons build/RISCV/gem5.opt -j8

编译完自检（应当打印出加速器的参数）：
     %s/build/RISCV/gem5.opt --help >/dev/null && \\
     python3 -c "import sys; sys.path.insert(0,'%s/build/RISCV/python'); \\
                 import m5.objects.Dotp8Accel; print('Dotp8Accel OK')"
""" % (os.path.join(here, "patch_riscv_tlb.py"), gem5, gem5, gem5, gem5))


if __name__ == "__main__":
    main()
