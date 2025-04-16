from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QRect

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QMouseEvent, QWheelEvent
from PyQt5.QtCore import Qt, QRect, QSize

class CompareSlider(QWidget):
    def __init__(self, original_pixmap: QPixmap, generated_pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.original = original_pixmap
        self.generated = generated_pixmap
        self.slider_pos = self.width() // 2
        self.zoom_factor = 1.0  # ← initial zoom

    def resizeEvent(self, event):
        self.slider_pos = self.width() // 2
        self.update()

    def paintEvent(self, event):
        if self.original.isNull() or self.generated.isNull():
            return

        painter = QPainter(self)
        widget_rect = self.rect()

        # Apply zoom to image sizes
        zoomed_size = QSize(int(widget_rect.width() * self.zoom_factor), int(widget_rect.height() * self.zoom_factor))
        original_scaled = self.original.scaled(zoomed_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        generated_scaled = self.generated.scaled(zoomed_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Center cropping offset
        offset_x = (original_scaled.width() - widget_rect.width()) // 2
        offset_y = (original_scaled.height() - widget_rect.height()) // 2
        source_rect = QRect(offset_x, offset_y, widget_rect.width(), widget_rect.height())

        # Draw original full
        painter.drawPixmap(widget_rect, original_scaled, source_rect)

        # Draw generated on right half
        mask_rect = QRect(self.slider_pos, 0, widget_rect.width() - self.slider_pos, widget_rect.height())
        painter.drawPixmap(mask_rect, generated_scaled.copy(source_rect.adjusted(self.slider_pos, 0, 0, 0)))

        # Draw slider bar
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

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        zoom_step = 0.1
        if delta > 0:
            self.zoom_factor += zoom_step
        else:
            self.zoom_factor -= zoom_step

        self.zoom_factor = max(0.5, min(self.zoom_factor, 5.0))  # Clamp zoom
        self.update()


from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QPen, QMouseEvent, QWheelEvent

class CompareView(QGraphicsView):
    def __init__(self, original: QPixmap, generated: QPixmap, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.original_item = QGraphicsPixmapItem(original)
        self.generated_item = ClippedPixmapItem(generated)

        self.scene.addItem(self.original_item)
        self.scene.addItem(self.generated_item)

        self.slider_pos = original.width() // 2
        self.zoom_factor = 1.0

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.updateMask()

    def drawForeground(self, painter, rect):
        # Draw the vertical red slider bar
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(int(self.slider_pos), int(rect.top()), int(self.slider_pos), int(rect.bottom()))


    def updateMask(self):
        full_rect = QRectF(0, 0, self.generated_item.pixmap().width(), self.generated_item.pixmap().height())
        mask_rect = QRectF(self.slider_pos, 0, full_rect.width() - self.slider_pos, full_rect.height())
        self.generated_item.setClipRect(mask_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.slider_pos = self.mapToScene(event.pos()).x()
            self.updateMask()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.slider_pos = self.mapToScene(event.pos()).x()
            self.updateMask()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom = 1.25 if delta > 0 else 0.8
        self.zoom_factor *= zoom
        self.scale(zoom, zoom)


from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRectF

class ClippedPixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, parent)
        self.clip_rect = None  # QRectF or None

    def setClipRect(self, rect: QRectF):
        self.clip_rect = rect
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        if self.clip_rect:
            painter.setClipRect(self.clip_rect)
        super().paint(painter, option, widget)
