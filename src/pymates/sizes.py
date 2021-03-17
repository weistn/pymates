inch = 72.0
cm = inch / 2.54
mm = cm * 0.1
pica = 12.0

_W, _H = (21*cm, 29.7*cm)

A6 = (_W*.5, _H*.5)
A5 = (_H*.5, _W)
A4 = (_W, _H)
A3 = (_H, _W*2)
A2 = (_W*2, _H*2)
A1 = (_H*2, _W*4)
A0 = (_W*4, _H*4)

Letter = (8.5*inch, 11*inch)
Legal = (8.5*inch, 14*inch)

_BW, _BH = (25*cm, 35.3*cm)

B6 = (_BW*.5, _BH*.5)
B5 = (_BH*.5, _BW)
B4 = (_BW, _BH)
B3 = (_BH*2, _BW)
B2 = (_BW*2, _BH*2)
B1 = (_BH*4, _BW*2)
B0 = (_BW*4, _BH*4)

def landscape(pagesize):
    """Use this to get page orientation right"""
    a, b = pagesize
    if a < b:
        return (b, a)
    else:
        return (a, b)

def portrait(pagesize):
    """Use this to get page orientation right"""
    a, b = pagesize
    if a >= b:
        return (b, a)
    else:
        return (a, b)
        
class Margin:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class Padding:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

_pymates_all_ = ["inch", "cm", "mm", "pica", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "B0", "B1", "B2", "B3", "B4", "B5", "B6", "landscape", "portrait"]