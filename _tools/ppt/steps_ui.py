# -*- coding: utf-8 -*-
"""操作步骤 PPT 的版式。

和 lab1.py … lab7.py 分开：那些脚本生成讲义「幻灯片.pptx」，这里生成
「操作步骤.pptx」。不要改讲义那一套。

一页只放学生接着要做的事：命令、要填的表、报告里要回答的问题。
"""
import os

import theme as T
from theme import (INK, PAPER_DIM, RED, RED_DIM, GREEN, GREEN_DIM, CONTENT_W, M)
from pptx.util import Inches, Emu
from pptx.enum.text import MSO_ANCHOR

BOTTOM = Inches(6.50)
CODE_INNER = CONTENT_W - Inches(0.62)


def out_path(lab_no):
    return os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "labs", "lab%d" % lab_no, "操作步骤.pptx"))


class Deck(object):
    def __init__(self, lab_no, foot):
        self.lab_no = lab_no
        self.accent = T.LAB_ACCENT[lab_no]
        self.foot = foot
        self.prs = T.new_deck()
        self.cur = None

    def _close(self):
        if self.cur is not None:
            self.cur.check()
            self.cur = None

    def cover(self, title, sub, meta):
        self._close()
        T.cover(self.prs, self.lab_no, title, sub, meta)
        return self

    def slide(self, kicker, title, aim=None):
        self._close()
        self.cur = Frame(self, kicker, title, aim)
        return self.cur

    def save(self, path):
        self._close()
        path = os.path.abspath(path)
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        self.prs.save(path)
        n = len(self.prs.slides._sldIdLst)
        print("wrote %s  (%d slides)" % (path, n))
        return path


class Frame(object):
    def __init__(self, deck, kicker, title, aim=None):
        self.deck = deck
        self.accent = deck.accent
        self.name = title
        self.s = T.blank(deck.prs)
        T.foot(self.s, deck.foot)
        T.txt(self.s, M, Inches(0.50), CONTENT_W, Inches(0.26),
              [(kicker, 13, True, self.accent)])
        n = T._wrapped_lines(title, CONTENT_W, 28)
        th = Inches(0.42 * n)
        T.txt(self.s, M, Inches(0.78), CONTENT_W, th,
              [(title, 28, True, INK)], spacing=1.05)
        self.y = Inches(0.78) + th + Inches(0.08)
        if aim:
            size = 16
            an = max(1, T._wrapped_lines(aim, CONTENT_W, size))
            ah = Inches(0.28 * an + 0.02)
            self._need(ah)
            T.txt(self.s, M, self.y, CONTENT_W, ah,
                  [(aim, size, False, INK)], spacing=1.12)
            self.y += ah + Inches(0.04)

    def check(self):
        if self.y > BOTTOM:
            raise RuntimeError("%s 溢出，底边 %.2f in（上限 6.50）" % (
                self.name, self.y / 914400.0))

    def _need(self, h):
        if self.y + h > BOTTOM:
            raise RuntimeError("%s 放不下 %.2f in 的一块（当前 %.2f）" % (
                self.name, h / 914400.0, self.y / 914400.0))

    def h3(self, text, color=None):
        h = Inches(0.34)
        self._need(h)
        T.txt(self.s, M, self.y, CONTENT_W, h,
              [(text, 16, True, color or self.accent)])
        self.y += h
        return self

    def text(self, body, size=15, bold=False, color=None, mono=False):
        color = INK if color is None else color
        n = T._wrapped_lines(body, CONTENT_W, size)
        h = Inches(0.28 * n + 0.06)
        self._need(h)
        T.txt(self.s, M, self.y, CONTENT_W, h,
              [(body, size, bold, color, mono)], spacing=1.15)
        self.y += h + Inches(0.06)
        return self

    def steps(self, items, size=15.5, color=None):
        color = color or self.accent
        num_w = Inches(0.38)
        text_w = CONTENT_W - num_w
        for i, it in enumerate(items, 1):
            raw = it if isinstance(it, str) else "".join(r[0] for r in it)
            nlines = max(1, T._wrapped_lines(raw, text_w, size))
            h = Inches(0.30 * nlines + 0.08)
            self._need(h)
            T.txt(self.s, M, self.y, num_w, h,
                  [(str(i), size, True, color, True)],
                  anchor=MSO_ANCHOR.TOP)
            runs = [(it, size, False, INK)] if isinstance(it, str) else it
            T.txt(self.s, M + num_w, self.y, text_w, h, runs, spacing=1.12)
            self.y += h + Inches(0.04)
        self.y += Inches(0.06)
        return self

    def code(self, lines, size=13, hi=()):
        for ln in lines:
            if T._wrapped_lines(ln, CODE_INNER, size) > 1:
                raise RuntimeError("%s 命令会折行: %s" % (self.name, ln))
        h = T.code(self.s, M, self.y, CONTENT_W, lines, size=size, hi=hi)
        self._need(h)
        self.y += h + Inches(0.12)
        return self

    def table(self, rows, col_w, row_h=0.38, size=13, hi_rows=(),
              aligns=None, mono_cols=(), head_size=12):
        rh = Inches(row_h)
        h = Emu(int(rh * 1.06)) + rh * (len(rows) - 1)
        self._need(h + Inches(0.04))
        T.table(self.s, M, self.y, CONTENT_W, rows, col_w,
                size=size, head_size=head_size, row_h=rh,
                hi_rows=hi_rows, aligns=aligns, mono_cols=mono_cols)
        self.y += h + Inches(0.12)
        return self

    def ask(self, items, heading="报告里要回答"):
        self.h3(heading)
        return self.steps(items, size=15)

    def why(self, body):
        """页边说明。不要小标题，小标题一多就象套话。"""
        paras = [body] if isinstance(body, str) else list(body)
        size = 15
        inner_w = CONTENT_W - Inches(0.56)
        heights = []
        for para in paras:
            n = max(1, T._wrapped_lines(para, inner_w, size))
            heights.append(Inches(0.30 * n + 0.02))
        h = Inches(0.16) + sum(heights, Inches(0)) + Inches(0.10)
        self._need(h)
        T.card(self.s, M, self.y, CONTENT_W, h, PAPER_DIM)
        yy = self.y + Inches(0.12)
        for para, ph in zip(paras, heights):
            T.txt(self.s, M + Inches(0.24), yy, inner_w, ph,
                  [(para, size, False, INK)], spacing=1.15)
            yy += ph
        self.y += h + Inches(0.10)
        return self

    def callout(self, text, kind="warn"):
        if kind == "warn":
            color, fill, icon = RED, RED_DIM, "!"
        elif kind == "ok":
            color, fill, icon = GREEN, GREEN_DIM, "√"
        else:
            color, fill, icon = self.accent, PAPER_DIM, "※"
        # note() 自己算高度；先按同样的规则预留，避免画出页外。
        size = 14.5
        nlines = max(1, T._wrapped_lines(text, CONTENT_W - Inches(1.0), size))
        h = max(Inches(0.62), Inches(0.28 + 0.30 * nlines))
        self._need(h)
        got = T.note(self.s, M, self.y, CONTENT_W, text,
                     color=color, fill=fill, size=size, icon=icon)
        self.y += got + Inches(0.10)
        return self
