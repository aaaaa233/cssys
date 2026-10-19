# -*- coding: utf-8 -*-
"""《计算机系统综合设计实验》讲课用 PPT —— 共用视觉系统。

设计口径（7 次实验统一）：
  * 16:9，13.333 × 7.5 英寸
  * 讲课用：少字、大图、留白。正文一页不超过 6 行，关键数字用超大字号单独占位
  * 配色是内容驱动的：石墨=结构，朱砂=花钱/超预算/警示，青绿=省钱/免费
  * 视觉母题 = **按面积成比例的方块**（本课程的核心就是"面积去哪了"），
    不用装饰色条、不用标题下划线
  * 字体：微软雅黑（中文/西文正文）+ Consolas（数字与命令行）
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
import copy
import math

# ---------------------------------------------------------------- 配色
INK        = "22282F"   # 石墨（暗场底 / 主文字）
INK_SOFT   = "6B7684"   # 冷灰（次要文字、说明）
PAPER      = "FFFFFF"   # 纸白
PAPER_DIM  = "F4F5F7"   # 极浅灰（卡片底）
RED        = "C1272D"   # 朱砂：花钱、超预算、陷阱、警示
RED_DIM    = "F6E4E5"   # 朱砂淡底
GREEN      = "0F766E"   # 青绿：省钱、免费、收益
GREEN_DIM  = "E1F0EE"   # 青绿淡底
GOLD       = "B8860B"   # 暗金：强调（用得极少）
WHITE_DIM  = "9AA3AD"   # 暗场上的次要文字

# 每次实验的章节色（封面/节间页取用，正文一律石墨）
LAB_ACCENT = {
    1: "2E5C8A",  # 基线测量   石墨蓝
    2: "0E7C7B",  # Cache      青
    3: "6B4E9B",  # 替换策略   紫
    4: "C25E00",  # 乱序/分支  橙
    5: "A62B5F",  # 自定义指令 洋红
    6: "2C7A4B",  # 加速器     翠
    7: "C1272D",  # 综合设计   朱砂
}

# ---------------------------------------------------------------- 字体
F_SANS = "微软雅黑"
F_MONO = "Consolas"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
M = Inches(0.75)                      # 统一左右页边距
CONTENT_W = SLIDE_W - 2 * M


# ---------------------------------------------------------------- 底层工具
def _set_typeface(run, latin, ea):
    """python-pptx 只写 a:latin；中文必须另外写 a:ea，否则 PowerPoint 用默认宋体。"""
    rPr = run._r.get_or_add_rPr()
    for tag, face in (("a:latin", latin), ("a:ea", ea), ("a:cs", latin)):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", face)


def _line_spacing(para, mult):
    """按倍数设行距（python-pptx 的 line_spacing 传 float 即倍数）。"""
    para.line_spacing = mult


def txt(slide, x, y, w, h, blocks, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
        spacing=1.15, wrap=True):
    """通用文本框。blocks = [(文字, size, bold, color, mono?, 'sup'/'sub'?), ...]
    或 [[run,...], ...]。

    传入一维列表 → 单段；传入二维列表 → 每个子列表一段。
    """
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor

    paras = blocks if blocks and isinstance(blocks[0], list) else [blocks]
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        _line_spacing(p, spacing)
        # 中日韩断行规则：行尾标点悬挂，别让孤零零一个「。」换行；
        # 西文只在词边界断，别把 mem_ctrls 之类拆开。
        pPr = p._p.get_or_add_pPr()
        pPr.set("eaLnBrk", "1")
        pPr.set("hangingPunct", "1")
        pPr.set("latinLnBrk", "0")
        for item in runs:
            s, size, bold, color = item[0], item[1], item[2], item[3]
            mono = item[4] if len(item) > 4 else False
            base = item[5] if len(item) > 5 else None
            r = p.add_run()
            r.text = s
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = RGBColor.from_string(color)
            _set_typeface(r, F_MONO if mono else F_SANS, F_SANS)
            if base:
                r._r.get_or_add_rPr().set(
                    "baseline", "30000" if base == "sup" else "-25000")
    return box


def rect(slide, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE, radius=None):
    sh = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def outline(slide, x, y, w, h, color, width=1.25, dash=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.background()
    sh.line.color.rgb = RGBColor.from_string(color)
    sh.line.width = Pt(width)
    sh.shadow.inherit = False
    if dash:
        ln = sh.line._get_or_add_ln()
        d = ln.makeelement(qn("a:prstDash"), {"val": dash})
        ln.append(d)
    return sh


def line(slide, x1, y1, x2, y2, color=INK_SOFT, width=1.0, dash=None):
    """任意两点之间的直线（画前沿折线、爆炸引导线用）。"""
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, int(x1), int(y1),
                                   int(x2), int(y2))
    c.line.color.rgb = RGBColor.from_string(color)
    c.line.width = Pt(width)
    c.shadow.inherit = False
    if dash:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn("a:prstDash"), {"val": dash}))
    return c


def card(slide, x, y, w, h, fill=PAPER_DIM):
    """内容卡片：淡底 + 圆角，不加边线、不加色条。"""
    return rect(slide, x, y, w, h, fill, MSO_SHAPE.ROUNDED_RECTANGLE, 0.045)


# ---------------------------------------------------------------- 版式
def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    return prs


def blank(prs, dark=False, bg=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    color = bg if bg else (INK if dark else PAPER)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, color)
    return s


def head(slide, title, kicker=None, dark=False, accent=RED):
    """页标题。规矩：标题 34pt 粗；上方可有一行小号提示词；标题下不画线。"""
    y = Inches(0.62)
    if kicker:
        txt(slide, M, y, CONTENT_W, Inches(0.3),
            [(kicker, 13, True, accent)])
        y += Inches(0.42)
    txt(slide, M, y, CONTENT_W, Inches(0.7),
        [(title, 34, True, PAPER if dark else INK)])
    return y + Inches(0.95)


def foot(slide, text, dark=False):
    txt(slide, M, SLIDE_H - Inches(0.75), CONTENT_W, Inches(0.25),
        [(text, 11, False, WHITE_DIM if dark else INK_SOFT)])


# ---------------------------------------------------------------- 组件
def stat(slide, x, y, w, value, label, color=RED, size=64, sub=None,
         align=PP_ALIGN.LEFT, mono=True):
    """大数字callout：数字 60-72pt，标签 13pt 灰。"""
    txt(slide, x, y, w, Inches(0.95), [(value, size, True, color, mono)],
        align=align, spacing=0.95)
    yy = y + Inches(size / 72.0 * 1.02)
    txt(slide, x, yy, w, Inches(0.34), [(label, 13, True, INK)], align=align)
    if sub:
        txt(slide, x, yy + Inches(0.3), w, Inches(0.6),
            [(sub, 11.5, False, INK_SOFT)], align=align, spacing=1.25)


def area_blocks(slide, x, y, w, h, items, gap=Inches(0.045), vertical=False,
                label_size=11.5):
    """★ 本课程的视觉母题：按数值成比例的方块。

    items = [(标签, 数值, 颜色, 文字色), ...]
    横向时按宽度成比例，纵向时按高度成比例。方块内写标签+数值（放得下才写）。
    """
    total = sum(i[1] for i in items)
    span = (h if vertical else w) - gap * (len(items) - 1)
    cur = y if vertical else x
    out = []
    for name, val, fill, fg in items:
        seg = int(span * (val / total))
        if vertical:
            sh = rect(slide, x, cur, w, seg, fill)
            if seg > Inches(0.34):
                txt(slide, x + Inches(0.16), cur + seg / 2 - Inches(0.13),
                    w - Inches(0.32), Inches(0.28),
                    [(name, label_size, True, fg)], anchor=MSO_ANCHOR.MIDDLE)
            cur += seg + gap
        else:
            sh = rect(slide, cur, y, seg, h, fill)
            if seg > Inches(0.62):
                txt(slide, cur, y + h / 2 - Inches(0.2), seg, Inches(0.4),
                    [(name, label_size, True, fg)],
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            cur += seg + gap
        out.append(sh)
    return out


def table(slide, x, y, w, rows, col_w, head_fill=INK, head_fg=PAPER,
          size=13, head_size=12.5, row_h=Inches(0.42), zebra=True,
          aligns=None, mono_cols=(), hi_rows=(), hi_fill=RED_DIM):
    """朴素表格：无 PowerPoint 默认蓝条纹，表头石墨底白字。

    rows[0] 是表头。col_w 是英寸比例列表，会归一化到 w。
    """
    nr, nc = len(rows), len(rows[0])
    tot = sum(col_w)
    gt = slide.shapes.add_table(nr, nc, x, y, w, row_h * nr).table
    gt.first_row = False
    gt.horz_banding = False
    for j, cw in enumerate(col_w):
        gt.columns[j].width = Emu(int(w * cw / tot))
    for i, row in enumerate(rows):
        gt.rows[i].height = row_h if i else Emu(int(row_h * 1.06))
        for j, val in enumerate(row):
            c = gt.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.1)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if i == 0:
                c.fill.fore_color.rgb = RGBColor.from_string(head_fill)
            elif i in hi_rows:
                c.fill.fore_color.rgb = RGBColor.from_string(hi_fill)
            else:
                c.fill.fore_color.rgb = RGBColor.from_string(
                    PAPER_DIM if (zebra and i % 2 == 0) else PAPER)
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = (aligns[j] if aligns else
                           (PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT))
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(head_size if i == 0 else size)
            r.font.bold = (i == 0) or (i in hi_rows)
            r.font.color.rgb = RGBColor.from_string(
                head_fg if i == 0 else (RED if i in hi_rows else INK))
            _set_typeface(r, F_MONO if j in mono_cols else F_SANS, F_SANS)
    return gt


def bullets(slide, x, y, w, items, size=16, gap=Inches(0.52), color=INK,
            marker=GREEN, marker_size=None):
    """图标行：小方块 + 文字。不用 PowerPoint 项目符号（讲课用要留白）。"""
    ms = marker_size or Inches(0.13)
    for k, it in enumerate(items):
        yy = y + gap * k
        rect(slide, x, yy + Inches(0.075), ms, ms,
             marker if isinstance(marker, str) else marker[k])
        runs = it if isinstance(it, list) else [(it, size, False, color)]
        txt(slide, x + ms + Inches(0.22), yy, w - ms - Inches(0.22),
            Inches(0.4), runs, spacing=1.2)


def cover(prs, lab_no, title, sub, meta):
    """封面：暗场，超大标题。title 里用 \\n 手动断行，副题会自动往下让。"""
    accent = LAB_ACCENT[lab_no]
    s = blank(prs, dark=True)
    txt(s, M, Inches(1.55), CONTENT_W, Inches(0.5),
        [("实验 %d" % lab_no, 15, True, accent),
         ("　|　计算机系统综合设计实验", 15, False, WHITE_DIM)])
    n = title.count("\n") + 1          # 标题几行，副题就往下让几行
    txt(s, M, Inches(2.15), Inches(10.6), Inches(0.88) * n,
        [(title, 54, True, PAPER)], spacing=1.12)
    txt(s, M, Inches(2.15) + Inches(0.88) * n + Inches(0.34), Inches(9.6),
        Inches(0.9), [(sub, 19, False, WHITE_DIM)], spacing=1.35)
    txt(s, M, SLIDE_H - Inches(1.05), CONTENT_W, Inches(0.5),
        [(meta, 13, False, WHITE_DIM)])
    return s


def section(prs, no, title, sub=None, accent=RED):
    """节间页：暗场，编号 + 一句话。"""
    s = blank(prs, dark=True)
    txt(s, M, Inches(2.5), Inches(2.0), Inches(1.6),
        [(no, 88, True, accent, True)], spacing=0.95)
    txt(s, M + Inches(2.3), Inches(2.62), Inches(9.5), Inches(1.0),
        [(title, 40, True, PAPER)], spacing=1.1)
    if sub:
        txt(s, M + Inches(2.3), Inches(3.72), Inches(9.3), Inches(0.9),
            [(sub, 17, False, WHITE_DIM)], spacing=1.35)
    return s


def punch(prs, lines, sub=None, accent=RED):
    """暗场大字页：用来砸一个结论。lines = [(文字, 是否强调), ...]

    40pt 中文的行距约 0.9 英寸。超过三行就整块上移、副题跟着往下让，
    否则第四行会压在副题上（三行及以内保持原位，别动已经定稿的版）。
    """
    s = blank(prs, dark=True)
    n = len(lines)
    top = Inches(2.35) if n <= 3 else Inches(1.95)
    body_h = Inches(0.9) * n
    runs = [[(t, 40, True, accent if hi else PAPER)] for t, hi in lines]
    txt(s, M, top, CONTENT_W, body_h, runs, spacing=1.32)
    if sub:
        sub_y = Inches(5.55) if n <= 3 else top + body_h + Inches(0.5)
        txt(s, M, sub_y, Inches(11.0), Inches(0.9),
            [(sub, 16, False, WHITE_DIM)], spacing=1.35)
    return s


def code(slide, x, y, w, lines, size=13, fill=INK, fg="D7DBE0", hi=()):
    """命令行块：石墨底等宽字。hi 为需要朱砂高亮的行号。"""
    h = Inches(0.3) * len(lines) + Inches(0.34)
    rect(slide, x, y, w, h, fill, MSO_SHAPE.ROUNDED_RECTANGLE, 0.06)
    runs = [[(l, size, i in hi, RED if i in hi else fg, True)]
            for i, l in enumerate(lines)]
    txt(slide, x + Inches(0.26), y + Inches(0.17), w - Inches(0.5),
        h - Inches(0.34), runs, spacing=1.28)
    return h


def _wrapped_lines(text, width_emu, size):
    """估算这行字在给定宽度里要占几行：中文按 1 个字宽，ASCII 按 0.55 折算。"""
    pts = width_emu / 914400.0 * 72.0
    ems = sum(0.55 if " " <= c <= "~" else 1.0 for c in text)
    return max(1, int(math.ceil(ems * size / pts)))


def note(slide, x, y, w, text, color=RED, fill=RED_DIM, size=14.5, icon="★"):
    """强调条：淡底卡片 + 星号 + 一句话（不是色条，是整块淡底卡片）。

    高度取「字数档」和「实际折行数」的较大者。只按字数算的话，
    窄框里的长句会排到三行、把卡片撑破——那是文字溢出，读者一眼就看得见。
    """
    h = max(Inches(0.62) if len(text) < 34 else Inches(0.92),
            Inches(0.30 + 0.32 * _wrapped_lines(text, w - Inches(1.0), size)))
    card(slide, x, y, w, h, fill)
    txt(slide, x + Inches(0.28), y + Inches(0.02), Inches(0.4), h,
        [(icon, size + 1, True, color)], anchor=MSO_ANCHOR.MIDDLE)
    txt(slide, x + Inches(0.72), y + Inches(0.02), w - Inches(1.0), h,
        [(text, size, True, color)], anchor=MSO_ANCHOR.MIDDLE, spacing=1.25)
    return h
