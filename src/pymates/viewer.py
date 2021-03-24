import sys
import pymates.markdown
import pymates.sizes
from pymates.mainwindow import MainWindow
from pymates.parser import Parser
from pymates.scanner import Scanner
from pymates.evaluator import Evaluator
from pymates.treeify import treeify
from pymates.generator import generate
from pymates.lom import FontWeight, Alignment
from PySide6.QtWidgets import QApplication

from pymates.lom import font
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
    parser.addBuiltin("FontWeight", FontWeight)
    parser.parse()

    ev = Evaluator()
    for step in (None, "counters", "references"):
        ev.evaluate(parser.doc, parser.nspace, step)
        treeify(parser.doc)
    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Preview")
    app.setApplicationName("Preview")

    i = QFontDatabase.addApplicationFont("/Users/weis/Projects/pymates/Lobster-Regular.ttf")
    print(i)
    print(QFontDatabase.applicationFontFamilies(i))
    i = QFontDatabase.addApplicationFont("/Users/weis/Projects/pymates/Roboto-Regular.ttf")
    print(i)
    print(QFontDatabase.applicationFontFamilies(i))
    # print(f"------------------------> {font('Lobster', 12).advance('Hello World')}")

    mw = MainWindow()

    d = generate(parser.doc)

    mw.setDocument(d)
    mw.show()
    sys.exit(app.exec_())

