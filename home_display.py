from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QVBoxLayout
from BServer import BServer


class HomeDisp(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = QLabel()
        # pixmap = QPixmap("")
        # self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.setText("Hello Testing")
        self.window_layout = QVBoxLayout(self)
        self.window_layout.addWidget(self.label)
        self.server = BServer(self)
        self.server.start_server()
