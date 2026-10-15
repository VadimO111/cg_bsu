import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false"

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QSlider, QSpinBox,
    QPushButton, QColorDialog, QGroupBox, QGridLayout, QVBoxLayout,
    QHBoxLayout, QFrame,
)

from color_math import (
    rgb_to_cmyk, cmyk_to_rgb,
    rgb_to_hsv, hsv_to_rgb,
)


STYLE = """
QMainWindow, QWidget { background: #1e1e2e; color: #e0e0f0; }
QGroupBox {
    border: 1px solid #3a3a52; border-radius: 8px;
    margin-top: 14px; padding: 12px; font-weight: bold; color: #7aa2f7;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QLabel { color: #e0e0f0; }
QLabel#dim { color: #9090a8; }
QLabel#hex { color: #7aa2f7; font-family: Consolas; font-size: 15px; font-weight: bold; }
QSlider::groove:horizontal {
    height: 6px; background: #3a3a52; border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #7aa2f7; width: 14px; margin: -5px 0; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #9bb8ff; }
QSpinBox {
    background: #313145; color: #e0e0f0;
    border: 1px solid #3a3a52; border-radius: 4px;
    padding: 2px 6px; min-width: 48px;
}
QPushButton {
    background: #313145; color: #e0e0f0;
    border: 1px solid #3a3a52; border-radius: 6px;
    padding: 8px 14px;
}
QPushButton:hover { background: #454560; }
QPushButton#accent {
    background: #7aa2f7; color: #1e1e2e;
    border: none; font-weight: bold;
}
QPushButton#accent:hover { background: #9bb8ff; }
"""


class ColorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Models: RGB / CMYK / HSV")
        self.resize(860, 560)

        self.updating = False
        self.vars = {}
        self.sliders = {}

        self.r, self.g, self.b = 122, 162, 247

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(10)

        title = QLabel("Предпросмотр")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        left.addWidget(title)

        dim = QLabel("Текущий цвет")
        dim.setObjectName("dim")
        left.addWidget(dim)

        self.preview = QFrame()
        self.preview.setFixedSize(260, 180)
        self.preview.setStyleSheet(
            "QFrame { background: #7aa2f7; border-radius: 10px; }"
        )
        left.addWidget(self.preview)

        hex_row = QHBoxLayout()
        hex_lbl = QLabel("HEX")
        hex_lbl.setObjectName("dim")
        self.hex_label = QLabel("#7AA2F7")
        self.hex_label.setObjectName("hex")
        hex_row.addWidget(hex_lbl)
        hex_row.addStretch()
        hex_row.addWidget(self.hex_label)
        left.addLayout(hex_row)

        btn_palette = QPushButton("Палитра")
        btn_palette.setObjectName("accent")
        btn_palette.clicked.connect(self.choose_color)
        left.addWidget(btn_palette)

        btn_copy = QPushButton("Скопировать HEX")
        btn_copy.clicked.connect(self.copy_hex)
        left.addWidget(btn_copy)

        left.addStretch()
        root.addLayout(left)

        right = QVBoxLayout()
        right.setSpacing(10)

        title2 = QLabel("Цветовые модели")
        title2.setFont(QFont("Segoe UI", 14, QFont.Bold))
        right.addWidget(title2)

        dim2 = QLabel("Изменяйте любую компоненту — остальные обновятся автоматически")
        dim2.setObjectName("dim")
        right.addWidget(dim2)

        right.addWidget(self._make_group("RGB", [
            ("R", 255, "#e05a5a"),
            ("G", 255, "#5ac97a"),
            ("B", 255, "#5a8fe0"),
        ]))

        right.addWidget(self._make_group("CMYK", [
            ("C", 100, "#00b8d4"),
            ("M", 100, "#e040a0"),
            ("Y", 100, "#f0d000"),
            ("K", 100, "#888888"),
        ]))

        right.addWidget(self._make_group("HSV", [
            ("H", 359, "#d0a0ff"),
            ("S", 100, "#ff8080"),
            ("V", 100, "#a0d0ff"),
        ]))

        right.addStretch()
        root.addLayout(right, 1)

        self.update_from_rgb(self.r, self.g, self.b, source="RGB")

    def _make_group(self, title, fields):
        group = QGroupBox(title)
        grid = QGridLayout(group)
        grid.setContentsMargins(12, 16, 12, 12)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        for i, (label, maxv, color) in enumerate(fields):
            tag = QFrame()
            tag.setFixedSize(10, 10)
            tag.setStyleSheet(f"background: {color}; border-radius: 5px;")

            lbl = QLabel(label)
            lbl.setFixedWidth(18)

            var = QSpinBox()
            var.setRange(0, maxv)
            var.setValue(0)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, maxv)
            slider.setValue(0)

            slider.valueChanged.connect(var.setValue)
            var.valueChanged.connect(slider.setValue)

            slider.valueChanged.connect(lambda v, n=label: self._on_change(n))
            var.valueChanged.connect(lambda v, n=label: self._on_change(n))

            grid.addWidget(tag, i, 0)
            grid.addWidget(lbl, i, 1)
            grid.addWidget(slider, i, 2)
            grid.addWidget(var, i, 3)

            self.vars[label] = var
            self.sliders[label] = slider

        return group

    def _on_change(self, name):
        if self.updating:
            return

        vals = {k: v.value() for k, v in self.vars.items()}

        if name in ("R", "G", "B"):
            self.update_from_rgb(vals["R"], vals["G"], vals["B"], source="RGB")
        elif name in ("C", "M", "Y", "K"):
            r, g, b = cmyk_to_rgb(vals["C"], vals["M"], vals["Y"], vals["K"])
            self.update_from_rgb(r, g, b, source="CMYK")
        elif name in ("H", "S", "V"):
            r, g, b = hsv_to_rgb(vals["H"], vals["S"], vals["V"])
            self.update_from_rgb(r, g, b, source="HSV")

    def update_from_rgb(self, r, g, b, source):
        self.updating = True

        self.r, self.g, self.b = int(r), int(g), int(b)

        if source != "RGB":
            self.vars["R"].setValue(self.r)
            self.vars["G"].setValue(self.g)
            self.vars["B"].setValue(self.b)

        if source != "CMYK":
            c, m, y, k = rgb_to_cmyk(self.r, self.g, self.b)
            self.vars["C"].setValue(c)
            self.vars["M"].setValue(m)
            self.vars["Y"].setValue(y)
            self.vars["K"].setValue(k)

        if source != "HSV":
            h, s, v = rgb_to_hsv(self.r, self.g, self.b)
            self.vars["H"].setValue(h)
            self.vars["S"].setValue(s)
            self.vars["V"].setValue(v)

        hex_color = f"#{self.r:02X}{self.g:02X}{self.b:02X}"
        self.hex_label.setText(hex_color.upper())
        self.preview.setStyleSheet(
            f"QFrame {{ background: {hex_color}; border-radius: 10px; }}"
        )

        self.updating = False

    def choose_color(self):
        color = QColorDialog.getColor(
            QColor(self.r, self.g, self.b), self, "Выберите цвет"
        )
        if color.isValid():
            self.update_from_rgb(color.red(), color.green(), color.blue(),
                                 source="RGB")

    def copy_hex(self):
        QApplication.clipboard().setText(self.hex_label.text())


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = ColorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()