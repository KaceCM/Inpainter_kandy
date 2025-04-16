from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QMainWindow, QSlider, QLabel, QGraphicsScene, QFileDialog, QFrame, QApplication, QPushButton,QLineEdit, QProgressDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import resources.resources
from editor import Editor
import os
import json


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Editpage(QMainWindow):
	def __init__(self, homepage, image_path):
		super().__init__()
		self.homepage = homepage
		self.image_path = image_path
		self.setupUi()
		self.moveAtCenter()

	def setupUi(self):

		uic.loadUi(resource_path("ui_edit.ui"), self)
		self.penButton = self.findChild(QPushButton, "pen_button")
		self.eraserButton = self.findChild(QPushButton, "eraser_button")
		self.backButton = self.findChild(QPushButton, "back_button")
		self.inpaintButton = self.findChild(QPushButton, "inpaint_button")
		self.saveButton = self.findChild(QPushButton, "save_button")
		self.saveMaskButton = self.findChild(QPushButton, "save_mask_button")
		self.resetButton = self.findChild(QPushButton, "reset_button")
		self.minButton = self.findChild(QPushButton, "min_button")
		self.maxButton = self.findChild(QPushButton, "max_button")
		self.greenMarker = self.findChild(QPushButton, "green_marker")
		self.redMarker = self.findChild(QPushButton, "red_marker")
		self.blueMarker = self.findChild(QPushButton, "blue_marker")
		self.markerWidthSlider = self.findChild(QSlider, "marker_width_slider")
		self.titleBar = self.findChild(QFrame, "title_bar")
		self.infoLabel = self.findChild(QLabel, "info_label")
		self.textPrompt = self.findChild(QLineEdit, "info_input")
		self.inpaintRatio = self.findChild(QLineEdit, "ratio_input")
		self.mainFrame = self.findChild(QFrame, "main_frame")
		self.viewFrame = self.findChild(QFrame, "view_frame")
		self.chooseMethod = self.findChild(QComboBox, "choose_method")
		self.offset = None
		self.chooseMethod.currentIndexChanged.connect(self.selectionChange)

		self.penButton.setProperty('selected', True)
		self.penButton.setStyle(self.penButton.style())
		self.eraserButton.setProperty('selected', False)
		self.eraserButton.setStyle(self.penButton.style())

		self.penButton.clicked.connect(self.penSelect)
		self.eraserButton.clicked.connect(self.eraserSelect)
		self.backButton.clicked.connect(self.goBack)
		self.minButton.clicked.connect(self.showMinimized)
		self.maxButton.clicked.connect(self.maximize)

		self.redMarker.setProperty('selected', True)
		self.redMarker.setStyle(self.redMarker.style())
		self.greenMarker.setProperty('selected', False)
		self.greenMarker.setStyle(self.greenMarker.style())
		self.blueMarker.setProperty('selected', False)
		self.blueMarker.setStyle(self.blueMarker.style())

		self.redMarker.clicked.connect(self.redSelect)
		self.blueMarker.clicked.connect(self.blueSelect)
		self.greenMarker.clicked.connect(self.greenSelect)

	

		self.inpaintButton.clicked.connect(self.inpaintImage)
		self.saveButton.clicked.connect(self.saveImage)
		self.saveMaskButton.clicked.connect(self.saveOptions)
		self.resetButton.clicked.connect(self.resetImage)		
		


		flags = Qt.WindowFlags(Qt.FramelessWindowHint)
		self.setWindowFlags(flags)
		self.setAttribute(Qt.WA_TranslucentBackground)

		self.scene = QGraphicsScene()

		self.imageView = Editor(self.scene, self.viewFrame,
		                        slider=self.markerWidthSlider)
		self.imageView.setPhoto(QPixmap(self.image_path))

		vbox = QVBoxLayout()
		vbox.addWidget(self.imageView)
		self.viewFrame.setLayout(vbox)
		
		####--add new inpainting methods here--####
		 
		# self.addInpaintingMethod("Deepfill") 
	
		####-----------------------------------####
	
	def moveAtCenter(self):
		screen = QApplication.desktop().screenGeometry()
		x = (screen.width() - self.width())//2
		y = (screen.height() - self.height())//2
		self.move(x, y)

	def selectionChange(self):
		self.imageView.setInpaintingMethod(self.chooseMethod.currentText())

	def addInpaintingMethod(self, method):
		if not isinstance(method, str):
			raise Exception("method should be a string.")
		self.chooseMethod.addItem(method)

	def maximize(self):
		if self.isMaximized():
			self.showNormal() 
		else:
			self.showMaximized()
	
	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.offset = event.pos()
		else:
			super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self.offset is not None and event.buttons() == Qt.LeftButton:
			self.move(self.pos() + event.pos() - self.offset)
		else:
			super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self.offset = None
		super().mouseReleaseEvent(event)	
	
	def updateView(self):
		scene = self.imageView.scene()
		r = scene.sceneRect()
		self.imageView.fitInView(r, Qt.KeepAspectRatio)
	
	def resizeEvent(self, event):
		self.updateView()
		
	def showEvent(self, event):
		if not event.spontaneous():
			self.updateView()

		
	def redSelect(self):
		self.redMarker.setProperty('selected',True)
		self.redMarker.setStyle(self.redMarker.style())
		self.greenMarker.setProperty('selected',False)
		self.greenMarker.setStyle(self.greenMarker.style())
		self.blueMarker.setProperty('selected',False)
		self.blueMarker.setStyle(self.blueMarker.style())
		self.imageView.brushColor = "red"	

	def greenSelect(self):
		self.redMarker.setProperty('selected',False)
		self.redMarker.setStyle(self.redMarker.style())
		self.greenMarker.setProperty('selected',True)
		self.greenMarker.setStyle(self.greenMarker.style())
		self.blueMarker.setProperty('selected',False)
		self.blueMarker.setStyle(self.blueMarker.style())
		self.imageView.brushColor = "green"	

	def blueSelect(self):
		self.redMarker.setProperty('selected',False)
		self.redMarker.setStyle(self.redMarker.style())
		self.greenMarker.setProperty('selected',False)
		self.greenMarker.setStyle(self.greenMarker.style())
		self.blueMarker.setProperty('selected',True)
		self.blueMarker.setStyle(self.blueMarker.style())
		self.imageView.brushColor = "blue"	

	def penSelect(self):
		self.penButton.setProperty('selected',True)
		self.penButton.setStyle(self.penButton.style())
		self.eraserButton.setProperty('selected',False)
		self.eraserButton.setStyle(self.penButton.style())
		self.imageView.drawMode = True


	def eraserSelect(self):
		self.penButton.setProperty('selected',False)
		self.penButton.setStyle(self.penButton.style())
		self.eraserButton.setProperty('selected',True)
		self.eraserButton.setStyle(self.penButton.style())
		self.imageView.drawMode = False


	def goBack(self):
		self.homepage.show()
		self.hide()
		

	def inpaintImage(self):
		if self.imageView.hasBeenSet:
			progress = QProgressDialog("Generating image...", None, 0, 0, self)
			progress.setWindowTitle("Processing")
			progress.setWindowModality(Qt.WindowModal)
			progress.setCancelButton(None)  # No cancel button
			progress.show()
			
			# Process any pending events so that the dialog is updated
			QApplication.processEvents()
			self.imageView.inpaint(textPrompt=self.textPrompt.text(), ratio=self.inpaintRatio.text(), merge=True)

			progress.close()
		else:
			print(Exception("No mask has been created!"))
			return
		

	def saveImage(self):
		self.imageView.save()


	def saveOptions(self):
		try:
			self.saveMask()
			if self.textPrompt.text() == "":
				return
			self.savePrompt()
			return True
		except Exception as e:
			print("error \n", e)
			return

	def savePrompt(self):
		try:
			image_prompt = self.textPrompt.text()
			init_image_name = self.init_image_name

			savePath = self.maskPath.split(".png")[0] + ".json"
			with open(savePath, "w") as f:
				json.dump({"image_name": init_image_name, "image_path": self.image_path, "mask_path": self.maskPath, "prompt": image_prompt}, f, indent=4)
			return savePath
		except Exception as e:
			print("error \n", e)
			return None



	def saveMask(self):
		self.init_image_name = self.image_path.split("/")[-1].replace(".jpg", ".png")
		try:
			mask_path, _ = QFileDialog.getSaveFileName(None, "Save mask file...", f"./masks/mask_{self.init_image_name}", "PNG files (*.png)")
			mask_path += ".png" if not mask_path.endswith(".png") else ""
			self.imageView._mask.save(mask_path)
			self.maskPath = mask_path
		except Exception as e:
			print("error \n", e)
			return

	def resetImage(self):
		print(self.textPrompt.text())
		self.imageView.reset()


	
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editpage = Editpage(None, None, None)
    editpage.show()
    app.exec()
		

