import pymates.sizes
from functools import wraps
from enum import Enum

def mergeStyle(s1, s2):
    s = {}
    for k in s1:
        s[k] = s1[k]
    for k in s2:
        s[k] = s2[k]
    return s

def checkBool(key, val):
    if not isinstance(val, bool):
        raise BaseException(f"Argument {key} is not a boolean")

class Node:
    def __init__(self, func, children=None):
        self.func = func
        if children == None:
            self.children = []
        elif isinstance(children, tuple):
            self.children = list(children)
        else:
            self.children = children
        self.indent = 0
        self.className = None
        
    def append(self, *children):
        for c in children:
            self.children.append(c)

    def isContainer(self):
        return False

class DocumentNode(Node):
    def __init__(self, func):
        super(DocumentNode, self).__init__(func)
        self.pageSize = pymates.sizes.A4
        self.pageMargin = pymates.sizes.Margin(20, 20, 20, 20)

    def isContainer(self):
        return True

class ParagNode(Node):
    def __init__(self, func, style = None, children=None, config = None, parentContainer = None, isContainer = False):
        super(ParagNode, self).__init__(func, children)
        self.style = style
        self.config = config
        self.parentContainer = parentContainer
        self._isContainer = isContainer
        self.parent = None
        if style != None:
            for k in style:
                if k == "bold": checkBool(k, style[k])
                elif k == "italic": checkBool(k, style[k])
#                else: raise BaseException(f"Argument {k} is not a supported style option")

    def isContainer(self):
        return self._isContainer

class StyleNode(Node):
    def __init__(self, func, style, child = None):
        super(StyleNode, self).__init__(func)
        self.style = style
        if child != None:
            self.append(child)
        if style != None:
            for k in style:
                if k == "bold": checkBool(k, style[k])
                elif k == "italic": checkBool(k, style[k])
#                else: raise BaseException(f"Argument {k} is not a supported style option")

class SpanNode(Node):
    def __init__(self, func, children = None):
        super(SpanNode, self).__init__(func)
        if children != None:
            self.children = children

class MathNode(Node):
    def __init__(self, func, children):
        super(MathNode, self).__init__(func)
        self.children = children

class FunctionNodeMode(Enum):
    SectionOrInline = 1
    Inline = 2
    Section = 3

class FunctionNode(Node):
    def __init__(self, func, mode, args, kwargs):
        super(FunctionNode, self).__init__(func)
        self.mode = mode
        self.args = args
        self.kwargs = kwargs
        self.evaluateArgs = True

def section(className):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args == None:
                args = []
            else:
                args = list(args)
            fn = FunctionNode(func, FunctionNodeMode.Section, args, kwargs)
            fn.className = className
            return fn
        return wrapper
    return decorator

def inline(className):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args == None:
                args = []
            else:
                args = list(args)
            fn = FunctionNode(func, FunctionNodeMode.Inline, args, kwargs)
            fn.className = className
            return fn
        return wrapper
    return decorator