import sys
import pymates.markdown
import pymates.units
from pymates.mainwindow import MainWindow
from pymates.parser import Parser
from pymates.scanner import Scanner
from pymates.evaluator import Evaluator
from pymates.treeify import treeify
from pymates.generator import generate
from pymates.lom import FontWeight, Alignment
from PySide6.QtWidgets import QApplication

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
    parser.addBuiltins(pymates.units)
    parser.addBuiltin("FontWeight", FontWeight)
    parser.parse()

    ev = Evaluator()
    ev.evaluate(parser.doc, parser.nspace)

    treeify(parser.doc)
    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Preview")
    app.setApplicationName("Preview")

    d = generate(parser.doc)

    mw = MainWindow()
    mw.setDocument(d)
    mw.show()
    sys.exit(app.exec_())

