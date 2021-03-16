from enum import Enum
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPageSize, QTransform
from PySide6.QtCore import Qt, QPointF, QRect

def ptToPx(pt, dpi):
    return pt/72*dpi

def pxToPt(px, dpi):
    return px*72/dpi

def mmToPt(mm):
    return mm * 2.8346456693

class Alignment(Enum):
    Left = 0
    Right = 1
    Justify = 2
    Center = 3

class FontWeight(Enum):
    Thin = QFont.Thin
    ExtraLight = QFont.ExtraLight
    Light = QFont.Light
    Normal = QFont.Normal
    Medium = QFont.Medium
    DemiBold = QFont.DemiBold
    Bold = QFont.Bold
    ExtraBold = QFont.ExtraBold
    Black = QFont.Black

fonts = {}
colors = {}
qpaintDevice = None
xdpi = 72
ydpi = 72

def setPaintDevice(paintDevice):
    global qpaintDevice
    qpaintDevice = paintDevice
    global xdpi
    xdpi = paintDevice.logicalDpiX()
    global ydpi
    ydpi = paintDevice.logicalDpiY()
    fonts.clear()

def font(family, size, weight =  FontWeight.Normal, italic = False, underline = False, strikeOut = False):
    name = f"{family}|{size}|{weight}|{italic}|{underline}|{strikeOut}"
    if name in fonts:
        return fonts[name]
    f = Font(family, size, weight, italic, underline, strikeOut)
    fonts[name] = f
    return f

def deriveFont(baseFont, style):
    if style == None:
        return baseFont
    baseStyle = {
        "fontFamily": baseFont.family,
        "fontSize": baseFont.size,
        "fontWeight": baseFont.weight,
        "italic": baseFont.italic,
        "underline": baseFont.underline,
        "strikeOut": baseFont.strikeOut
    }
    for key in baseStyle:
        if (key in style) and style[key] != None:
            baseStyle[key] = style[key] 
    return font(baseStyle["fontFamily"], baseStyle["fontSize"], baseStyle["fontWeight"], baseStyle["italic"], baseStyle["underline"], baseStyle["strikeOut"])    

def color(r, g ,b):
    name = f"{r},{g},{b}"
    if name in colors:
        return colors[name]
    c = Color(r, g, b)
    colors[name] = c
    return c

class Font:
    def __init__(self, family, size, weight =  FontWeight.Normal, italic = False, underline = False, strikeOut = False):
        self.family = family
        self.size = size
        self.weight = weight
        self.italic = italic
        self.underline = underline
        self.strikeOut = strikeOut

        self.qfont = QFont(family, size)
        if weight !=  FontWeight.Normal:
            self.qfont.setWeight(weight.value)
        if italic:
            self.qfont.setItalic(True)
        if underline:
            self.qfont.setUnderline(True)
        if strikeOut:
            self.qfont.setStrikeOut(True)
        self.qmetrics = QFontMetricsF(self.qfont, qpaintDevice)
        self.spaceAdvance = self.qmetrics.horizontalAdvanceChar(" ")
        self.ascent = self.qmetrics.ascent()
        self.descent = self.qmetrics.descent()
        self.leading = self.qmetrics.leading()

    def advance(self, str):
        return self.qmetrics.horizontalAdvance(str, -1)

class Color:
    def __init__(self, r, g, b):
        self.qcolor = QColor(r, g, b)

