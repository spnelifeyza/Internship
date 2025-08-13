import numpy as np
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QImage
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QSizePolicy, QFileDialog, QScrollArea, QDialog, QRubberBand, QMessageBox, QProgressBar, QPlainTextEdit
)
import cv2
from PIL import Image
from datetime import datetime
from easy_ocr import OCRWorker
from easyocr import Reader

easyocr_reader = Reader(['en'], gpu=True)

class UploadWindow(QWidget):
    def __init__(self, go_back_callback=None):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.cv_images = {}  # Stores cropped images per index
        self.image_paths = []  # Keeps track of image paths
        self.current_index = 0  # Tracks which image is being shown
        self.ocr_results = {}  # Stores OCR results by index
        self.ocr_threads = []  # Stores running OCR threads


        # Main horizontal layout (left: buttons, right: image + thumbnails)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(40)

        # Left panel layout
        left_panel_layout = QVBoxLayout()

        # Back button at top left
        btn_back = QPushButton("←")
        btn_back.setFont(QFont("Verdana", 16))
        btn_back.setFixedSize(50, 40)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #dddddd;
            }
        """)
        btn_back.clicked.connect(self.go_back)

        # Functional buttons
        btn_upload = QPushButton("Upload Picture/s")
        btn_upload.clicked.connect(self.upload_picture)

        btn_manual = QPushButton("Manual Selection")
        btn_manual.clicked.connect(self.manual_selection)

        btn_extract = QPushButton("Extract Text")
        btn_extract.clicked.connect(self.start_text_popup)

        btn_save = QPushButton("Save as PDF")
        btn_save.clicked.connect(self.save_as_pdf)

        self.buttons = [btn_upload, btn_manual, btn_extract, btn_save]

        # Style and layout for functional buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        for btn in self.buttons:
            btn.setFont(QFont("Verdana", 14))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c5b7a;
                    color: white;
                    border-radius: 6px;
                    padding: 20px 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5b4a6a;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            button_layout.addWidget(btn)

        # Vertical centering of buttons
        button_group = QVBoxLayout()
        button_group.addStretch()
        button_group.addLayout(button_layout)
        button_group.addStretch()

        # Assemble left panel
        left_panel_layout.addWidget(btn_back, alignment=Qt.AlignLeft)
        left_panel_layout.addSpacing(30)

        left_panel_layout.addLayout(button_group)
        left_panel_layout.addStretch()

        # Right panel: image + thumbnails
        right_panel = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: white; border: 2px dashed white;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setStyleSheet("border: none;")
        right_panel.addWidget(self.scroll_area)

        # Thumbnail layout inside scroll area
        self.thumbnail_layout = QHBoxLayout()
        self.thumbnail_layout.setSpacing(2)

        thumbnail_container = QWidget()
        thumbnail_container.setLayout(self.thumbnail_layout)

        self.thumbnail_scroll = QScrollArea()
        self.thumbnail_scroll.setWidget(thumbnail_container)
        self.thumbnail_scroll.setWidgetResizable(True)
        self.thumbnail_scroll.setMinimumHeight(100)
        self.thumbnail_scroll.setMaximumHeight(120)
        self.thumbnail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.thumbnail_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnail_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: transparent;
                margin: 2px 20px 2px 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #6c5b7a;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
        """)

        right_panel.addWidget(self.thumbnail_scroll)

        # Add both panels to main layout
        main_layout.addLayout(left_panel_layout)
        main_layout.addLayout(right_panel)
        self.setLayout(main_layout)

    # go back button
    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()

    # upload picture button
    def upload_picture(self):
        # Clear previous data
        self.cv_images.clear()
        self.ocr_results.clear()
        self.ocr_threads.clear()
        self.image_label.clear()

        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_paths:
            return

        self.image_paths = file_paths
        self.current_index = 0

        # Remove previous thumbnails
        for i in reversed(range(self.thumbnail_layout.count())):
            widget = self.thumbnail_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # (devamı zaten sende var)

        # Add thumbnails for each selected image
        for i, path in enumerate(file_paths):
            thumb_label = QLabel()
            thumb_label.setPixmap(QPixmap(path).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            thumb_label.setFixedSize(90, 90)
            thumb_label.setCursor(Qt.PointingHandCursor)
            thumb_label.setStyleSheet("margin: 0px 3px;")

            # Define click handler for each thumbnail
            def make_click_handler(index):
                def handler(event):
                    self.current_index = index
                    if index in self.cv_images:
                        # Show cropped image if exists
                        cropped = self.cv_images[index]
                        rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb.shape
                        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qimg)
                    else:
                        # Show original image
                        pixmap = QPixmap(self.image_paths[index])

                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.repaint()

                return handler

            # Assign the click handler to the thumbnail
            thumb_label.mousePressEvent = make_click_handler(i)
            self.thumbnail_layout.addWidget(thumb_label)

        # Run auto-detect for each image after loading
        for i in range(len(self.image_paths)):
            self.auto_detect_document(i)

    def auto_detect_document(self, index):
        try:
            img_cv = cv2.imread(self.image_paths[index])
            doc = self.detect_document(img_cv)
            if doc is not None:
                self.cv_images[index] = doc  # Save cropped result
                self.start_ocr_thread(index, doc)

                # Convert to pixmap and show
                rgb = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)

                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                if index == self.current_index:
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.repaint()

                # Update thumbnail
                thumb_pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb_widget = self.thumbnail_layout.itemAt(index).widget()
                if thumb_widget:
                    thumb_widget.setPixmap(thumb_pixmap)
                    thumb_widget.repaint()
        except Exception as e:
            print(f"[Auto Detect Error] Image {index}: {e}")

    def detect_document(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2)
                return self.four_point_transform(image, pts)

        return None  # no document found

    def four_point_transform(self, image, pts):
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def manual_selection(self):
        if not self.image_paths:
            QMessageBox.warning(self, "No image", "Please upload at least one image first.")
            return

        image_path = self.image_paths[self.current_index]
        dialog = ManualSelector(image_path, self)
        if dialog.exec_() == QDialog.Accepted:
            cropped = dialog.get_cropped_image()
            if cropped is not None:
                self.cv_images[self.current_index] = cropped

                # Convert cropped image to QPixmap
                rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)

                # Resize and update main image
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.repaint()

                # Update thumbnail
                thumb_pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb_widget = self.thumbnail_layout.itemAt(self.current_index).widget()
                if thumb_widget:
                    thumb_widget.setPixmap(thumb_pixmap)
                    thumb_widget.repaint()

                # 🔥 OCR thread başlat!
                self.start_ocr_thread(self.current_index, cropped)

    def start_ocr_thread(self, index, image):
        worker = OCRWorker(index, image, easyocr_reader)  # reader parametresi veriliyor
        worker.result_ready.connect(self.store_ocr_result)
        self.ocr_threads.append(worker)
        worker.start()

    def store_ocr_result(self, index, result):
        self.ocr_results[index] = result

    def start_text_popup(self):
        if not self.image_paths:
            QMessageBox.warning(self, "No image", "Please upload at least one image first.")
            return

        index = self.current_index

        if index in self.ocr_results:
            self.show_text_popup(index)
            return

        # Create waiting dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("OCR in Progress")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("background-color: #3e2f4c;")

        layout = QVBoxLayout(dialog)

        label = QLabel("OCR is still preparing...")
        label.setStyleSheet("color: white; font-size: 16px; font-family: Verdana;")
        label.setAlignment(Qt.AlignCenter)

        progress = QProgressBar()
        progress.setRange(0, 0)  # Infinite loop
        progress.setTextVisible(False)
        progress.setStyleSheet("""
            QProgressBar {
                background-color: #2b1f33;
                border: 2px solid #6c5b7a;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                background-color: #8c78aa;
            }
        """)

        layout.addStretch()
        layout.addWidget(label)
        layout.addSpacing(10)
        layout.addWidget(progress)
        layout.addStretch()

        # Timer to check OCR status
        def check_ready():
            if index in self.ocr_results:
                timer.stop()
                dialog.accept()
                QTimer.singleShot(100, lambda: self.show_text_popup(index))

        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(check_ready)
        timer.start(300)

        dialog.exec_()

    def show_text_popup(self, index):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("OCR Result")
            dialog.setMinimumSize(1200, 700)
            dialog.setStyleSheet("background-color: #3e2f4c;")

            # Main horizontal layout (text + image)
            content_layout = QHBoxLayout()

            # Text area on the left
            text_edit = QPlainTextEdit()
            text_edit.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #2b1f33;
                    color: white;
                    font-family: Verdana;
                    font-size: 14px;
                    padding: 10px;
                    border: 2px solid #6c5b7a;
                }
            """)
            text = "\n".join([str(line[1]) for line in self.ocr_results[index]])
            text_edit.setPlainText(text)
            content_layout.addWidget(text_edit, 2)

            # Image preview on the right
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            img_cv = self.cv_images[index] if index in self.cv_images else cv2.imread(self.image_paths[index])
            rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(450, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            content_layout.addWidget(image_label, 1)

            # Main vertical layout
            main_layout = QVBoxLayout(dialog)
            main_layout.addLayout(content_layout)

            # Save as TXT button
            save_btn = QPushButton("💾 Save as TXT")
            save_btn.setFont(QFont("Verdana", 12))
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c5b7a;
                    color: white;
                    border-radius: 5px;
                    padding: 10px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5b4a6a;
                }
            """)
            main_layout.addWidget(save_btn, alignment=Qt.AlignLeft | Qt.AlignBottom)

            def save_text():
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_path, _ = QFileDialog.getSaveFileName(
                    dialog, "Save Text", f"ocr_result_{now}.txt", "Text Files (*.txt)"
                )
                if output_path:
                    try:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(text_edit.toPlainText())
                        QMessageBox.information(dialog, "Saved", f"Text saved:\n{output_path}")
                    except Exception as e:
                        QMessageBox.critical(dialog, "Error", f"Failed to save text:\n{str(e)}")

            save_btn.clicked.connect(save_text)

            dialog.setLayout(main_layout)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display OCR result:\n{str(e)}")

    def save_as_pdf(self):
        if not self.image_paths:
            QMessageBox.warning(self, "No images", "Please upload at least one image.")
            return

        images = []

        for i, path in enumerate(self.image_paths):
            if i in self.cv_images:
                img_cv = self.cv_images[i]
            else:
                img_cv = cv2.imread(path)

            rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb).convert("RGB")
            images.append(pil_image)

        if not images:
            QMessageBox.warning(self, "No images", "No valid images found.")
            return

        # Generate file name
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"scanned_{now}.pdf", "PDF Files (*.pdf)")
        if not output_path:
            return

        # Save all images as a multi-page PDF
        try:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            QMessageBox.information(self, "Success", f"PDF saved:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")


