import os
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsOpacityEffect, QWidget, QHBoxLayout, \
    QPushButton, QVBoxLayout, QMessageBox, QDialog, QListWidget, QListWidgetItem
from PyQt5.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
from upload_pictures import UploadWindow, ManualSelector
from webcam_page import WebcamWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(400, 80, 700, 400)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("background-color:#9079a3;")
        self.setWindowTitle("DOCSee")
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        self.show()
        self.show_splash()

    def show_splash(self):
        pixmap = QPixmap("splash.png")
        self.label.setPixmap(pixmap)

        opacity = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(opacity)

        self.animation = QPropertyAnimation(opacity, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.show_main_content)
        QTimer.singleShot(2000, self.animation.start)

    def show_main_content(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        title_label = QLabel("Welcome to DOCSee")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Verdana", 28, QFont.Bold))
        title_label.setStyleSheet("color: white;")

        desc_label = QLabel(
            "• Auto-detect document edges\n"
            "• Manual corner selection is available\n"
            "• Save the result as a high-quality PDF"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Verdana", 14, italic=True))
        desc_label.setStyleSheet("color: white;")

        btn_webcam = QPushButton("📷 Open Webcam")
        btn_upload = QPushButton("🖼️ Upload Pictures")
        btn_webcam.clicked.connect(self.open_webcam_window)
        btn_upload.clicked.connect(self.open_upload_window)

        button_style = """
            QPushButton {
                background-color: #6c5b7a;
                color: white;
                padding: 30px 50px;
                border-radius: 8px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5b4a6a;
            }
        """
        btn_webcam.setStyleSheet(button_style)
        btn_upload.setStyleSheet(button_style)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_webcam)
        button_layout.addSpacing(40)
        button_layout.addWidget(btn_upload)
        button_layout.addStretch()

        # 📁 Saved Files button
        btn_saved_files = QPushButton("📁 Saved Files")
        btn_saved_files.setStyleSheet(button_style)
        btn_saved_files.clicked.connect(self.show_saved_files)

        main_layout.addStretch()
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        main_layout.addSpacing(20)
        main_layout.addWidget(desc_label, alignment=Qt.AlignCenter)
        main_layout.addSpacing(40)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(btn_saved_files, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setCentralWidget(central_widget)

    def open_upload_window(self):
        upload_widget = UploadWindow(self.show_main_content)
        self.setCentralWidget(upload_widget)

    def open_webcam_window(self):
        webcam_widget = WebcamWindow(self.show_main_content)
        self.setCentralWidget(webcam_widget)

    def show_saved_files(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Files")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #3e2f4c;")

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b1f33;
                color: white;
                font-family: Verdana;
                font-size: 14px;
                border: 2px solid #6c5b7a;
            }
            QListWidget::item:selected {
                background-color: #6c5b7a;
            }
        """)

        # Search for all .pdf and .txt files in current directory
        for filename in os.listdir("."):
            if filename.endswith(".pdf") or filename.endswith(".txt"):
                item = QListWidgetItem(filename)
                list_widget.addItem(item)

        layout.addWidget(list_widget)

        def open_file(item):
            filepath = os.path.abspath(item.text())
            try:
                if os.name == 'nt':
                    os.startfile(filepath)
                elif os.name == 'posix':
                    subprocess.call(('xdg-open', filepath))
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to open file:\n{str(e)}")

        list_widget.itemClicked.connect(open_file)

        dialog.setLayout(layout)
        dialog.exec_()