class Margin:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class Padding:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class Document:
    def __init__(self, pageSize, pageLayout, font, textColor = None):
        self.namedFlows = {}
        self.flows = []
        self.pageLayout = pageLayout
        self.pageSize = pageSize
        self.font = font
        if textColor == None:
            self.textColor = color(0, 0, 0)
        else:
            self.textColor = textColor
        self._flowIndex = 0

    def newOrderedFlow(self):
        flow = TextFlow(self, None)
        self.flows.append(flow)
        return flow

    def newNamedFlow(self, name):
        if name in self.flows:
            raise Exception(f"Flow of name {name} already exists")
        flow = TextFlow(self, name)
        self.namedFlows[name] = flow
        return flow

    def startLayout(self):
        self._flowIndex = 0
        if len(self.flows) != 0:
            self.flows[0].startLayout()

    def consumed(self):
        return self._flowIndex >= len(self.flows)

    def currentFlow(self):
        while True:
            if self._flowIndex >= len(self.flows):
                return None
            flow = self.flows[self._flowIndex]
            if not flow.consumed():
                return flow
            self._flowIndex += 1
            if self._flowIndex < len(self.flows):
                self.flows[self._flowIndex].startLayout()

class TextFlow:
    def __init__(self, doc, name):
        self.doc = doc
        self.name = name
        self.cursor = TextCursor(self)
        self.blocks = []
        self._blockIndex = 0
        self._pageLayout = None

    def pageLayout(self):
        if self._pageLayout == None:
            return self.doc.pageLayout
        return self._pageLayout

    def setPageLayout(self, pageLayout):
        self._pageLayout = pageLayout

    def startLayout(self):
        self._blockIndex = 0
        if len(self.blocks) > 0:
            self.blocks[0].startLayout()

    def consumed(self):
        return self._blockIndex >= len(self.blocks)

    def currentBlock(self):
        while True:
            if self._blockIndex >= len(self.blocks):
                return None
            b = self.blocks[self._blockIndex]
            if not b.consumed():
                return b
            self._blockIndex += 1
            if self._blockIndex < len(self.blocks):
                self.blocks[self._blockIndex].startLayout()

class TextBlock:
    def __init__(self, flow, align = Alignment.Left, font = None, textColor = None):
        self.flow = flow
        self.flow.blocks.append(self)
        self.align = align
        if font == None:
            self.font = flow.doc.font
        else:
            self.font = font
        if textColor == None:
            self.textColor = flow.doc.textColor
        else:
            self.textColor = textColor
        self.objects = []
        # Set when textline() is called
        self.width = -1
        self.height = -1
        self.objectIndex = 0
        self.saveObjectIndex = 0

    def isEmpty(self):
        return len(self.objects) == 0

    def startLayout(self):
        self.objectIndex = 0

    def consumed(self):
        return self.objectIndex == len(self.objects)

    def nextLine(self, width, nonEmpty = False):
        if self.objectIndex == len(self.objects):
            return None
        t = TextLine(self.objectIndex)
        t.save()
        while True:
            # End of block?
            if self.objectIndex == len(self.objects):
                t.endOfBlock = True
                if self.align == Alignment.Center:
                    t.translate((width - t.width) / 2, 0)
                elif self.align == Alignment.Right:
                    t.translate(width - t.width, 0)
                return t
            # Try the next text object
            obj = self.objects[self.objectIndex]
            self.objectIndex += 1
            # A space? Line could end here. Save the line state
            if obj.isSpace():
                t.save()
                self.saveObjectIndex = self.objectIndex
            # Add the text object to the line
            t.append(obj)
            # line is too long?
            if t.width > width:
                if nonEmpty and len(t.objects) == 1:
                    pass
                else:
                    # Restore the previous line state, but consume the space
                    t.restore()
                    self.objectIndex = self.saveObjectIndex
                if self.align == Alignment.Justify:
                    t.justify(width)
                elif self.align == Alignment.Center:
                    t.translate((width - t.width) / 2, 0)
                elif self.align == Alignment.Right:
                    t.translate(width - t.width, 0)
                return t

    def undoLine(self, line):
        self.objectIndex = min(self.objectIndex, line.objectIndex)

    def leading(self):
        return self.font.leading

