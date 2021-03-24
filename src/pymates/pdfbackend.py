from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from pymates.sizes import FontWeight

def pdfInit():
    pass

def pdfColor(color):
    color.pdfcolor = colors.Color(color.r/255, color.g/255, color.b/255)

def pdfFont(font):
    if font.family == "Courier":
        if font.weight.value > FontWeight.Normal.value:
            if font.italic:
                font.pdfname = "Courier-BoldOblique"
            else:
                font.pdfname = "Courier-Bold"
        else:
            if font.italic:
                font.pdfname = "Courier-Oblique"
            else:
                font.pdfname = "Courier"
    elif font.family == "Helvetica":
        if font.weight.value > FontWeight.Normal.value:
            if font.italic:
                font.pdfname = "Helvetica-BoldOblique"
            else:
                font.pdfname = "Helvetica-Bold"
        else:
            if font.italic:
                font.pdfname = "Helvetica-Oblique"
            else:
                font.pdfname = "Helvetica"
    elif font.family == "Times":
        if font.weight.value > FontWeight.Normal.value:
            if font.italic:
                font.pdfname = "Times-BoldItalic"
            else:
                font.pdfname = "Times-Bold"
        else:
            if font.italic:
                font.pdfname = "Times-Italic"
            else:
                font.pdfname = "Times"
    elif font.family == "Symbol":
        font.pdfname = font.family
    elif font.family == "ZapfDingbats":
        font.pdfname = font.family
    else:
        font.pdfname = font.family
    font.pdffont = pdfmetrics.getFont(font.pdfname)

class pdfFontMetrics:
    def __init__(self, font):
        self.font = font
        if hasattr(self.font.pdffont, "ascent"):
            self.ascent = self.font.pdffont.ascent * font.size / 1000
        else:
            self.ascent = self.font.pdffont.face.ascent * font.size / 1000
        if hasattr(self.font.pdffont, "descent"):
            self.descent = -self.font.pdffont.descent * font.size / 1000
        else:
            self.descent = -self.font.pdffont.face.descent * font.size / 1000
        print(f"Metrics {font.pdfname} {font.size} {self.ascent} {self.descent} {0.2*font.size}")
        if hasattr(self.font.pdffont, "face") and hasattr(self.font.pdffont.face, "bbox"):
            print(f"   bbox {list(map(lambda x: x * font.size / 1000, self.font.pdffont.face.bbox))}")
            print(f"   capH {self.font.pdffont.face.capHeight * font.size / 1000}")
            print(f"   lineGap {self.font.pdffont.face.lineGap * font.size / 1000}")
            print(f"   winA {self.font.pdffont.face.winAscent * font.size / 1000}")
            print(f"   winD {self.font.pdffont.face.winDescent * font.size / 1000}")
        self.leading = 0.2*font.size

    def advance(self, txt):
        return self.font.pdffont.stringWidth(txt, self.font.size)

def nativeFontMetrics(font):
    if not hasattr(font, "pdffont"):
        pdfFont(font)
    return pdfFontMetrics(font)

class pdfPainter:
    def __init__(self, page, canvas):
        self.page = page
        self.canvas = canvas
        self.textObject = None

    def setPen(self, color):
        if not hasattr(color, "pdfcolor"):
            pdfColor(color)
        if self.textObject != None:
            self.textObject.setFillColor(color.pdfcolor)
        else:
            self.canvas.setStrokeColor(color.pdfcolor)
    
    def setFont(self, font):
        if not hasattr(font, "pdffont"):
            pdfFont(font)
        if self.textObject != None:
            self.textObject.setFont(font.pdfname, font.size)
        else:
            self.canvas.setFont(font.pdfname, font.size)

    def startText(self, x, y):
        if self.textObject == None:
            self.textObject = self.canvas.beginText()
            self.newTextObject = True

    def drawText(self, x, y, txt):
        if self.textObject == None:
            self.startText(x, y)
        else:
            self.textObject.setTextOrigin(x, self._trY(y))
        #print(f"{txt}: {x} {y}")
        self.textObject.textOut(txt)

    def finish(self):
        if self.textObject != None:
            self.canvas.drawText(self.textObject)
            self.textObject = None

    def _trY(self, y):
        return self.page.pageLayout.height - y