backend = None
fontBackends = []

def setFontMetricsBackend(b):
    global backend
    backend = b
    addFontBackend(b)

def addFontBackend(b):
    global fontBackends
    fontBackends.append(b)

class Font:
    def __init__(self, family, size, weight = 400, italic = False, underline = False, strikeOut = False):
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

# Font factory that cashes Font objects.
def font(family, size, weight = 400, italic = False, underline = False, strikeOut = False):
    name = f"{family}|{size}|{weight}|{italic}|{underline}|{strikeOut}"
    if name in fonts:
        return fonts[name]
    f = Font(family, size, weight, italic, underline, strikeOut)
    fonts[name] = f
    return f

def loadFont(file, family, weight = 400, italic = False):
    for b in fontBackends:
        b.loadFont(file, family, weight, italic)
