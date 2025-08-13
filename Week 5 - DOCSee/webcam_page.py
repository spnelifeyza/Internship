import cv2
import numpy as np
import os
import atexit
from datetime import datetime
from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QScrollArea, QMessageBox, QDialog, QFileDialog, QProgressBar, QPlainTextEdit
)
from easyocr import Reader
from easy_ocr import OCRWorker

easyocr_reader = Reader(['en'], gpu=True)


class WebcamWindow(QWidget):
    def __init__(self, go_back_callback=None):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.detected_counter = 0
        self.last_detected_corners = None
        self.temp_files = []
        self.captured_images = {}
        self.current_index = 0
        self.timer = QTimer()
        self.cap = None
        self.ocr_results = {}  # Stores OCR results by index
        self.ocr_threads = []  # Stores OCR threads

        atexit.register(self.cleanup_temp_files)

        # Layout setup
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(40)

        # Left panel with buttons
        left_panel = QVBoxLayout()
        btn_back = QPushButton("←")
        btn_back.setFont(QFont("Verdana", 16))
        btn_back.setFixedSize(50, 40)
        btn_back.setStyleSheet("QPushButton { background: transparent; color: white; border: none; font-weight: bold; }")
        btn_back.clicked.connect(self.go_back)

        buttons = [
            ("Open Webcam", self.open_webcam),
            ("Take Picture", self.take_picture),
            ("Manual Selection", self.manual_selection),
            ("Extract Text", self.start_text_popup),
            ("Save as PDF", self.save_as_pdf)
        ]

        button_layout = QVBoxLayout()
        for label, func in buttons:
            button_layout.setSpacing(20)
            btn = QPushButton(label)
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
            btn.clicked.connect(func)
            button_layout.addWidget(btn)

        button_group = QVBoxLayout()
        button_group.addStretch()
        button_group.addLayout(button_layout)
        button_group.addStretch()

        left_panel.addWidget(btn_back, alignment=Qt.AlignLeft)
        left_panel.addSpacing(30)
        left_panel.addLayout(button_group)
        left_panel.addStretch()

        # Right panel with image
        right_panel = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: white; border: 2px dashed white;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(100, 100)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setStyleSheet("border: none;")
        right_panel.addWidget(self.scroll_area)

        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        self.setLayout(main_layout)

    def go_back(self):
        if self.cap:
            self.cap.release()
        if self.timer.isActive():
            self.timer.stop()
        if self.go_back_callback:
            self.go_back_callback()

    def cleanup_temp_files(self):
        for path in self.temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Could not delete {path}: {e}")

    def open_webcam(self):
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open webcam.")
            return
        self.detected_counter = 0
        self.last_detected_corners = None
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        self.cv_image = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        document_contour = None
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                document_contour = approx
                break

        if document_contour is not None:
            current_corners = document_contour.reshape(4, 2)
            if self.last_detected_corners is not None:
                diffs = [np.linalg.norm(c1 - c2) for c1, c2 in zip(current_corners, self.last_detected_corners)]
                if np.mean(diffs) < 25:
                    self.detected_counter += 1
                else:
                    self.detected_counter = 0
            else:
                self.detected_counter = 0
            self.last_detected_corners = current_corners
            cv2.drawContours(frame, [document_contour], -1, (0, 255, 0), 2)
            if self.detected_counter >= 6:
                self.timer.stop()
                if self.cap:
                    self.cap.release()
                warped = self.four_point_transform(self.cv_image.copy(), current_corners)
                self.captured_images[self.current_index] = warped
                self.display_captured(warped)
                self.start_ocr_thread(self.current_index, warped)
                return
        else:
            self.detected_counter = 0
            self.last_detected_corners = None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def four_point_transform(self, image, pts):
        rect = np.array(pts, dtype="float32")
        s = rect.sum(axis=1)
        diff = np.diff(rect, axis=1)
        rect_ordered = np.zeros((4, 2), dtype="float32")
        rect_ordered[0] = rect[np.argmin(s)]
        rect_ordered[2] = rect[np.argmax(s)]
        rect_ordered[1] = rect[np.argmin(diff)]
        rect_ordered[3] = rect[np.argmax(diff)]
        (tl, tr, br, bl) = rect_ordered
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect_ordered, dst)
        return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    def take_picture(self):
        def take_picture(self):
            if not hasattr(self, "cv_image") or self.cv_image is None:
                QMessageBox.warning(self, "No Frame", "No webcam frame available to capture.")
                return
            self.timer.stop()
            self.captured_images[self.current_index] = self.cv_image.copy()
            self.display_captured(self.cv_image)

    def display_captured(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def manual_selection(self):
        if self.current_index not in self.captured_images:
            QMessageBox.warning(self, "No Image", "Please take a picture first.")
            return
        from upload_pictures import ManualSelector
        img = self.captured_images[self.current_index]
        temp_path = f"temp_capture_{datetime.now().strftime('%H%M%S')}.jpg"
        cv2.imwrite(temp_path, img)
        self.temp_files.append(temp_path)
        dialog = ManualSelector(temp_path, self)
        if dialog.exec_() == QDialog.Accepted:
            cropped = dialog.get_cropped_image()
            if cropped is not None:
                self.captured_images[self.current_index] = cropped
                self.display_captured(cropped)
                self.start_ocr_thread(self.current_index, cropped)

    def start_ocr_thread(self, index, image):
        worker = OCRWorker(index, image, easyocr_reader)
        worker.result_ready.connect(self.store_ocr_result)
        self.ocr_threads.append(worker)
        worker.start()

    def store_ocr_result(self, index, result):
        self.ocr_results[index] = result

    def start_text_popup(self):
        index = self.current_index

        if index not in self.captured_images:
            QMessageBox.warning(self, "No Image", "Please take a picture first.")
            return

        if index in self.ocr_results:
            self.show_text_popup(index)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("OCR in Progress")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("background-color: #3e2f4c;")

        layout = QVBoxLayout(dialog)

        label = QLabel("OCR is still preparing...")
        label.setStyleSheet("color: white; font-size: 16px; font-family: Verdana;")
        label.setAlignment(Qt.AlignCenter)

        progress = QProgressBar()
        progress.setRange(0, 0)
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

        def check_ready():
            if index in self.ocr_results:
                timer.stop()
                dialog.accept()
                QTimer.singleShot(100, lambda: self.show_text_popup(index))

        timer = QTimer()
        timer.timeout.connect(check_ready)
        timer.start(300)

        dialog.exec_()

    def show_text_popup(self, index):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("OCR Result")
            dialog.setMinimumSize(1000, 600)
            dialog.setStyleSheet("background-color: #3e2f4c;")

            # Main vertical layout
            main_layout = QVBoxLayout(dialog)

            # Horizontal layout for text and image
            layout = QHBoxLayout()

            # Text area on the left
            text_edit = QPlainTextEdit()
            text_edit.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #2b1f33;
                    color: white;
                    font-family: Verdana;
                    font-size: 14px;
                    padding: 10px 15px;
                    border: 2px solid #6c5b7a;
                }
            """)
            text = "\n".join([str(line[1]) for line in self.ocr_results[index]])
            text_edit.setPlainText(text)
            layout.addWidget(text_edit, 2)

            # Image preview on the right
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            img_cv = self.captured_images.get(index)
            rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(450, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            layout.addWidget(image_label, 1)

            # Add horizontal layout to main vertical layout
            main_layout.addLayout(layout)

            # Save as TXT button
            save_btn = QPushButton("💾 Save as TXT")
            save_btn.setFont(QFont("Verdana", 12))
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c5b7a;
                    color: white;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5b4a6a;
                }
            """)
            save_btn.setFixedSize(180, 50)  # Boyut ayarlandı
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

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display OCR result:\n{str(e)}")

    def save_as_pdf(self):
        if not self.captured_images:
            QMessageBox.warning(self, "No Images", "No captured image found.")
            return
        images = []
        for img in self.captured_images.values():
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb).convert("RGB")
            images.append(pil_image)
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", f"scanned_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf", "PDF Files (*.pdf)"
        )
        if not output_path:
            return
        try:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            QMessageBox.information(self, "Success", f"PDF saved:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")