class TextLine:
    def __init__(self, objectIndex):
        self.objectIndex = objectIndex
        self.objects = []
        self.width = 0
        self.ascent = 0
        self.descent = 0
        self.wordCount = 0
        self.endOfBlock = False
        self.x = 0
        self.y = 0

    def height(self):
        return self.ascent + self.descent

    def save(self):
        self._saveObjects = len(self.objects)
        self._saveWidth = self.width
        self._saveAscent = self.ascent
        self._saveDescent = self.descent
        self._saveWordCount = self.wordCount

    def restore(self):
        self.objects = self.objects[:self._saveObjects]
        self.width = self._saveWidth
        self.ascent = self._saveAscent
        self.descent = self._saveDescent
        self.wordCount = self._saveWordCount

    def justify(self, width):
        if self.endOfBlock:
            return
        spaces = 0
        for obj in self.objects:
            if obj.isSpace():
                spaces += obj.advance
        addSpace = (width - self.width) / spaces
        addX = 0
        for obj in self.objects:
            obj.x += addX
            if obj.isSpace():
                addX += addSpace * obj.advance

    def translate(self, x, y):
        for obj in self.objects:
            obj.x += x
            obj.y += y

    def draw(self, painter, x, y):
        for obj in self.objects:
            obj.draw(painter, x, y + self.ascent)
            
    def append(self, obj):
        obj.y = 0
        obj.x = self.width
        self.objects.append(obj)
        self.width += obj.advance
        self.ascent = max(self.ascent, obj.ascent)
        self.descent = max(self.descent, obj.descent)

    def textBoxes(self):
        boxes = []
        for obj in self.objects:
            if isinstance(obj, TextBox):
                boxes.append(obj)
        return boxes

class TextObject:
    def __init__(self, block):
        self.block = block
        block.objects.append(self)
        self.y = 0
        self.startOfWord = True
        # Set by a derived class
        self.ascent = -1
        self.descent = -1
        self.advance = -1
        # Set when the object is added to a TextLine
        self.x = -1

    def draw(self, painter, x, baseline):
        pass

    def isSpace(self):
        return False

class TextBox(TextObject):
    def __init__(self, block, subFlow):
        super(TextBox, self).__init__(block)
        self.subFlow = subFlow
        self.ascent = 0
        self.descent = 0
        self.advance = 0
        self.marginPoints = Margin(0, 0, 0, 0)

class TextString(TextObject):
    def __init__(self, block, str, font = None, textColor = None):
        super(TextString, self).__init__(block)
        self.str = str
        if font == None:
            self.font = block.font
        else:
            self.font = font
        if textColor == None:
            self.textColor = block.textColor
        else:
            self.textColor = textColor
        # Compute the dimensions
        self.ascent = self.font.ascent
        self.descent = self.font.descent
        self.advance = self.font.advance(self.str)

    def draw(self, painter, x, baseline):
        # print(f"Draw str {self.str} at {x}+{self.x}, {baseline}")
        painter.setPen(self.textColor.qcolor)
        painter.setFont(self.font.qfont)
        painter.drawText(QPointF(x + self.x, baseline + self.y), self.str)

    def isSpace(self):
        return self.str == " "

class TextCursor:
    def __init__(self, flow):
        self.flow = flow
        self.block = None
        self.font = None
        self.textColor = None
        self.formatStack = []

    def startBlock(self, align = Alignment.Left, font = None, textColor = None):
        self.block = TextBlock(self.flow, align, font, textColor)
        self.font = None
        self.textColor = None
        if len(self.formatStack) != 0:
            self.formatStack = []
        return self.block

    def blockFormat(self, align = None, font = None, textColor = None):
        if align != None:
            self.block.align = align
        if textColor != None:
            self.block.textColor = textColor
        if font != None:
            self.block.font = font

    def text(self, str):
        if self.block == None:
            raise Exception("No block")
        if str.startswith(" "):
            if not self.block.isEmpty():
                TextString(self.block, " ", self.font, self.textColor)
        words = str.split()
        for i in range(0, len(words)):
            if i != 0:
                TextString(self.block, " ", self.font, self.textColor)
            TextString(self.block, words[i], self.font, self.textColor)
        if str.endswith(" "):
            TextString(self.block, " ", self.font, self.textColor)

    def startFormat(self, font = None, textColor = None):
        self.formatStack.append({"textColor": self.textColor, "font": self.font})
        if font != None:
            self.font = font
        if textColor != None:
            self.textColor = textColor

    def endFormat(self):
        if len(self.formatStack) == 0:
            raise Exception("No matching startFormat")
        f = self.formatStack.pop()
        self.font = f["font"]
        self.textColor = f["textColor"]

    def textBox(self, name):
        subFlow = self.flow.doc.newNamedFlow(name)
        box = TextBox(self.block, subFlow)
        return box

    def currentFont(self):
        if self.font != None:
            return self.font
        if self.block != None:
            return self.block.font
        return self.flow.doc.font

