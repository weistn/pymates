from enum import Enum

class Token(Enum):
    # TokenEOF denotes the end of file.
    EoF                 = 0
    # TokenText denotes plain text
    Text                = 1
    # TokenSection denotes a tag
    Section             = 2
    BracketOpen = 5
    BracketClose = 6
    # TokenTableCell denotes text that represents a table cell
    TableCell           = 7
    # TokenTableRow denotes text that represents a table row
    TableRow            = 8
    # Text enclosed in backticks
    InlineCode = 9
    # Text enclosed in '$'
    InlineMath          = 10
    # Text enclosed in three backticks
    CodeSection         = 11
    # Text enclodes in '$$'
    MathSection         = 12
    # A section ending with ':' on the first line
    DefinitionSection   = 13
    Style = 14
    OrderedListSection         = 15
    UnorderedListSection = 16
    Function = 17
    FunctionSection = 18
    FunctionArg = 19

class ScannerMode(Enum):
    Normal          = 0
    # ModeNewTag means that the scanner is expecting a new tag. If it sees text or style or entities instead,
    # it assumes a new paragraph.
    NewTag          = 1
    Definition      = 2
    FunctionArgs    = 3

class TextMode(Enum):
    Normal      = 0
    Table       = 1

"""
ScannerError reports a lexicographic error,
which is either an illegal character or a malformed UTF-8 encoding.
"""
class ScannerError:
    """
    pos is of type ScannerRange.
    """
    def __init__(self, pos, text):
        self.pos = pos
        self.text = text

    def __str__(self):
        return self.text

"""
ScannerRange describes a position in the input markdown.
"""
class ScannerRange:
    def __init__(self, fromOffset, fromLine, fromLinePos, toOffset):
        self.fromOffset = fromOffset
        self.fromLine = fromLine
        self.fromLinePos = fromLinePos
        self.toOffset = toOffset

