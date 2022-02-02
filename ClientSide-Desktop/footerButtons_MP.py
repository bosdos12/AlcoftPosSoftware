import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import sys
sys.path.append(r"C:\Users\Led-Com.CH\Desktop\AdaksPythonLibrary")
from AdaksPyQt5Tools import PercentageValue as adakPV

def footerButtons_MP(self, x, y, f, a, t):
    productsButton = qtw.QPushButton(t, self, clicked=f)
    productsButton.setFixedSize(adakPV(12, "w", a), adakPV(6, "h", a))
    productsButton.setFont(qtg.QFont("Arial", adakPV(1.5, "w", a)))
    productsButton.move(adakPV(x, "w", a), adakPV(y, "h", a))
    return productsButton