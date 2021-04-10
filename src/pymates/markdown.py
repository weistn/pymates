import os
import pymates.fonts
from pymates.dom import DocumentNode, ParagNode, StyleNode, SpanNode, MathNode, inline
from pymates.lom import Alignment

def document():
    return DocumentNode(document)

def pagesize(size):
    return style(pageSize=size)

@inline("counters")
def counter(node, counterFmt, refFmt, *names):
    section = node.section()
    if section == None:
        raise BaseException("Parent of counter must be a section") 
    doc = node.document()
    c = []
    for i in range(0, len(names) - 1):
        c.append(doc.counter(names[i]))
    c.append(doc.incCounter(names[len(names) - 1]))
    s = counterFmt.format(*c)
    section.setReferenceName(refFmt.format(*c))
    return s

@inline("counters")
def label(node, name):
    section = node.section()
    if section == None:
        raise BaseException("Parent of label must be a section") 
    node.document().setLabel(name, section)

@inline("references")
def ref(node, name):
    section = node.document().label(name)
    return section.referenceName()

def p(*children):
    return ParagNode(p, style={"fontSize": 12}, children=children)

def h1(*children):
    return ParagNode(h1, style={"fontSize": 32}, children=children)

def h2(*children):
    return ParagNode(h2, style={"fontSize": 24}, children=children)

def h3(*children):
    return ParagNode(h3, style={"fontSize": 20}, children=children)

def h4(*children):
    return ParagNode(h4, style={"fontSize": 16}, children=children)

def chapter(*children):
    return h1(counter("Chapter {}: ", "Chapter {}", "Level1"), *children)

def subchapter(*children):
    return h2(counter("Section {}.{}: ", "Section {}.{}", "Level1", "Level2"), *children)

def code(*children):
    return ParagNode(code, style={"fontFamily": "Courier"}, children=children)

def math(*children):
    return ParagNode(code, style={}, children=children)

# def deck():
#     return ParagNode(deck)

# def slide(tmpl = None, **kwargs):
#    return ParagNode(slide, style=kwargs, config={"tmpl": tmpl}, parent=deck)

def style(child = None, **styleInfo):
    return StyleNode(style, child=child, style=styleInfo)

def bold(child = None):
    return style(child, fontWeight=700)

def italic(child = None):
    return style(child, italic=True)

def emph(child = None):
    return bold(italic(child))

def underline(child = None):
    return style(child, underline=True)

def strike(child = None):
    return style(child, strikeOut=True)

def tt(child = None):
    return style(child, fontFamily="Courier")

def color(red, green, blue, child = None):
    return style(child, color=(red, green, blue))

def red(child = None):
    return color(255, 0, 0, child)

def align(a, child = None):
    return style(child, align=a)

def left(child = None):
    return align(Alignment.Left, child)

def right(child = None):
    return align(Alignment.Right, child)

def center(child = None):
    return align(Alignment.Center, child)

def justify(child = None):
    return align(Alignment.Justify, child)

def margin(left=None, top=None, right=None, bottom=None, child=None):
    return style(child, margin={"left": left, "top": top, "right": right, "bottom": bottom})

def padding(left=None, top=None, right=None, bottom=None, child=None):
    return style(child, padding={"left": left, "top": top, "right": right, "bottom": bottom})

def inlineMath(child):
    return style(child, math=True)

def inlineCode(child):
    return style(child, color=(0xd0, 0x10, 0x40), fontFamily="Courier")

# def fract(counter, denominator):
#    return MathNode(fract, [counter, denominator])

def span(*children):
    return SpanNode(span, list(children))

def pageLayout(repeat = False):
    return style(None, pageLayout={"repeat": repeat})

def nextPageLayout(repeat = False):
    return style(None, nextPageLayout={"repeat": repeat})

def pageBox(flow, rect):
    return style(None, pageBox={"rect": rect, "flow": flow})

def pageBreak():
    return style(child, pageBreak=True)

# scope is "document" or "flow"
def flow(name = "", scope = "document"):
    if scope != "document" and scope != "flow":
        raise BaseException(f"Unknown flow scope '{scope}'")
    if name == "" and scope == "flow":
        raise BaseException("A flow with 'scope=flow' must have a name")
    return style(flow = name, flowScope = scope)

def py(value):
    return value

@inline("counters")
def setvar(node, name, value):
    node.document().setVariable(name, value)
    return None

@inline("references")
def var(node, name):
    return node.document().variable(name)

# -----------------------------------------

_lobster = False

def lobster(child = None):
    global _lobster
    if not _lobster:
        fontPath = os.path.join(os.path.dirname(pymates.__file__), "fonts")
        pymates.fonts.registerFont(os.path.join(fontPath, "Lobster-Regular.ttf"), "Lobster", 400, False)
        _lobster = True

    return style(child, fontFamily = "Lobster")

_roboto = False

def roboto(child = None):
    global _roboto
    if not _roboto:
        fontPath = os.path.join(os.path.dirname(pymates.__file__), "fonts")
        pymates.fonts.registerFont(os.path.join(fontPath, "Roboto-Regular.ttf"), "Roboto", 400, False)
        pymates.fonts.registerFont(os.path.join(fontPath, "Roboto-Bold.ttf"), "Roboto", 700, False)
        _roboto = True

    return style(child, fontFamily = "Roboto")

# -----------------------------------------

from pymates.sizes import mm, A4, landscape

def slidedeck():
    return pagesize(landscape(A4))

def slide(*children):
    return ParagNode(slide, style={}, parentContainer=document, isContainer=True, children=(
        flow(), pageLayout(), margin(20*mm, 50*mm, 20*mm, 20*mm),
        pageBox(flow="title", rect=(20*mm, 15*mm, 250*mm, 30*mm)),
        pageBox(flow="footer", rect=(20*mm, 190*mm, 250*mm, 10*mm)),
        *children
    ))

def title(*children):
    return ParagNode(title, style={"fontSize": 32}, parentContainer=slide, children=(
        flow("title", "flow"), *children
    ))

def footer(localPage = False, *children):
    return ParagNode(footer, style={"fontSize": 12}, parentContainer=slide, children=(
        flow("footer", "flow" if localPage else "document"), *children
    ))

# -----------------------------------------

if __name__ == '__main__':
    deck().append(
        slide(tmpl="black", bold=True).append(
            "Hello ", bold(span(italic("World"), "!!!"))
        )
    )

# ```
# \deck
# \slide(tmpl="white")
# Hello \bold{\italic{World}!!!}
# ```