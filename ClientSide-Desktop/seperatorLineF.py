import PyQt5.QtWidgets as qtw
import sys
sys.path.append(r"C:\Users\Led-Com.CH\Desktop\AdaksPythonLibrary")
from AdaksPyQt5Tools import PercentageValue as adakPV

def seperatorLineF(self, x, y, w, h, app):
    hs = qtw.QFrame(self)
    hs.setStyleSheet("border: 1px solid black; background-color: black;")
    hs.setFixedSize(int(adakPV(w, "w", app)), adakPV(h, "h", app)/2)
    hs.move(adakPV(x, "w", app), adakPV(y, "h", app))
    return hs