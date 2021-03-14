import sys
from PySide6.QtGui import QPalette, QPainter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QScrollArea, QApplication, QWidget
from pymates.lom import setPaintDevice

class PageArea(QWidget):
    def __init__(self):
        super(PageArea, self).__init__()
        self.pageArea = None

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.layouter.draw(qp, False)
        qp.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Preview")
        self.setGeometry(300, 300, 600, 270)
        # fileMenu = mw.menuBar().addMenu("&File")
        # fileMenu.addAction("Close")
        self.scroll = QScrollArea()
        self.scroll.setBackgroundRole(QPalette.Mid)
        self.scroll.setAlignment(Qt.AlignHCenter or Qt.AlignTop)
        self.pageArea = PageArea()
        self.scroll.setWidget(self.pageArea)
        self.setCentralWidget(self.scroll)
        setPaintDevice(self.pageArea)

    def setDocument(self, doc):
        layouter = Layouter(doc)
        layouter.layout()
        self.pageArea.layouter = layouter
        self.pageArea.setGeometry(0, 0, layouter.widgetHeightPx, layouter.widgetWidthPx)
        self.pageArea.setFixedHeight(layouter.widgetHeightPx)
        self.pageArea.setFixedWidth(layouter.widgetWidthPx)

from PySide6.QtGui import QPageSize
from pymates.lom import DefaultPageLayout, PageSize, Document, Margin, Layouter, Alignment, font, color

if __name__ == '__main__':
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
        
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Preview")
    app.setApplicationName("Preview")
    mw = MainWindow()

    pl = DefaultPageLayout()
    ps = PageSize.fromId(QPageSize.A4)
    # ps = PageSize(mmToPt(100), mmToPt(50))
    f = font("Helvetica", 12)
    doc = Document(ps, pl, f)
    flow = doc.newOrderedFlow()
    cursor = flow.cursor

    b = cursor.startBlock(align = Alignment.Justify)
    cursor.text("Here comes some text followed by a box. ")
    
    box = cursor.textBox("MyBox")
    box.marginPoints = Margin(3, 0, 3, 3)
    cursor2 = box.subFlow.cursor
    cursor2.startBlock(textColor=color(50, 200, 50))
    cursor2.text("Humble text is shown inside the nice box.")
    cursor2.startBlock(textColor=color(50, 200, 50))
    cursor2.text("One")
    cursor2.startBlock(textColor=color(50, 200, 50))
    cursor2.text("Two")
    cursor2.startBlock(textColor=color(50, 200, 50))
    cursor2.text("Three")
    cursor2.startBlock(textColor=color(50, 200, 50))
    cursor2.text("Four")

    cursor.text("Hello cruel world. This is an ugly place to rest. I do not know what this text is all about, but it is a very long text. ")
    cursor.startFormat(textColor = color(255, 0, 0), font = font("Helvetica", 20))
    cursor.text("And now everything in red.")
    cursor.endFormat()
    cursor.text(" More in black. This text is very long and we want to see how things are flowing.")

    mw.setDocument(doc)
    mw.show()
    sys.exit(app.exec_())
