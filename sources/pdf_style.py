"""Mise en forme commune des livrables PDF (reportlab)."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

NAVY = colors.HexColor("#1b3350")
TEAL = colors.HexColor("#1f8a8a")
LIGHT = colors.HexColor("#eef3f7")
GRID = colors.HexColor("#9aa9b8")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, fontSize=16, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=TEAL, fontSize=12.5,
                    spaceBefore=10, spaceAfter=4)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], textColor=NAVY, fontSize=11,
                    spaceBefore=6, spaceAfter=3)
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.5, leading=12.5)
CELL = ParagraphStyle("C", parent=BODY, fontSize=8.5, leading=10.5)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
TITLE = ParagraphStyle("T", parent=H1, alignment=TA_CENTER, fontSize=20)
SUB = ParagraphStyle("S", parent=BODY, alignment=TA_CENTER, fontSize=10.5)


def p(text, style=BODY):
    return Paragraph(text, style)


def table(rows, widths, header=True, size=None):
    cell, cellb = CELL, CELLB
    if size:
        cell = ParagraphStyle(f"C{size}", parent=CELL, fontSize=size, leading=size + 2)
        cellb = ParagraphStyle(f"CB{size}", parent=CELLB, fontSize=size, leading=size + 2)
    data = [[p(c, cellb if (header and i == 0) else cell) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), NAVY)]
        style += [("BACKGROUND", (0, i), (-1, i), LIGHT) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(style))
    return t


GREEN = colors.HexColor("#d9efd9")
GREY = colors.HexColor("#e6e6e6")
ORANGE = colors.HexColor("#fce4d6")
BLUE = colors.HexColor("#ddebf7")


def box(d, x, y, w, h, lines, fill=LIGHT, dashed=False, bold_first=True, size=7.5):
    """Rectangle avec texte centré (coordonnées en points, origine en bas à gauche)."""
    from reportlab.graphics.shapes import Rect, String
    r = Rect(x, y, w, h, rx=3, ry=3, fillColor=fill, strokeColor=NAVY if not dashed else colors.grey,
             strokeWidth=0.8)
    if dashed:
        r.strokeDashArray = [3, 2]
    d.add(r)
    lines = lines if isinstance(lines, list) else [lines]
    lh = size + 2
    y0 = y + h / 2 + (len(lines) - 1) * lh / 2 - size / 3
    for i, t in enumerate(lines):
        d.add(String(x + w / 2, y0 - i * lh, t, textAnchor="middle", fontSize=size,
                     fontName="Helvetica-Bold" if (i == 0 and bold_first) else "Helvetica",
                     fillColor=colors.black if not dashed else colors.HexColor("#555555")))


def link(d, x1, y1, x2, y2, label=None, dashed=False, size=6):
    from reportlab.graphics.shapes import Line, String
    ln = Line(x1, y1, x2, y2, strokeColor=colors.grey if dashed else TEAL, strokeWidth=0.8)
    if dashed:
        ln.strokeDashArray = [3, 2]
    d.add(ln)
    if label:
        d.add(String((x1 + x2) / 2, (y1 + y2) / 2 + 2, label, textAnchor="middle", fontSize=size,
                     fillColor=colors.HexColor("#333333")))


def arrow(d, x1, y, x2, label=None, size=6):
    """Flèche horizontale de (x1, y) vers (x2, y), avec étiquette facultative au-dessus."""
    from reportlab.graphics.shapes import Line, Polygon, String
    d.add(Line(x1, y, x2 - 4, y, strokeColor=NAVY, strokeWidth=1))
    d.add(Polygon([x2, y, x2 - 5, y + 3, x2 - 5, y - 3], fillColor=NAVY, strokeColor=NAVY))
    if label:
        d.add(String((x1 + x2) / 2, y + 4, label, textAnchor="middle", fontSize=size,
                     fontName="Helvetica-Bold", fillColor=TEAL))


def build(out, story, title, footer_text, pagesize=A4):
    doc = SimpleDocTemplate(str(out), pagesize=pagesize, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title=title, author="Retail Intelligence - TP J1")

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1 * cm, footer_text)
        canvas.drawRightString(pagesize[0] - 2 * cm, 1 * cm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF généré : {out}")
