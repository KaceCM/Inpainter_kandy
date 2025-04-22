# stylepage.py
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit,
    QFrame, QApplication
)
from PyQt5.QtGui import QPixmap
from compare_slider import CompareView
from backend import change_style

class StylePage(QMainWindow):
    def __init__(self, homepage, image_path):
        super().__init__()
        self.homepage = homepage
        self.image_path = image_path
        self.setupUi()
        self.resize(800, 600)
        self.moveAtCenter()

    def setupUi(self):
        self.setWindowTitle("Style Change")
        self.mainFrame = QFrame(self)
        self.setCentralWidget(self.mainFrame)

        # Layout principal
        self.mainLayout = QVBoxLayout(self.mainFrame)

        # 1) Conteneur image
        self.imageContainer = QWidget(self.mainFrame)
        self.imageLayout = QVBoxLayout(self.imageContainer)
        self.scene = QGraphicsScene(self)
        self.imageView = QGraphicsView(self.scene)
        self.original_pixmap = QPixmap(self.image_path)
        self.scene.addPixmap(self.original_pixmap)
        self.imageLayout.addWidget(self.imageView)
        self.mainLayout.addWidget(self.imageContainer)

        # Champ de saisie du style
        self.styleInput = QLineEdit(self)
        self.styleInput.setPlaceholderText("Enter style description…")
        self.mainLayout.addWidget(self.styleInput)

        # 2) Barre de boutons
        self.buttonsContainer = QWidget(self.mainFrame)
        self.buttonsLayout = QHBoxLayout(self.buttonsContainer)
        self.styleButton = QPushButton("Apply Style", self)
        self.resetButton = QPushButton("Reset", self)
        self.saveButton  = QPushButton("Save",  self)
        for btn in (self.styleButton, self.resetButton, self.saveButton):
            self.buttonsLayout.addWidget(btn)
        self.mainLayout.addWidget(self.buttonsContainer)

        # Connexions
        self.styleButton.clicked.connect(self.changeStyle)
        self.resetButton.clicked.connect(self.resetImage)
        self.saveButton.clicked.connect(self.saveImage)

    def moveAtCenter(self):
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def changeStyle(self):
        # TODO: récupérer l'image numpy, faire result = change_style(..., self.styleInput.text())
        result = self.original_pixmap
        self.showComparison(result)

    def showComparison(self, result: QPixmap):
        for i in reversed(range(self.imageLayout.count())):
            w = self.imageLayout.itemAt(i).widget()
            if w:
                w.setParent(None)
        slider = CompareView(self.original_pixmap, result, self.imageContainer)
        self.imageLayout.addWidget(slider)

    def resetImage(self):
        self.scene.clear()
        self.scene.addPixmap(self.original_pixmap)
        for i in reversed(range(self.imageLayout.count())):
            w = self.imageLayout.itemAt(i).widget()
            if isinstance(w, CompareView):
                w.setParent(None)
        self.imageLayout.addWidget(self.imageView)

    def saveImage(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save image", "", "PNG Files (*.png)")
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            # TODO: enregistrer l'image courante