"""
Scanner splits markdown into tokens.
"""
class Scanner:
    def __init__(self, src):
        # source
        self.src = src
        self.mode = ScannerMode.NewTag
        self.textMode = TextMode.Normal

        # scanning state

        self.ch = chr(0)    # Current character
        self.offset = 0     # Offset of `ch` in `src`
        self.readOffset = 0 # Reading offset (position after current character)
        self.lineOffset = 0 # Start of the current line in `src`.
        self.lineCount = 1  # Line number of the line containing `ch`.
        self.indent = 0     # The indentation level of the last tag

        # Errors denotes the lexicographical errors detected while scanning.
        self.errors = []    # List of ScannerErrors

        # Beginning of file. Move to the first non-whitespace character
        self.next()
        self.skipWhitespace(True)

        self.peekToken = None
        self.peekText = ""
        self.peekRange = None

    """
    Read the next Unicode char into ch.
    self.ch < 0 means end-of-file.
    """
    def next(self):
        if self.readOffset < len(self.src):
            self.offset = self.readOffset
            if self.ch == '\n':
                self.lineOffset = self.offset
                self.lineCount += 1
            self.ch = self.src[self.readOffset]
            self.readOffset += 1
        else:
            self.offset = len(self.src)
            if self.ch == '\n':
                self.lineOffset = self.offset
                self.lineCount += 1
            self.ch = chr(0) # eof

    # A space following a function name is not a space if followed by an identifier letter, "("" or "{",
    # because without the space the next character would become part of the function call.
    def isFunctionNameDelimiter(self):
        if self.ch == ' ' or self.ch == '\t':
            if len(self.src) - self.readOffset >= 1:
                ch = self.src[self.readOffset]
                if ch == '{' or ch == '(' or ch == '_' or (self.ch >= 'a' and self.ch <= 'z') or (self.ch >= 'A' and self.ch <= 'Z') or (self.ch >= '0' and self.ch <= '9'):
                    return True
        return False

    def peekString(self, lookahead):
        if len(self.src) - self.readOffset < len(lookahead):
            return False
        return self.src[self.readOffset:self.readOffset+len(lookahead)] == lookahead

    def skipWhitespace(self, skipNewline = False):
        while self.ch == ' ' or self.ch == '\t' or (skipNewline and self.ch == '\n') or self.ch == '\r':
            self.next()

    def spacesTillNewline(self):
        for i in range (self.readOffset, len(self.src)):
            if self.src[i] == '\n':
                return True
            if self.src[i] != '\t' and self.src[i] != '\r' and self.src[i] != ' ':
                return False
        return True

    def skipPythonExpression(self):
        while ord(self.ch) != 0:
            if self.ch == ')' or self.ch == ',':
                return
            if self.ch == '(':
                self.next()
                self.skipPythonParanthesis()
            elif self.ch == '"':
                self.next()
                self.skipPythonString()
            else:
                self.next()

    def skipPythonParanthesis(self):
        while ord(self.ch) != 0:
            if self.ch == ')':
                self.next()
                return
            if self.ch == '(':
                self.next()
                self.skipPythonParanthesis()
            elif self.ch == '"':
                self.next()
                self.skipPythonString()
            else:
                self.next()

    def skipPythonString(self):
        while ord(self.ch) != 0:
            if self.ch == '"':
                self.next()
                return
            if self.ch == '\\':
                self.next()
            self.next()

    def skipCodeSection(self):
        i = 0
        while ord(self.ch) != 0:
            if self.ch == '`':
                self.next()
                i = i + 1
                if i == 3:
                    return self.offset - 3
            else:
                i = 0
                self.next()
        return self.offset

    """
    isStartOfLine returns true if the current character `self.ch`
    is the first non-space character in the line.
    """
    def isStartOfLine(self):
        if self.lineOffset == self.offset:
            return True
        for i in range(self.lineOffset, self.offset):
            ch = self.src[i]
            if ch != ' ' and ch != '\t' and ch != '\r':
                return False
        return True

    def isEnum(self):
        if self.ch < '0' or self.ch > '9':
            return False
        # Peak at the next characters
        for i in range(self.readOffset, len(self.src)):
            if self.src[i] == '.':
                return True
            if self.src[i] < '0' or self.src[i] > '9':
                return False
        return False

    def error(self, line, linepos, offset, text):
        self.errors.append(ScannerError(ScannerRange(offset, line, linepos, offset), text))

    def peek(self):
        if self.peekToken != None:
            return self.peekRange, self.peekToken, self.peekText
        self.peekRange, self.peekToken, self.peekText = self.scan()
        return self.peekRange, self.peekToken, self.peekText

    """
    scan() returns the next token.
    """
    def scan(self): # Returns (ScannerRange, Token, string)
        if self.peekToken != None:
            t = self.peekToken
            self.peekToken = None
            return self.peekRange, t, self.peekText
        r = ScannerRange(self.offset, self.lineCount, self.offset - self.lineOffset, self.offset)
        t, s = self._scan()
        r.toOffset = self.offset
        return r, t, s

    def _scan(self): # Returns (Token, String)
        while ord(self.ch) != 0:
            if self.ch == '/' and self.peekString('/'): # Comment
                self.next()
                self.next()
                while self.ch != 0 and self.ch != '\n':
                    self.next()
                continue
            elif self.ch == '>' or self.ch == '#':      # Section
                ch = self.ch
                # The '#' and '>' symbols are treated special when it is at the beginning of a line
                if self.mode == ScannerMode.NewTag:
                    self.indent = self.offset - self.lineOffset
                    self.mode = ScannerMode.Normal
                    self.textMode = TextMode.Normal
                    # Consume all hashes or '>'
                    start = self.offset
                    self.next()
                    while self.ch == ch:
                        self.next()
                    name = self.src[start:self.offset]
                    self.mode = ScannerMode.Normal
                    self.skipWhitespace(False)
                    return Token.Section, name
            elif self.ch == '-':                    # Unordered list
                if self.mode == ScannerMode.NewTag:
                    self.mode = ScannerMode.Normal
                    self.textMode = TextMode.Normal
                    indent = self.offset - self.lineOffset
                    start = self.offset
                    # Skip the '-' character
                    self.next()
                    txt = self.src[start:self.offset]
                    self.mode = ScannerMode.Normal
                    self.skipWhitespace(False)
                    self.indent = indent
                    return Token.UnorderedListSection, txt
            elif self.ch >= '1' and self.ch <= '9': # Ordered list
                if self.mode == ScannerMode.NewTag:
                    # Peak at the next characters
                    isEnum = True
                    for i in range(self.readOffset, len(self.src)):
                        if self.src[i] == '.':
                            break
                        if self.src[i] < '0' or self.src[i] > '9':
                            isEnum = False
                            break
                    if isEnum:
                        indent = self.offset - self.lineOffset
                        start = self.offset
                        # Skip the number
                        self.next()
                        while self.ch >= '0' and self.ch <= '9':
                            self.next()
                        # Skip '.'
                        self.next()
                        txt = self.src[start:self.offset]
                        self.mode = ScannerMode.Normal
                        self.textMode = TextMode.Normal
                        self.indent = indent
                        return Token.OrderedListSection, txt
            elif self.ch == ':':
                if self.mode == ScannerMode.Definition:
                    self.next()
                    self.skipWhitespace(True)
                    self.textMode = TextMode.Normal
                    self.mode = ScannerMode.Normal
                    return Token.DefinitionSection, ":"
            elif self.ch == '|':
                # Table mode or start of a new table?
                if self.mode == ScannerMode.Normal and (self.textMode == TextMode.Table or self.isStartOfLine()):
                    self.textMode = TextMode.Table
                    start = self.offset
                    # Skip all following `|` characters (required for multi-column cells)
                    self.next()
                    while self.ch == '|':
                        self.next()
                    end = self.offset
                    self.skipWhitespace(False)
                    # | followed by newline is the end of a row
                    if self.ch == '\n':
                        self.next()
                        self.skipWhitespace(False)
                        # An empty line terminates the table
                        if self.ch == '\n':
                            self.textMode = TextMode.Normal
                            self.skipWhitespace(True)
                            self.mode = ScannerMode.NewTag
                        return Token.TableRow, self.src[start:end]
                    return Token.TableCell, self.src[start:end]
            elif self.ch == '_':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    return Token.Style, "_"
            elif self.ch == '*':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    return Token.Style, "*"
            elif self.ch == '{':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    return Token.BracketOpen, "{"
            elif self.ch == '}':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    return Token.BracketClose, "}"
            elif self.ch == '\\':
                # Skip the backslash
                self.next()
                start = self.offset
                # Skip the identifier
                while (self.ch >= 'a' and self.ch <= 'z') or (self.ch >= 'A' and self.ch <= 'Z') or (self.ch >= '0' and self.ch <= '9'):
                    self.next()
                # There is an identifier?
                if start < self.offset:
                    # A function call
                    name = self.src[start:self.offset]
                    mode = self.mode
                    if self.ch == '(':
                        self.mode = ScannerMode.FunctionArgs
                    elif self.ch == '\n' or self.ch == '\t' or self.ch == '\r' or self.ch == ' ':
                        if self.isFunctionNameDelimiter():
                            self.next()
                        # else:
                        #    self.skipWhitespace(False)
                        self.mode = ScannerMode.Normal
                    elif self.ch == '{' or self.ch == '\\' or self.ch == '_' or selr.ch == '*':
                        self.mode = ScannerMode.Normal
                    else:
                        self.error(self.lineCount, self.lineOffset, self.offset, f"Unexpected character '{self.ch}'")
                        self.mode = ScannerMode.Normal
                    if mode == ScannerMode.NewTag:
                        return Token.FunctionSection, name
                    return Token.Function, name
            elif self.ch == '`':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    start = self.offset
                    txt = ""
                    # Code mode is terminated by a backtick. A newline does not terminate code mode.
                    while self.ch != '`' and ord(self.ch) != 0:
                        # If "\`" then the "`" is part of the text.
                        # Otherwise, do not treat "\" special
                        if self.ch == '\\':
                            self.next()
                            if self.ch == '`':
                                txt += self.src[start : self.offset-1]
                                start = self.offset
                                self.next()
                        self.next()
                    txt += self.src[start:self.offset]
                    if self.ch == '`':
                        self.next()
                    return Token.InlineCode, txt
                elif self.mode == ScannerMode.NewTag and self.peekString("``"):
                    self.next()
                    self.next()
                    self.next()
                    start = self.offset
                    end = self.skipCodeSection()
                    self.skipWhitespace(True)
                    return Token.CodeSection, self.src[start:end]
            elif self.ch == '$':
                if self.mode == ScannerMode.Normal:
                    self.next()
                    start = self.offset
                    txt = ""
                    # Math mode can only be terminated by "$". A newline does not terminate math mode.
                    while self.ch != '$' and ord(self.ch) != 0:
                        # If "\$" then the $ is part of the text.
                        # Otherwise, do not treat "\" special
                        if self.ch == '\\':
                            self.next()
                            if self.ch == '$':
                                txt += self.src[start : self.offset-1]
                                start = self.offset
                                self.next()
                        self.next()
                    txt += self.src[start:self.offset]
                    if self.ch == '$':
                        self.next()
                    return Token.InlineMath, txt
                elif self.mode == ScannerMode.NewTag and self.peekString("$"):
                    self.next()
                    self.next()
                    self.mode = ScannerMode.Normal
                    return Token.MathSection, "$$"
            elif self.ch == '(' or self.ch == ',':
                if self.mode == ScannerMode.FunctionArgs:
                    self.next()
                    start = self.offset
                    self.skipPythonExpression()
                    return Token.FunctionArg, self.src[start:self.offset]
            elif self.ch == ')':
                if self.mode == ScannerMode.FunctionArgs:
                    self.next()
                    self.mode = ScannerMode.Normal

            if self.mode == ScannerMode.NewTag:
                # A new tag is required. Since no other markup could be found, we assume it to be a paragraph
                self.mode = ScannerMode.Normal
                self.indent = self.offset - self.lineOffset
                return Token.Section, "#p"
            # Scan normal text
            start = self.offset
            end = self.offset
            while ord(self.ch) != 0:
                # New section?
                if (self.ch == '#' or self.ch == '|' or self.ch == '-' or self.ch == '>' or self.isEnum()) and self.isStartOfLine():
                    self.mode = ScannerMode.NewTag
                    break
                if self.ch == '`' and self.peekString("``") and self.isStartOfLine():
                    self.mode = ScannerMode.NewTag
                    break
                if self.ch == '$' and self.peekString("$") and self.isStartOfLine():
                    self.mode = ScannerMode.NewTag
                    break
                # Text markup?
                if self.ch == '\\' or self.ch == '{' or self.ch == '}' or self.ch == '~' or self.ch == '`' or self.ch == '$' or self.ch == '_' or self.ch == '*':
                    break
                # Comment?
                if self.ch == '/' and self.peekString("/"):
                    break
                # New table cell?
                if self.textMode == TextMode.Table and self.ch == '|':
                    break
                # A definition?
                if self.ch == ':' and self.spacesTillNewline():
                    # Return the text scanned until here
                    self.mode = ScannerMode.Definition
                    break
                if self.ch == '\\':
                    break
                # Break upon an empty line
                if self.ch == '\n':
                    self.next()
                    l = self.lineCount
                    self.skipWhitespace(True)
                    if self.lineCount > l:
                        self.mode = ScannerMode.NewTag
                        break
                else:
                    self.next()
                    end = self.offset
            if start == end:
                continue
            result = self.src[start:end]
            return Token.Text, result
        return Token.EoF, ""

if __name__ == '__main__':
    scanner = Scanner("""
    # Hello world
    // This is a comment

    Where are _we_ going
    these \\bold{days}?

    \\p(color=red,font="Arial") This is some _freaking_ text in a paragraph
    1. Doof
    2. Dumm

    - Headline 1
      - Sub 1
      - Sub 2
    - Headline 2    

    Quantum:
    Something like an `integer` with value $5*4$

    ```
    for i in range {
        a = i
    }
    ```

    $$
    Sum_i = 0
    $$
    """)
    print(scanner.src)
    while True:
        r, t, s = scanner.scan()
        print(f"TOKEN={t} {s}")
        if t == Token.EoF:
            break