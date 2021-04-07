from pymates.sizes import Margin, Padding, Alignment
from pymates.fonts import Font

#def ptToPx(pt, dpi):
#    return pt/72*dpi

#def pxToPt(px, dpi):
#    return px*72/dpi

#def mmToPt(mm):
#    return mm * 2.8346456693

colors = {}

def color(r, g ,b):
    name = f"{r},{g},{b}"
    if name in colors:
        return colors[name]
    c = Color(r, g, b)
    colors[name] = c
    return c

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Document:
    def __init__(self, pageLayout, font, textColor = None):
        self.flows = []
        self.pageLayout = pageLayout
        self.font = font
        if textColor == None:
            self.textColor = color(0, 0, 0)
        else:
            self.textColor = textColor
        self._flowIndex = 0
        self.namedFlows = {}

    def newFlow(self):
        flow = TextFlow(self, None)
        self.flows.append(flow)
        return flow

    def newNamedFlow(self, name):
        if name in self.namedFlows:
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

    def lookupFlow(self, flowName):
        if flowName in self.namedFlows:
            return self.namedFlows[flowName]
        return None
        
class TextFlow:
    def __init__(self, docOrFlow, name):
        if isinstance(docOrFlow, Document):
            self.doc = docOrFlow
            self.parentFlow = None
        elif isinstance(docOrFlow, TextFlow):
            self.doc = docOrFlow.doc
            self.pageFlow = docOrFlow
        else:
            raise BaseException("Parent of a TextFlow must be the Document or another TextFlow")
        self.name = name
        self.cursor = TextCursor(self)
        self.blocks = []
        self.namedFlows = {}
        self._blockIndex = 0
        self._pageLayout = None

    def newNamedFlow(self, name):
        if name in self.namedFlows:
            raise Exception(f"Flow of name {name} already exists")
        flow = TextFlow(self, name)
        self.namedFlows[name] = flow
        return flow

    def lookupFlow(self, flowName):
        if flowName in self.namedFlows:
            return self.namedFlows[flowName]
        return None

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
    def __init__(self, flow, align = Alignment.Left, font = None, textColor = None, margin = None, padding = None):
        self.flow = flow
        self.flow.blocks.append(self)
        self.align = align
        self.margin = Margin(0, 0, 0, 0) if margin == None else margin
        self.padding = Padding(0, 0, 0, 0) if padding == None else padding
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
        return self.font.fontmetrics.leading

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
        painter.startText(x, y + self.ascent)
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
    def __init__(self, block, flow):
        super(TextBox, self).__init__(block)
        self.flow = flow
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
        self.ascent = self.font.fontmetrics.ascent
        self.descent = self.font.fontmetrics.descent
        self.advance = self.font.fontmetrics.advance(self.str)

    def draw(self, painter, x, baseline):
        # print(f"Draw str {self.str} at {x}+{self.x}, {baseline}")
        painter.setPen(self.textColor)
        painter.setFont(self.font)
        painter.drawText(x + self.x, baseline + self.y, self.str)

    def isSpace(self):
        return self.str == " "

class TextCursor:
    def __init__(self, flow):
        self.flow = flow
        self.block = None
        self.font = None
        self.textColor = None
        self._endsWithSpace = False
        self.formatStack = []

    def startBlock(self, align = Alignment.Left, font = None, textColor = None, padding=None, margin=None):
        self.block = TextBlock(self.flow, align, font, textColor, padding, margin)
        self.font = None
        self.textColor = None
        if len(self.formatStack) != 0:
            self.formatStack = []
        self._endsWithSpace = False
        return self.block

    def blockFormat(self, align = None, font = None, textColor = None, padding=None, margin=None):
        if align != None:
            self.block.align = align
        if textColor != None:
            self.block.textColor = textColor
        if font != None:
            self.block.font = font
        if padding != None:
            self.block.padding = padding
        if margin != None:
            self.block.margin = margin

    def text(self, str):
        if self.block == None:
            raise Exception("No block")
        if str.startswith(" "):
            if not self._endsWithSpace and not self.block.isEmpty():
                TextString(self.block, " ", self.font, self.textColor)
        words = str.split()
        for i in range(0, len(words)):
            if i != 0:
                TextString(self.block, " ", self.font, self.textColor)
            TextString(self.block, words[i], self.font, self.textColor)
        if len(words) != 0 and str.endswith(" "):
            TextString(self.block, " ", self.font, self.textColor)
            self._endsWithSpace = True
        else:
            self._endsWithSpace = False

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
        self._endsWithSpace = False
        flow = self.flow.newNamedFlow(name)
        box = TextBox(self.block, flow)
        return box

    def currentFont(self):
        if self.font != None:
            return self.font
        if self.block != None:
            return self.block.font
        return self.flow.doc.font

