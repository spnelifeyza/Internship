import sys
from PyQt5.QtWidgets import QApplication

from main_window import MainWindow  # Import your main window class

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
