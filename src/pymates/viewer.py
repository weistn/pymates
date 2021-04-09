import sys
import os
import pymates.markdown
import pymates.sizes
import pymates.fonts
import pymates.qtbackend
import pymates.pdfbackend
from pymates.mainwindow import MainWindow
from pymates.parser import Parser
from pymates.scanner import Scanner
from pymates.evaluator import Evaluator
from pymates.treeify import treeify
from pymates.generator import generate
from pymates.fonts import loadFont
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong argument count")
        sys.exit(1)

    file = open(sys.argv[1])
    content = file.read()
    file.close()

    scanner = Scanner(content)
    parser = Parser(scanner)
    # Add builtins
    parser.addBuiltins(pymates.markdown)
    parser.addBuiltins(pymates.sizes)
    parser.parse()

    ev = Evaluator()
    for step in (None, "counters", "references"):
        ev.evaluate(parser.doc, parser.nspace, step)
        treeify(parser.doc)
    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Preview")
    app.setApplicationName("Preview")

    mw = MainWindow()

    pymates.pdfbackend.pdfInit()
    pymates.fonts.setFontMetricsBackend(pymates.pdfbackend)
    pymates.qtbackend.qtInit(mw)
    pymates.fonts.addFontBackend(pymates.qtbackend)
    # pymates.fonts.setFontMetricsBackend(pymates.qtbackend)


    fontPath = os.path.join(os.path.dirname(pymates.__file__), "fonts")
    loadFont(os.path.join(fontPath, "Lobster-Regular.ttf"), "Lobster", 400, False)
    loadFont(os.path.join(fontPath, "Roboto-Regular.ttf"), "Roboto", 400, False)
    loadFont(os.path.join(fontPath, "Roboto-Bold.ttf"), "Roboto", 700, False)

    d = generate(parser.doc)

    mw.setDocument(d)
    mw.show()
    sys.exit(app.exec_())