class PageSize:
    def __init__(self, widthPoints, heightPoints):
        self.widthPoints = widthPoints
        self.heightPoints = heightPoints
        self.marginPoints = Margin(mmToPt(10), mmToPt(10), mmToPt(10), mmToPt(10))

    def fromId(id):
        qpagesize = QPageSize(id)
        qsize = qpagesize.sizePoints()
        return PageSize(qsize.width(), qsize.height())

class AbstractPageLayout:
    def __init__(self):
        pass
    
    def nextPageLayout(self):
        return self

class DefaultPageLayout(AbstractPageLayout):
    def __init__(self):
        super(DefaultPageLayout, self).__init__()

    def fillPage(self, doc, floatBoxes):
        page = Page(doc)
        ps = page.doc.pageSize
        w = ps.widthPoints
        w -= ps.marginPoints.left + ps.marginPoints.right
        h = ps.heightPoints
        h -= ps.marginPoints.top + ps.marginPoints.bottom
        self.box = PageBox(page, ps.marginPoints.left, ps.marginPoints.top, w, h)
        floatBoxes = self.box.fill(doc.currentFlow(), floatBoxes)
        return (page, floatBoxes)

class Page:
    def __init__(self, doc):
        self.doc = doc
        self.boxes = []

    def draw(self, painter):
        for box in self.boxes:
            box.draw(painter)

