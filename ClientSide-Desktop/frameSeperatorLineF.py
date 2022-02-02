import PyQt5.QtWidgets as qtw

def frameSeperatorLineF(self, x, y, w, h, color="black"):
    hs = qtw.QFrame(self)
    hs.setStyleSheet(f"border: 1px solid {color}; background-color: {color};")
    hs.setFixedSize(w, h)
    hs.move(x, y)
    return hs
