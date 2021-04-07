from pymates.sizes import FontWeight

backend = None

def setBackend(b):
    global backend
    backend = b

class Font:
    def __init__(self, family, size, weight =  FontWeight.Normal, italic = False, underline = False, strikeOut = False):
        self.family = family
        self.size = size
        self.weight = weight
        self.italic = italic
        self.underline = underline
        self.strikeOut = strikeOut
        self.fontmetrics = backend.nativeFontMetrics(self)

    def advance(self, str):
        return self.fontmetrics.horizontalAdvance(str, -1)

fonts = {}

def font(family, size, weight = FontWeight.Normal, italic = False, underline = False, strikeOut = False):
    name = f"{family}|{size}|{weight}|{italic}|{underline}|{strikeOut}"
    if name in fonts:
        return fonts[name]
    f = Font(family, size, weight, italic, underline, strikeOut)
    fonts[name] = f
    return f
