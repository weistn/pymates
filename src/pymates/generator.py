from pymates.lom import DefaultPageLayout, PageSize, Document, font, deriveFont, Alignment, color
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
        # i = 0
        # for i in range(0, len(node.children)):
        #     if not isinstance(node.children[i], dom.StyleNode):
        #         break
        #     genBlockStyle(node.children[i])
        for n in node.children:
            genNode(n, doc, cursor)

# def genBlockStyle(node, doc, cursor):
#    print("genBlockStyle")
#    textFont = deriveFont(cursor.currentFont(), node.style)
#    textColor = None
#    align = node.style["align"] if "align" in node.style else None
#    if "color" in node.style:
#        s = node.style["color"]
#        textColor = color(s[0], s[1], s[2])
#    cursor.blockFormat(font=textFont, textColor=textColor, align=align)
#    print("endStyle")

def genStyle(node, doc, cursor):
    print("genStyle")
    align = node.style["align"] if "align" in node.style else None
    textFont = deriveFont(cursor.currentFont(), node.style)
    textColor = None
    if "color" in node.style:
        s = node.style["color"]
        textColor = color(s[0], s[1], s[2])
    cursor.startFormat(font=textFont, textColor=textColor)
    if align != None:
        cursor.blockFormat(align=align)
    if len(node.children) != 0:
        genNodes(node.children, doc, cursor)
        cursor.endFormat()
    print("endStyle")

def genSpan(node, doc, cursor):
    genNodes(node.children, doc, cursor)

def genText(node, doc, cursor):
    print(f"genText {node}")
    cursor.text(node)

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
