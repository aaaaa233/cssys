# -*- coding: utf-8 -*-
"""生成七次实验的操作步骤 PPT。不覆盖各次的幻灯片.pptx。

    python _tools/ppt/steps_all.py
"""
import steps_lab1
import steps_lab2
import steps_lab3
import steps_lab4
import steps_lab5
import steps_lab6
import steps_lab7


def main():
    for mod in (steps_lab1, steps_lab2, steps_lab3, steps_lab4,
                steps_lab5, steps_lab6, steps_lab7):
        mod.build()


if __name__ == "__main__":
    main()
