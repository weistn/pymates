from pymates.lom import PageLayout, PageLayoutBox, Document, Alignment, color
from pymates.sizes import Padding, Margin, Rect
from pymates.fonts import font
from pymates import dom, markdown

generators = {}

def register(func, gen):
    generators[func] = gen

def generatePageLayout(docNode, style):
    if "margin" in style:
        margin = Margin.fromStyle(style["margin"])
    else:
        margin = Margin.fromStyle(docNode.style["margin"])
    pl = PageLayout(docNode.style["pageSize"], margin)
    if "pageBox" in style:
        if isinstance(style["pageBox"], list):
            for pageBox in style["pageBox"]:
                PageLayoutBox(pl, pageBox["flow"], Rect.fromStyle(pageBox["rect"]))
        else:
            pageBox = style["pageBox"]
            PageLayoutBox(pl, pageBox["flow"], Rect.fromStyle(pageBox["rect"]))
    return pl

def ensureCursor(doc, cursor):
    if cursor != None:
        return cursor
    flow = doc.newFlow()
    cursor = flow.cursor
    return cursor

def generate(docNode):
    pl = generatePageLayout(docNode, docNode.style)
    f = font("Helvetica", 12)
    doc = Document(pl, f)
    # flow = doc.newFlow()
    # cursor = flow.cursor
    # genNode(docNode, doc, cursor)
    genNode(docNode, doc, None)

    return doc

def genNodes(nodes, doc, cursor):
    if nodes != None:
        for n in nodes:
            cursor = genNode(n, doc, cursor)
    return cursor

def genNode(node, doc, cursor):
    if isinstance(node, str):
        return genText(node, doc, cursor)
    else:
        # print(node.func)
        return generators[node.func](node, doc, cursor)

def genDocument(node, doc, cursor):
    return genNodes(node.children, doc, cursor)

def genParag(node, doc, cursor):
    returnCursor = None
    if "flow" in node.style:
        flowName = node.style["flow"]
        flowScope = node.style["flowScope"] if "flowScope" in node.style else "document"
        if flowName == "":
            flow = doc.newFlow()
            if "pageLayout" in node.style:
                pl = generatePageLayout(node.document(), node.style)
                flow.setPageLayout(pl)
            cursor = flow.cursor
        else:
            cursor = ensureCursor(doc, cursor)
            returnCursor = cursor
            flow = (cursor.flow.doc if flowScope == "document" else cursor.flow).newNamedFlow(flowName)
            cursor = flow.cursor
    else:
        cursor = ensureCursor(doc, cursor)
    # ("genParag")
    align = node.style["align"] if "align" in node.style else Alignment.Left
    textFont = deriveFont(doc.font, node.style)
    textColor = None
    if "color" in node.style:
        s = node.style["color"]
        textColor = color(s[0], s[1], s[2])
    cursor.startBlock(font=textFont, textColor=textColor, align=align)
    if node.children != None:
        for n in node.children:
            cursor = genNode(n, doc, cursor)
    if returnCursor != None:
        return returnCursor
    return cursor

def genStyle(node, doc, cursor):
    # print("genStyle")
    textFont = deriveFont(cursor.currentFont(), node.style)
    textColor = None
    if "color" in node.style:
        s = node.style["color"]
        textColor = color(s[0], s[1], s[2])
    cursor.startFormat(font=textFont, textColor=textColor)
    align = node.style["align"] if "align" in node.style else None
    padding = derivePadding(cursor.block.padding, node.style["padding"]) if "padding" in node.style else None
    margin = deriveMargin(cursor.block.margin, node.style["margin"]) if "margin" in node.style else None
    if align != None or padding != None or margin != None:
        cursor.blockFormat(align=align, margin=margin, padding=padding)
    if len(node.children) != 0:
        genNodes(node.children, doc, cursor)
        cursor.endFormat()
    # print("endStyle")
    return cursor

def genSpan(node, doc, cursor):
    return genNodes(node.children, doc, cursor)

def genText(node, doc, cursor):
    # print(f"genText {node}")
    cursor.text(node)
    return cursor

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

def deriveMargin(baseMargin, margin):
    return Margin(
        margin["left"] if margin["left"] != None else baseMargin.left,
        margin["top"] if margin["top"] != None else baseMargin.top,
        margin["right"] if margin["right"] != None else baseMargin.right,
        margin["bottom"] if margin["bottom"] != None else baseMargin.bottom,        
    )

def derivePadding(basePadding, padding):
    return Padding(
        padding["left"] if padding["left"] != None else basePadding.left,
        padding["top"] if padding["top"] != None else basePadding.top,
        padding["right"] if padding["right"] != None else basePadding.right,
        padding["bottom"] if padding["bottom"] != None else basePadding.bottom,        
    )

register(markdown.document, genDocument)

register(markdown.h1, genParag)
register(markdown.h2, genParag)
register(markdown.h3, genParag)
register(markdown.h4, genParag)
register(markdown.p, genParag)

register(markdown.span, genSpan)

register(markdown.style, genStyle)
register(markdown.bold, genStyle)
register(markdown.italic, genStyle)
