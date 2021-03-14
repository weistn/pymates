from pymates.dom import DocumentNode, ParagNode, StyleNode, SpanNode, MathNode, mergeStyle
from pymates.lom import FontWeight, Alignment

def document():
    return DocumentNode(document)

def p(**style):
    return ParagNode(p, style=mergeStyle({"fontSize": 12}, style))

def h1(**style):
    return ParagNode(h1, style=mergeStyle({"fontSize": 32}, style))

def h2(**style):
    return ParagNode(h2, style=mergeStyle({"fontSize": 24}, style))

def h3(**style):
    return ParagNode(h3, style=mergeStyle({"fontSize": 20}, style))

def h4(**style):
    return ParagNode(h4, style=mergeStyle({"fontSize": 16}, style))

def code(**style):
    return ParagNode(code, style=mergeStyle({"fontFamily": "Courier"}, style))

def math(**style):
    return ParagNode(code, style=mergeStyle({}, style))

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

def color(col, child = None):
    return style(child, color=col)

def red(child = None):
    return color((255, 0, 0), child)

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

def inlineMath(child):
    return style(child, math=True)

def inlineCode(child):
    return style(child, code=True)

def fract(counter, denominator):
    return MathNode(fract, [counter, denominator])

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