class ManualSelector(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select 4 Corners")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #6c5b7a")

        self.points = []
        self.image_path = image_path
        self.original = cv2.imread(image_path)
        self.image = self.original.copy()

        self.display_width = 800
        self.display_height = 600
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, self.display_width, self.display_height)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px solid white;")

        # Resize original image proportionally to fit 800x600
        orig_h, orig_w = self.image.shape[:2]
        self.scale_x = self.display_width / orig_w
        self.scale_y = self.display_height / orig_h
        self.scale = min(self.scale_x, self.scale_y)

        self.resized_w = int(orig_w * self.scale)
        self.resized_h = int(orig_h * self.scale)
        self.offset_x = (self.display_width - self.resized_w) // 2
        self.offset_y = (self.display_height - self.resized_h) // 2

        self.update_display()
        self.label.mousePressEvent = self.mouse_click

    def update_display(self):
        resized = cv2.resize(self.image, (self.resized_w, self.resized_h))
        display = np.full((self.display_height, self.display_width, 3), (163, 121, 144), dtype=np.uint8)
        display[self.offset_y:self.offset_y+self.resized_h, self.offset_x:self.offset_x+self.resized_w] = resized

        for pt in self.points:
            cv2.circle(display, pt, 6, (255, 255, 255), -1)

        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                cv2.line(display, self.points[i-1], self.points[i], (255, 255, 255), 2)
        if len(self.points) == 4:
            cv2.line(display, self.points[3], self.points[0], (255, 255, 255), 2)

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, self.display_width, self.display_height, self.display_width * 3, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg))

    def mouse_click(self, event):
        x = event.pos().x()
        y = event.pos().y()

        # Only accept clicks inside the image area
        if (self.offset_x <= x <= self.offset_x + self.resized_w) and (self.offset_y <= y <= self.offset_y + self.resized_h):
            self.points.append((x, y))
            self.update_display()

        if len(self.points) == 4:
            result = QMessageBox.question(self, "Confirm", "Use this selection?", QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                self.accept()
            else:
                self.points.clear()
                self.update_display()

    def get_cropped_image(self):
        if len(self.points) != 4:
            return None

        # Scale points back to original image resolution
        orig_points = []
        for x, y in self.points:
            orig_x = int((x - self.offset_x) / self.scale)
            orig_y = int((y - self.offset_y) / self.scale)
            orig_points.append((orig_x, orig_y))

        pts = np.array(orig_points, dtype="float32")
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(self.original, M, (maxWidth, maxHeight))
        return warped

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect







