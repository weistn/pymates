from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
import pymates.fonts

def pdfInit():
    pass

def pdfColor(color):
    color.pdfcolor = colors.Color(color.r/255, color.g/255, color.b/255)

def pdfFont(font):
    font.pdffont = pdfmetrics.getFont(font.registeredFont.name)

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
        print(f"Metrics {font.registeredFont.name} {font.size} {self.ascent} {self.descent} {0.2*font.size}")
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

def loadFont(regfont):
    registerFont(TTFont(regfont.name, regfont.file))

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
            self.textObject.setFont(font.registeredFont.name, font.size)
        else:
            self.canvas.setFont(font.registeredFont.name, font.size)

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

# Register PDF builtin fonts
pymates.fonts.registerBuiltinFont("Courier-BoldOblique", "Courier", 700, True)
pymates.fonts.registerBuiltinFont("Courier-Bold", "Courier", 700, False)
pymates.fonts.registerBuiltinFont("Courier-Oblique", "Courier", 400, True)
pymates.fonts.registerBuiltinFont("Courier", "Courier", 400, False)
pymates.fonts.registerBuiltinFont("Helvetica-BoldOblique", "Helvetica", 700, True)
pymates.fonts.registerBuiltinFont("Helvetica-Bold", "Helvetica", 700, False)
pymates.fonts.registerBuiltinFont("Helvetica-Oblique", "Helvetica", 400, True)
pymates.fonts.registerBuiltinFont("Helvetica", "Helvetica", 400, False)
pymates.fonts.registerBuiltinFont("Times-BoldItalic", "Times", 700, True)
pymates.fonts.registerBuiltinFont("Times-Bold", "Times", 700, False)
pymates.fonts.registerBuiltinFont("Times-Italic", "Times", 400, True)
pymates.fonts.registerBuiltinFont("Symbol", "Symbol", 400, False)
pymates.fonts.registerBuiltinFont("ZapfDingbats", "ZapfDingbats", 400, False)
