from pymates.dom import DocumentNode, ParagNode, StyleNode, SpanNode, MathNode, inline
from pymates.lom import FontWeight, Alignment

def document():
    return DocumentNode(document)

def pagesize(size):
    return style(pagesize=size)

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
    return style(child, fontWeight=FontWeight.Bold)

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

def inlineMath(child):
    return style(child, math=True)

def inlineCode(child):
    return style(child, color=(0xd0, 0x10, 0x40), fontFamily="Courier")

@inline("references")
def ref(node, name):
    return "Chapter: " + name

# def fract(counter, denominator):
#    return MathNode(fract, [counter, denominator])

def span(*children):
    return SpanNode(span, list(children))

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