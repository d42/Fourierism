from itertools import product, zip_longest
import math

from PySide.QtGui import (QDialog, QWidget, QFileDialog, QImage,
                          QDialogButtonBox, QPen, QBrush, QImage, QPixmap,
                          QPainter)

from ui.ui_noise_dialog import Ui_Dialog
from ui.ui_noise_dialog_custom import Ui_Form as CustomLayoutSetup
from ui.ui_noise_dialog_stripes import Ui_Form as StripesLayoutSetup
from ui.ui_noise_dialog_squares import Ui_Form as SquaresLayoutSetup




class SubLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_actions()

    def setup_actions(self):
        pass


class CustomLayout(SubLayout, CustomLayoutSetup):
    def setup_actions(self):
        self.load_file.clicked.connect(self.file_dialog)

    def file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Pattern",
                filter="images (*.png *.jpg *.bmp)")
        if not path: return
        self.path_label.setText(path)

    @property
    def settings(self):
        return {'path': self.path_label.text()}

    def gen_painter(self, settings):
        path = settings['path']
        spacing = settings['spacing']
        opacity = settings['opacity']

        def p(painter, color):
            tile_image = QImage(path)

            return
        return p


class SquaresLayout(SubLayout, SquaresLayoutSetup):
    def setup_actions(self):
        pass

    @property
    def settings(self):
        return {'width': self.slider_width.value(),
                'height': self.slider_height.value()}

    def gen_painter(self, settings):
        spacing = settings['spacing']
        opacity = settings['opacity']
        random = settings['random']
        sq_width, sq_height = settings['width'], settings['height']
        # I'm not too fond of generating my own textures, because .setPixel
        # performance gave me serious ptsd already.
        noise_brush = QBrush(QImage(":misc/noise.png"))

        def p(painter, color):
            device = painter.device()
            width, height = device.width(), device.height()

            painter.setOpacity(opacity/100)

            for x, y in product(range(0, width, sq_width+spacing),
                                range(0, height, sq_height+spacing)):
                brush = noise_brush if random else color
                painter.fillRect(x, y, sq_width, sq_height, brush)
        return p


class StripesLayout(SubLayout, StripesLayoutSetup):

    @property
    def settings(self):
        ang = (self.dial_angle.value() - 90) % 360

        return {'thickness': self.slider_thickness.value(),
                'angle': ang} # normalizing

    def gen_painter(self, settings):
        spacing = settings['spacing']
        thickness = settings['thickness']
        opacity = settings['opacity']
        random = settings['random']
        angle = settings['angle']
        angle = angle - 180 if (angle > 180) else angle
        noise_brush = QBrush(QImage(":misc/noise.png"))

        def p(painter, color):
            device = painter.device()
            width, height = device.width(), device.height()
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen()
            pen.setWidth(thickness)
            if random:
                pen.setBrush(noise_brush)
            painter.setPen(pen)
            painter.setOpacity(opacity/100)

            def getpoints(x, y):
                if angle in [0, 180]:
                    return (0, y), (width, y)
                if angle in [90, 270]:
                    return (x, 0), (x, height)
                derp = max(height, width)
                deg = math.radians(angle)
                p1 = (x - derp*math.cos(deg), y + derp * math.sin(deg))
                p2 = (x+derp*math.cos(deg), y - derp * math.sin(deg))
                return p1, p2


            for pos in range(spacing+thickness, max(height, width), spacing+thickness):
                x = pos if angle < 90 else width-pos
                y = pos
                (x1, y1), (x2, y2) = getpoints(x, y)
                painter.drawLine(x1, y1, x2, y2)
            return
        return p


class NoiseDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_layouts()
        self.group_noise.buttonClicked.connect(self.set_layout)
        self.accepted.connect(self.on_accept)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def __iter__(self):
        for l in [self.custom_layout, self.squares_layout, self.stripes_layout]:
            yield l

    def on_accept(self):
        return self.layout.gen_painter(self.settings)

    def init_layouts(self):
        self.custom_layout = CustomLayout()
        self.squares_layout = SquaresLayout()
        self.stripes_layout = StripesLayout()

        for layout in self:
            self.gridLayout.addWidget(layout, 4, 0, 1, -1)
            layout.hide()

    def _button_to_layout(self, button):
        layout = None
        if button == self.radio_custom:
            layout = self.custom_layout

        if button == self.radio_squares:
            layout = self.squares_layout

        if button == self.radio_stripes:
            layout = self.stripes_layout
        return layout

    def set_layout(self, button):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        layout = self._button_to_layout(button)

        for l in self:
            l.hide()

        layout.show()

    @property
    def layout(self):
        layout = self._button_to_layout(self.group_noise.checkedButton())
        return layout

    @property
    def settings(self):
        settings = {}
        settings['opacity'] = self.slider_opacity.value()
        settings['spacing'] = self.slider_spacing.value()
        settings['random'] = self.check_random.isChecked()

        for key, value in self.layout.settings.items():
            settings[key] = value
        return settings

    @property
    def painter_function(self):
        return self.layout.gen_painter(self.settings)
