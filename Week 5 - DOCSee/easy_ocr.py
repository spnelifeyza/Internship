import cv2
import re
from PyQt5.QtCore import QThread, pyqtSignal
import traceback

class OCRWorker(QThread):
    result_ready = pyqtSignal(int, list)

    def __init__(self, index, image, reader):
        super().__init__()
        self.index = index      # Index of the image
        self.image = image      # OpenCV BGR image
        self.reader = reader    # EasyOCR reader (shared, passed from GUI)

    def run(self):
        try:
            # Step 1: Convert to grayscale
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            # Step 2: Apply sharpening to emphasize text
            sharpened = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 1), -0.5, 0)

            # Step 3: Convert to RGB for EasyOCR
            processed = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

            # Step 4: Run EasyOCR
            results = self.reader.readtext(processed)

            # Step 5: Filter by confidence and keep valid formats
            filtered = []
            for res in results:
                text = res[1].strip()
                conf = res[2]

                if conf < 0.4 or len(text) < 2:
                    continue  # skip low confidence or meaningless short text

                if re.match(r'^[-•*]?\s*[A-Z0-9][\w\s.,:;()\-+*/=%&!?"\']+$', text):
                    filtered.append(res)

            # Step 6: Emit result
            self.result_ready.emit(self.index, filtered)

        except Exception as e:
            print(f"[OCRWorker ERROR] index={self.index} -> {e}")
            traceback.print_exc()
