import inspect
from pymates.markdown import document, inlineCode, inlineMath, bold, italic, math, code, h1, h2, h3, h4, p, span
from pymates.scanner import Token, Scanner
from pymates.dom import FunctionNode, SpanNode

def isKeywordArgument(code):
    for i in range(0, len(code)):
        ch = code[i]
        if ch == '=':
            return code[:i], code[i+1:]
        if (ch < 'a' or ch > 'z') and (ch < 'A' or ch > 'Z') and (i == 0 or ch < '0' or ch > '9') and ch != '_':
            return False
    return False

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.doc = document()
        self.nspace = {}

    def addBuiltin(self, name, func):
        self.nspace[name] = func

    def addBuiltins(self, mod):
        for name, val in inspect.getmembers(mod, lambda o: inspect.isfunction(o)):
            # print(f"Importing {name}")
            self.addBuiltin(name, val)

    def lookupBuiltin(self, name, default):
        if name in self.nspace:
            return self.nspace[name]
        return default

    def parse(self):
        self.parseSection(self.doc)

    def parseSection(self, section):
        while True:
            r, tok, txt = self.scanner.scan()
            if tok == Token.EoF:
                break
            elif tok == Token.Text:
                print(f"STR: '{txt}'")
                section.append(txt)
            elif tok == Token.OrderedListSection:
                newSection = self.lookupBuiltin("ol", ol)()
                newSection.indent = self.scanner.indent
                section.append(newSection)
            elif tok == Token.UnorderedListSection:
                newSection = self.lookupBuiltin("ul", ul)()
                newSection.indent = self.scanner.indent
                section.append(newSection)            
            elif tok == Token.Section:
                if txt == "#p":
                    newSection = self.lookupBuiltin("p", p)()
                elif txt == "#":
                    newSection = self.lookupBuiltin("h1", h1)()
                elif txt == "##":
                    newSection = self.lookupBuiltin("h2", h2)()
                elif txt == "###":
                    newSection = self.lookupBuiltin("h3", h2)()
                elif txt == "####":
                    newSection = self.lookupBuiltin("h4", h2)()
                else:
                    raise BaseException("Oooops")
                newSection.indent = self.scanner.indent
                section.append(newSection)
            elif tok == Token.BracketOpen:
                newSpan = self.lookupBuiltin("span", span)()
                section.append(self.parseSpan(newSpan, Token.BracketClose, "}"))
            elif tok == Token.InlineCode:
                newSpan = self.lookupBuiltin("inlineCode", inlineCode)(txt)
                section.append(newSpan)
            elif tok == Token.InlineMath:
                newSpan = self.lookupBuiltin("inlineMath", inlineMath)(txt)
                section.append(newSpan)
            elif tok == Token.MathSection:
                newSection = self.lookupBuiltin("math", math)()
                newSection.indent = self.scanner.indent
                section.append(newSection)
            elif tok == Token.CodeSection:
                newSection = self.lookupBuiltin("code", code)()
                newSection.indent = self.scanner.indent
                section.append(newSection)
            elif tok == Token.TableRow:
                pass # TODO
            elif tok == Token.DefinitionSection:
                pass # TODO
            elif tok == Token.Style:
                if txt == "*":
                    newSpan = self.lookupBuiltin("bold", bold)(None)
                    section.append(self.parseSpan(newSpan, Token.Style, "*"))
                elif txt == "_":
                    newSpan = self.lookupBuiltin("italic", italic)(None)
                    section.append(self.parseSpan(newSpan, Token.Style, "_"))
                else:
                    raise BaseException("Ooops")
            elif tok == Token.Function or tok == Token.FunctionSection:
                func = self.lookupBuiltin(txt, None)
                if func == None:
                    raise BaseException(f"Unknown function {txt}")
                section.append(self.parseFunction(func, tok == Token.FunctionSection))
            else:
                raise BaseException(f"Unexpected token {txt}")

    def parseFunction(self, func, possibleSection):
        print(f"Parse function {func.__name__}")
        node = FunctionNode(func, possibleSection, [], {})
        node.indent = self.scanner.indent
        print(node)
        r, tok, txt = self.scanner.peek()
        while tok == Token.FunctionArg:    
            self.scanner.scan()
            txt = txt.rstrip().lstrip()
            kw = isKeywordArgument(txt)
            if kw == False:
                node.args.append(txt)
            else:
                node.kwargs[kw[0]] = kw[1]
            r, tok, txt = self.scanner.peek()
        while tok == Token.BracketOpen:
            self.scanner.scan()
            newSpan = self.parseSpan(SpanNode(span), Token.BracketClose, "}")
            node.append(newSpan)
            r, tok, txt = self.scanner.peek()
        return node

    def parseSpan(self, span, endToken, endText):
        while True:
            r, tok, txt = self.scanner.scan()
            if tok == endToken and txt == endText:
                return span
            elif tok == Token.EoF:
                raise BaseException(f"Unexpected end of file. Missing '{endText}'")
            elif tok == Token.Text:
                span.append(txt)
            elif tok == Token.BracketOpen:
                newSpan = self.lookupBuiltin("span", span)()
                span.append(self.parseSpan(newSpan))
            elif tok == Token.InlineCode:
                newSpan = self.lookupBuiltin("inlineCode", inlineCode)(txt)
                span.append(newSpan)
            elif tok == Token.InlineMath:
                newSpan = self.lookupBuiltin("inlineMath", inlineMath)(txt)
                span.append(newSpan)
            elif tok == Token.Style:
                if txt == "*":
                    newSpan = self.lookupBuiltin("bold", bold)(None)
                    span.append(self.parseSpan(newSpan, Token.Style, "*"))
                elif txt == "_":
                    newSpan = self.lookupBuiltin("italic", italic)(None)
                    span.append(self.parseSpan(newSpan, Token.Style, "_"))
                else:
                    raise BaseException("Ooops")
            elif tok == Token.Function:
                func = self.lookupBuiltin(txt, None)
                if func == None:
                    raise BaseException(f"Unknown function {txt}")
                span.append(self.parseFunction(func, False))
            else:
                raise BaseException(f"Unexpected token {txt} in span")

if __name__ == '__main__':
    scanner = Scanner("""
    # Hello world

    Here comes the _text_.
    """)
    parser = Parser(scanner)
    parser.parse()