class AbstractPageLayout:
    def __init__(self, pageSize):
        self.pageSize = pageSize
        self.width = self.pageSize[0]
        self.height = self.pageSize[1]

    def nextPageLayout(self):
        return self

class PageLayout(AbstractPageLayout):
    def __init__(self, pageSize, margin):
        super(PageLayout, self).__init__(pageSize)
        self.margin = margin
        self.layoutBoxes = []

    def lookupFlow(self, flow, flowName):
        f = flow.lookupFlow(flowName)
        if f != None:
            return f
        return flow.doc.lookupFlow(flowName)

    def fillPage(self, doc, floatBoxes):
        # Create a new page
        page = Page(self, doc)
        # Create a box on the page which is determined by page size and margins
        w = self.width
        w -= self.margin.left + self.margin.right
        h = self.height
        h -= self.margin.top + self.margin.bottom
        self.box = PageBox(page, self.margin.left, self.margin.top, w, h)
        flow = doc.currentFlow()
        floatBoxes = self.box.fill(flow, floatBoxes)
        #
        for layoutBox in self.layoutBoxes:
            namedFlow = self.lookupFlow(flow, layoutBox.flowName)
            if namedFlow == None:
                print(f"Unknown flow {layoutBox.flowName}")
                continue
            namedFlow.startLayout()
            box = PageBox(page, layoutBox.rect.x, layoutBox.rect.y, layoutBox.rect.width, layoutBox.rect.height)
            box.fill(namedFlow, [])
        return (page, floatBoxes)

class PageLayoutBox:
    def __init__(self, pageLayout, flowName, rect):
        self.pageLayout = pageLayout
        self.rect = rect
        self.flowName = flowName
        pageLayout.layoutBoxes.append(self)

class Page:
    def __init__(self, pageLayout, doc):
        self.pageLayout = pageLayout
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
        self.heightPoints = 0

        # Fit as many of the pending TextBoxes as possible 
        while len(textBoxes) > 0:
            textBox = textBoxes[0]
            yPoints = self.heightPoints
            xPoints = textBox.marginPoints.left
            boxWidthPoints = self.widthPoints - textBox.marginPoints.left - textBox.marginPoints.right
            p = PageBox(self, xPoints, yPoints, boxWidthPoints, self.maxHeightPoints - yPoints)
            print(f"B {boxWidthPoints}")
            textBox.flow.startLayout()
            missingBoxes = p.fill(textBox.flow, [])
            if len(missingBoxes) != 0:
                print("TextBox in overfull TextBox")
            if not textBox.flow.consumed():
                self.removeChildBox(p)
                break
            textBoxes = textBoxes[1:]
            self.heightPoints += leading + p.heightPoints + textBox.marginPoints.bottom

        # Fit lines of text and TextBoxes
        done = False
        while not done:
            b = flow.currentBlock()
            if b == None:
                break
            leading = b.leading()
            while not b.consumed():
                line = b.nextLine(self.widthPoints)
                h = line.height() + leading
                if self.heightPoints + h > self.maxHeightPoints:
                    b.undoLine(line)
                    done = True
                    break
                print("L")
                line.x = 0
                line.y = self.heightPoints
                self.heightPoints += h
                self.lines.append(line)
                # leading = b.leading()
                # Layout all text boxes associated with the line
                for textBox in line.textBoxes():
                    yPoints = self.heightPoints + leading
                    xPoints = textBox.marginPoints.left
                    boxWidthPoints = self.widthPoints - textBox.marginPoints.left - textBox.marginPoints.right
                    p = PageBox(self, xPoints, yPoints, boxWidthPoints, self.maxHeightPoints - yPoints)
                    print(f"B {boxWidthPoints}")
                    textBox.flow.startLayout()
                    missingBoxes = p.fill(textBox.flow, [])
                    if len(missingBoxes) != 0:
                        print("TextBox in overfull TextBox")
                    if not textBox.flow.consumed():
                        textBoxes.append(textBox)
                        self.removeChildBox(p)
                    else:
                        self.heightPoints += leading + p.heightPoints + textBox.marginPoints.bottom            
        return textBoxes

    def draw(self, painter):
        x = self.xAbsPoints()
        y = self.yAbsPoints()
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

    def layout(self):
        self.doc.startLayout()
        floatBoxes = []
        # Iterate over all flows
        while True:
            print("F")
            flow = self.doc.currentFlow()
            if flow == None:
                return
            # Choose the page layout for the flow
            pageLayout = flow.pageLayout()
            while True:
                # Create pages until the flow is consumed
                print("P")
                page, floatBoxes = pageLayout.fillPage(self.doc, floatBoxes)
                self.pages.append(page)
                if flow.consumed():
                    break
                pageLayout = pageLayout.nextPageLayout()
