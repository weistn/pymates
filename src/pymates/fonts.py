_backend = None
_fontBackends = []

def setFontMetricsBackend(b):
    global _backend
    _backend = b
    addFontBackend(b)

def addFontBackend(b):
    global _fontBackends
    _fontBackends.append(b)

class Font:
    def __init__(self, family, size, weight = 400, italic = False, underline = False, strikeOut = False):
        self.family = family
        self.size = size
        self.weight = weight
        self.italic = italic
        self.underline = underline
        self.strikeOut = strikeOut
        self.registeredFont = _matchFont(family, weight, italic)
        _loadFont(self.registeredFont)
        self.fontmetrics = _backend.nativeFontMetrics(self)

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

_registeredFonts = []

class RegisteredFont:
    def __init__(self, file, name, family, weight, italic):
        self.file = file
        if name == None or name == "":
            self.name = f"{family}_{weight}{italic}"
        else:
            self.name = name
        self.family = family
        self.weight = weight
        self.italic = italic

def registerFont(file, family, weight, italic):
    _registeredFonts.append(RegisteredFont(file, None, family, weight, italic))

def registerBuiltinFont(name, family, weight, italic):
    _registeredFonts.append(RegisteredFont(None, name, family, weight, italic))

def _matchFont(family, weight, italic):
    # Find exact match
    for f in _registeredFonts:
        if f.family == family and f.weight == weight and f.italic == italic:
            return f
    # Search for nearest weight match
    bestSmaller = None
    bestSmallerDist = 1000
    bestBigger = None
    bestBiggerDist = 1000
    for f in _registeredFonts:
        if f.family == family and f.italic == italic:
            w = f.weight
            if w > weight and (w - weight) < bestBiggerDist:
                bestBigger = f
                bestBiggerDist = (w - weight)
            elif w < weight and (weight - w) < bestSmallerDist:
                bestSmaller = f
                bestSmallerDist = (weight - w)
    if bestSmaller == None and bestBigger == None and italic:
        # Try again, now ignoring italic
        return _matchFont(family, weight, False)
    # Find a good weight match (if at least one match exists)
    if bestSmaller != None or bestBigger != None:
        if weight <= 500:
            if bestSmaller:
                return bestSmaller
            else:
                return bestBigger
        if bestBigger:
            return bestBigger
        else:
            return bestSmaller
    # Use Helvetica as fallback
    return _matchFont("Helvetica", weight, italic)

def _loadFont(regfont):
    # Builtin font?
    if regfont.file == None:
        return
    for b in _fontBackends:
        b.loadFont(regfont)
