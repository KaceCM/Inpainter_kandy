from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QRect

class CompareSlider(QWidget):
    def __init__(self, original_pixmap: QPixmap, generated_pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.original = original_pixmap
        self.generated = generated_pixmap
        self.slider_pos = self.width() // 2  # Start centered

    def resizeEvent(self, event):
        self.slider_pos = self.width() // 2
        self.update()

    def paintEvent(self, event):
        if self.original.isNull() or self.generated.isNull():
            return

        painter = QPainter(self)

        # Resize both images to fit the widget size
        widget_rect = self.rect()
        original_scaled = self.original.scaled(widget_rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        generated_scaled = self.generated.scaled(widget_rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Center images by calculating offset
        offset_x = (original_scaled.width() - widget_rect.width()) // 2
        offset_y = (original_scaled.height() - widget_rect.height()) // 2
        source_rect = QRect(offset_x, offset_y, widget_rect.width(), widget_rect.height())

        # Draw original full
        painter.drawPixmap(widget_rect, original_scaled, source_rect)

        # Draw generated on right side only
        mask_rect = QRect(self.slider_pos, 0, widget_rect.width() - self.slider_pos, widget_rect.height())
        painter.drawPixmap(mask_rect, generated_scaled.copy(source_rect.adjusted(self.slider_pos, 0, 0, 0)))

        # Draw red slider bar
        painter.setPen(Qt.red)
        painter.drawLine(self.slider_pos, 0, self.slider_pos, widget_rect.height())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.slider_pos = event.pos().x()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.slider_pos = max(0, min(event.pos().x(), self.width()))
            self.update()
