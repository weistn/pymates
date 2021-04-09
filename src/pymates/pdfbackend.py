from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

def pdfInit():
    pass

def pdfColor(color):
    color.pdfcolor = colors.Color(color.r/255, color.g/255, color.b/255)

def pdfFont(font):
    font.pdfname = pdfSearchFont(font.family, font.weight, font.italic)
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

# The ´name´ is only a suggestion.
# The function returns the name that the font backend uses for this font.
def loadFont(file, name):
    registerFont(TTFont(name, file))
    return name

pdfFonts = []

def pdfRegisterFont(file, name, family, weight, italic):
    pdfFonts.append({
        "file": file,
        "family": family,
        "name": name,
        "weight": weight,
        "italic": italic
    })

def pdfSearchFont(family, weight, italic):
    # Find exact match
    for f in pdfFonts:
        if f["family"] == family and f["weight"] == weight and f["italic"] == italic:
            return f["name"]
    print("!!!!!!!!!!! NO GOOD MATCH", family, weight, italic)
    # Search for nearest weight match
    bestSmaller = None
    bestSmallerDist = 1000
    bestBigger = None
    bestBiggerDist = 1000
    for f in pdfFonts:
        if f["family"] == family and f["italic"] == italic:
            w = f["weight"]
            if w > weight and (w - weight) < bestBiggerDist:
                bestBigger = f.name
                bestBiggerDist = (w - weight)
            elif w < weight and (weight - w) < bestSmallerDist:
                bestSmaller = f.name
                bestSmallerDist = (weight - w)
    if bestSmaller == None and bestBigger == None and italic:
        # Try again, now ignoring italic
        return pdfSearchFont(family, weight, False)
    # Find a good weight match (if at least one match exists)
    if bestSmaller != None or bestBigger != None:
        if weight <= 500:
            if bestSmaller:
                return bestSmaller
            else:
                return bestBigger
        if bestBigger:
            return bestBigger
        else:
            return bestSmaller
    # Use Helvetica as fallback
    return pdfSearchFont("Helvetica", weight, italic)

def loadFont(file, family, weight = 400, italic = False):
    # Font already loaded?
    for f in pdfFonts:
        if f["file"] == file:
            return
    name = f"{family}_{weight}{italic}"
    registerFont(TTFont(name, file))
    print("********* Register", file, name, family, weight, italic)
    pdfRegisterFont(file, name, family, weight, italic)

# Register PDF builtin fonts
pdfRegisterFont(None, "Courier-BoldOblique", "Courier", 700, True)
pdfRegisterFont(None, "Courier-Bold", "Courier", 700, False)
pdfRegisterFont(None, "Courier-Oblique", "Courier", 400, True)
pdfRegisterFont(None, "Courier", "Courier", 400, False)
pdfRegisterFont(None, "Helvetica-BoldOblique", "Helvetica", 700, True)
pdfRegisterFont(None, "Helvetica-Bold", "Helvetica", 700, False)
pdfRegisterFont(None, "Helvetica-Oblique", "Helvetica", 400, True)
pdfRegisterFont(None, "Helvetica", "Helvetica", 400, False)
pdfRegisterFont(None, "Times-BoldItalic", "Times", 700, True)
pdfRegisterFont(None, "Times-Bold", "Times", 700, False)
pdfRegisterFont(None, "Times-Italic", "Times", 400, True)
pdfRegisterFont(None, "Symbol", "Symbol", 400, False)
pdfRegisterFont(None, "ZapfDingbats", "ZapfDingbats", 400, False)

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