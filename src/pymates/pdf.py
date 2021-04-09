import sys
import pymates.markdown
import pymates.sizes
import pymates.pdfbackend
import pymates.fonts
from pymates.parser import Parser
from pymates.scanner import Scanner
from pymates.evaluator import Evaluator
from pymates.treeify import treeify
from pymates.generator import generate
from pymates.lom import Layouter
from reportlab.pdfgen import canvas

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong argument count")
        sys.exit(1)

    pymates.pdfbackend.pdfInit()
    pymates.fonts.setFontMetricsBackend(pymates.pdfbackend)

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
    ev.evaluate(parser.doc, parser.nspace)

    treeify(parser.doc)
    
    doc = generate(parser.doc)

    layouter = Layouter(doc)
    layouter.layout()

    c = canvas.Canvas("out.pdf")

    for page in layouter.pages:
        painter = pymates.pdfbackend.pdfPainter(page, c)
        page.draw(painter)
        painter.finish()
        c.showPage()

    c.save()