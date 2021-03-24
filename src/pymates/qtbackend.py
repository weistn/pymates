from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter
from PySide6.QtCore import QPointF
from pymates.sizes import FontWeight

qpaintDevice = None
xdpi = 72
ydpi = 72

def qtInit(paintDevice):
    global qpaintDevice
    qpaintDevice = paintDevice
    global xdpi
    xdpi = paintDevice.logicalDpiX()
    global ydpi
    ydpi = paintDevice.logicalDpiY()

def hPtToPx(pt):
    return pt/72*ydpi

def wPtToPx(pt):
    return pt/72*xdpi

def wPxToPt(px):
    return px*72/xdpi

def hPxToPt(px):
    return px*72/ydpi

def qtColor(color):
    color.qcolor = QColor(color.r, color.g, color.b)

def qtFont(font):
    qfont = QFont(font.family, font.size)
    if font.weight == FontWeight.Thin:
        qfont.setWeight(QFont.Thin)
    elif font.weight == FontWeight.ExtraLight:
        qfont.setWeight(QFont.ExtraLight)
    elif font.weight == FontWeight.Light:
        qfont.setWeight(QFont.Light)
    elif font.weight == FontWeight.Normal:
        qfont.setWeight(QFont.Normal)
    elif font.weight == FontWeight.Medium:
        qfont.setWeight(QFont.Medium)
    elif font.weight == FontWeight.DemiBold:
        qfont.setWeight(QFont.DemiBold)
    elif font.weight == FontWeight.Bold:
        qfont.setWeight(QFont.Bold)
    elif font.weight == FontWeight.ExtraBold:
        qfont.setWeight(QFont.ExtraBold)
    elif font.weight == FontWeight.Black:
        qfont.setWeight(QFont.Black)
    if font.italic:
        qfont.setItalic(True)
    if font.underline:
        qfont.setUnderline(True)
    if font.strikeOut:
        qfont.setStrikeOut(True)
    font.qfont = qfont

class qtFontMetrics:
    def __init__(self, qfont):
        self.qmetrics = QFontMetricsF(qfont, qpaintDevice)
        # self.spaceAdvance = self.qmetrics.horizontalAdvanceChar(" ")
        self.ascent = hPxToPt(self.qmetrics.ascent())
        self.descent = hPxToPt(self.qmetrics.descent())
        self.leading = hPxToPt(self.qmetrics.leading())
        # print(f"Metrics {qfont.family()} {qfont.pointSize()} {self.ascent} {self.descent} {self.leading}")
        print(f"ptMetrics {qfont.family()} {qfont.pointSize()} {self.qmetrics.ascent()} {self.qmetrics.descent()} {self.qmetrics.leading()}")

    def advance(self, txt):
        return wPxToPt(self.qmetrics.horizontalAdvance(txt, -1))

def nativeFontMetrics(font):
    if not hasattr(font, "qfont"):
        qtFont(font)
    return qtFontMetrics(font.qfont)

class qtPainter:
    def __init__(self, qpainter):
        self.qpainter = qpainter

    def setPen(self, color):
        if not hasattr(color, "qcolor"):
            qtColor(color)
        self.qpainter.setPen(color.qcolor)
    
    def setFont(self, font):
        if not hasattr(font, "qfont"):
            qtFont(font)
        self.qpainter.setFont(font.qfont)

    def startText(self, x, y):
        pass

    def drawText(self, x, y, txt):
        self.qpainter.drawText(QPointF(wPtToPx(x), hPtToPx(y)), txt)

    def finish(self):
        pass