class PageBox:
    def __init__(self, pageOrPageBox, xPoints, yPoints, widthPoints, maxHeightPoints):
        if isinstance(pageOrPageBox, PageBox):
            self.parentBox = pageOrPageBox
            self.page = self.parentBox.page
            self.parentBox.childBoxes.append(self)
        else:
            self.parentBox = None
            self.page = pageOrPageBox
            self.page.boxes.append(self)
        self.xPoints = xPoints
        self.yPoints = yPoints
        self.widthPoints = widthPoints
        self.heightPoints = 0
        self.maxHeightPoints = maxHeightPoints
        self.lines = []
        self.childBoxes = []

    def removeChildBox(self, pageBox):
        self.childBoxes.remove(pageBox)
        
    def fill(self, flow, textBoxes):
        if flow == None:
            return
        leading = 0
        yPixels = 0
        yPixelsMax = ptToPx(self.maxHeightPoints, ydpi)

        # Fit as many of the pending TextBoxes as possible 
        while len(textBoxes) > 0:
            textBox = textBoxes[0]
            yPoints = pxToPt(yPixels, ydpi)
            xPoints = textBox.marginPoints.left
            boxWidthPoints = self.widthPoints - textBox.marginPoints.left - textBox.marginPoints.right
            p = PageBox(self, xPoints, yPoints, boxWidthPoints, self.maxHeightPoints - yPoints)
            print(f"B {boxWidthPoints}")
            textBox.subFlow.startLayout()
            missingBoxes = p.fill(textBox.subFlow, [])
            if len(missingBoxes) != 0:
                print("TextBox in overfull TextBox")
            if not textBox.subFlow.consumed():
                self.removeChildBox(p)
                break
            textBoxes = textBoxes[1:]
            yPixels += leading + ptToPx(p.heightPoints + textBox.marginPoints.bottom, ydpi)

        # Fit lines of text and TextBoxes
        done = False
        while not done:
            b = flow.currentBlock()
            if b == None:
                break
            while not b.consumed():
                line = b.nextLine(ptToPx(self.widthPoints, xdpi))
                h = line.height() + leading
                if yPixels + h > yPixelsMax:
                    self.heightPoints = pxToPt(yPixels, ydpi)
                    b.undoLine(line)
                    done = True
                    break
                print("L")
                line.x = 0
                line.y = yPixels
                yPixels += h
                self.lines.append(line)
                leading = b.leading()
                # Layout all text boxes associated with the line
                for textBox in line.textBoxes():
                    yPoints = pxToPt(yPixels + leading, ydpi)
                    xPoints = textBox.marginPoints.left
                    boxWidthPoints = self.widthPoints - textBox.marginPoints.left - textBox.marginPoints.right
                    p = PageBox(self, xPoints, yPoints, boxWidthPoints, self.maxHeightPoints - yPoints)
                    print(f"B {boxWidthPoints}")
                    textBox.subFlow.startLayout()
                    missingBoxes = p.fill(textBox.subFlow, [])
                    if len(missingBoxes) != 0:
                        print("TextBox in overfull TextBox")
                    if not textBox.subFlow.consumed():
                        textBoxes.append(textBox)
                        self.removeChildBox(p)
                    else:
                        yPixels += leading + ptToPx(p.heightPoints + textBox.marginPoints.bottom, ydpi)
        self.heightPoints = pxToPt(yPixels, ydpi)
        return textBoxes

    def draw(self, painter):
        x = ptToPx(self.xAbsPoints(), xdpi)
        y = ptToPx(self.yAbsPoints(), ydpi)
        for line in self.lines:
            line.draw(painter, x + line.x, y + line.y)
        for childBox in self.childBoxes:
            childBox.draw(painter)

    def xAbsPoints(self):
        if self.parentBox == None:
            return self.xPoints
        return self.parentBox.xAbsPoints() + self.xPoints

    def yAbsPoints(self):
        if self.parentBox == None:
            return self.yPoints
        return self.parentBox.yAbsPoints() + self.yPoints

class Layouter:
    def __init__(self, doc):
        self.doc = doc
        self.pages = []
        self.widgetMarginPx = 10
        self.widgetHeightPx = self.widgetMarginPx
        self.widgetWidthPx = ptToPx(self.doc.pageSize.widthPoints, xdpi) + 2 + 2*self.widgetMarginPx

    def layout(self):
        self.doc.startLayout()
        floatBoxes = []
        while True:
            print("F")
            f = self.doc.currentFlow()
            if f == None:
                return
            l = f.pageLayout()
            while True:
                print("P")
                p, floatBoxes = l.fillPage(self.doc, floatBoxes)
                self.pages.append(p)
                h = ptToPx(self.doc.pageSize.heightPoints, ydpi)
                self.widgetHeightPx += h + 2 + self.widgetMarginPx
                if f.consumed():
                    break
                l = l.nextPageLayout()

    def draw(self, painter, paged):
        # Used for drawing on a widget
        yOffsetPx = 0
        # Draw all pages
        for page in self.pages:
            if not paged:
                # Draw a border around the page
                yOffsetPx += self.widgetMarginPx
                painter.setWorldTransform(QTransform())
                w = ptToPx(self.doc.pageSize.widthPoints, xdpi)
                h = ptToPx(self.doc.pageSize.heightPoints, ydpi)
                painter.fillRect(QRect(self.widgetMarginPx, yOffsetPx, w + 2, h + 2), color(255, 255, 255).qcolor)
                painter.setPen(QColor(0xb2, 0xb2, 0xb2))
                painter.drawRect(self.widgetMarginPx, yOffsetPx, w + 2, h + 2)
                painter.translate(self.widgetMarginPx + 1, yOffsetPx + 1)
                yOffsetPx += h + 2
            page.draw(painter)
            if paged:
                painter.device().newPage()
