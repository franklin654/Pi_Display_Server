import sys
from PySide6.QtWidgets import QApplication
from home_display import HomeDisp

app = QApplication(sys.argv)
disp = HomeDisp(None)
disp.showMaximized()
app.exec()
