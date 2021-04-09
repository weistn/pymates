from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QFontDatabase
from PySide6.QtCore import QPointF

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

def qtMapWeight(weight):
    if weight <= 100:
        return QFont.Weight.Thin
    if weight <= 300:
        return QFont.Weight.Light
    if weight <= 400:
        return QFont.Weight.Normal
    if weight <= 500:
        return QFont.Weight.Medium
    if weight <= 700:
        return QFont.Weight.Bold
    return QFont.Weight.Black

def qtFont(font):
    qfont = QFont(font.family, font.size)
    qfont.setWeight(qtMapWeight(font.weight))
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

def loadFont(file, family, weight = 400, italic = False):
    QFontDatabase.addApplicationFont(file)

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