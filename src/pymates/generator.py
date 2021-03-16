from pymates.lom import DefaultPageLayout, PageSize, Document, font, Alignment, color
from pymates.units import Padding, Margin
from pymates import dom, markdown
from PySide6.QtGui import QPageSize

generators = {}

def register(func, gen):
    generators[func] = gen

def generate(docNode):
    pl = DefaultPageLayout()
    ps = PageSize.fromId(QPageSize.A4)
    f = font("Helvetica", 12)
    doc = Document(ps, pl, f)
    flow = doc.newOrderedFlow()
    cursor = flow.cursor

    genNode(docNode, doc, cursor)

    return doc

def genNodes(nodes, doc, cursor):
    if nodes != None:
        for n in nodes:
            genNode(n, doc, cursor)

def genNode(node, doc, cursor):
    if isinstance(node, str):
        genText(node, doc, cursor)
    else:
        print(node.func)
        generators[node.func](node, doc, cursor)

def genDocument(node, doc, cursor):
    genNodes(node.children, doc, cursor)

def genParag(node, doc, cursor):
    print("genParag")
    align = node.style["align"] if "align" in node.style else Alignment.Left
    textFont = deriveFont(doc.font, node.style)
    textColor = None
    if "color" in node.style:
        s = node.style["color"]
        textColor = color(s[0], s[1], s[2])
    cursor.startBlock(font=textFont, textColor=textColor, align=align)
    if node.children != None:
        for n in node.children:
            genNode(n, doc, cursor)

def genStyle(node, doc, cursor):
    print("genStyle")
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
    print("endStyle")

def genSpan(node, doc, cursor):
    genNodes(node.children, doc, cursor)

def genText(node, doc, cursor):
    print(f"genText {node}")
    cursor.text(node)

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
