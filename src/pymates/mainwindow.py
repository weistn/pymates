import sys
from PySide6.QtGui import QPalette, QPainter, QTransform, QColor
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QMainWindow, QScrollArea, QApplication, QWidget
from pymates.qtbackend import hPtToPx, wPtToPx, qtInit
import pymates.fonts
import pymates.qtbackend

class PageArea(QWidget):
    def __init__(self):
        super(PageArea, self).__init__()
        self.layouter = None
        self.widgetHeightPx = 0
        self.widgetWidthPx = 0
        self.widgetMarginPx = 10

    def setLayouter(self, layouter):
        self.layouter = layouter
        self.widgetHeightPx = self.widgetMarginPx
        self.widgetWidthPx = wPtToPx(self.layouter.pages[0].pageLayout.width) + 2 + 2*self.widgetMarginPx
        for page in self.layouter.pages:
            h = hPtToPx(page.pageLayout.height)
            self.widgetHeightPx += h + 2 + self.widgetMarginPx

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qpainter):
        # Used for drawing on a widget
        yOffsetPx = 0
        # Draw all pages
        for page in self.layouter.pages:
            # Draw a border around the page
            yOffsetPx += self.widgetMarginPx
            qpainter.setWorldTransform(QTransform())
            w = wPtToPx(page.pageLayout.width)
            h = hPtToPx(page.pageLayout.height)
            qpainter.fillRect(QRect(self.widgetMarginPx, yOffsetPx, w + 2, h + 2), QColor(255, 255, 255))
            qpainter.setPen(QColor(0xb2, 0xb2, 0xb2))
            qpainter.drawRect(self.widgetMarginPx, yOffsetPx, w + 2, h + 2)
            qpainter.translate(self.widgetMarginPx + 1, yOffsetPx + 1)
            yOffsetPx += h + 2
            painter = pymates.qtbackend.qtPainter(qpainter)
            page.draw(painter)
            painter.finish()

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
        qtInit(self.pageArea)
        pymates.fonts.setBackend(pymates.qtbackend)

    def setDocument(self, doc):
        layouter = Layouter(doc)
        layouter.layout()
        self.pageArea.setLayouter(layouter)
        self.pageArea.setGeometry(0, 0, self.pageArea.widgetHeightPx, self.pageArea.widgetWidthPx)
        self.pageArea.setFixedHeight(self.pageArea.widgetHeightPx)
        self.pageArea.setFixedWidth(self.pageArea.widgetWidthPx)

from pymates.lom import PageLayout, Document, Layouter, color
from pymates.fonts import font
from pymates.sizes import Margin, Alignment, A4

if __name__ == '__main__':
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
        
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Preview")
    app.setApplicationName("Preview")
    mw = MainWindow()

    pl = PageLayout(A4, Margin(20, 20, 20, 20))
    # ps = PageSize(mmToPt(100), mmToPt(50))
    f = font("Helvetica", 12)
    doc = Document(pl, f)
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
