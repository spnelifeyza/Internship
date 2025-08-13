# DOCSee

DOCSee is a full-featured document scanning and OCR (Optical Character Recognition) application built with **Python**, **PyQt5**, **OpenCV**, and **EasyOCR**. It allows you to scan documents from both **uploaded images** and **webcam input**, automatically detect and crop the document, apply perspective correction and enhancement, and extract editable text. It also supports **multi-page PDF export**, **manual corner selection**, and **real-time OCR threading** for a smooth user experience.

---

## ✨ Features

- **📷 Image & Webcam Input**
  - Upload single or multiple images
  - Live webcam document detection and capture
  - Automatic document detection on upload

- **📐 Document Detection & Manual Selection**
  - Automatic contour-based document detection
  - Perspective correction with four-point transform
  - Manual selection via:
    - Rectangle drawing
    - Corner-by-corner clicking with real-time line connections

- **🖼 Image Processing**
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - Adaptive Thresholding for better OCR accuracy
  - Morphological operations for noise removal

- **🔍 OCR (Text Extraction)**
  - EasyOCR integration with background threading (no UI freeze)
  - Instant text availability when the OCR window opens
  - Spell checking and low-confidence result filtering
  - Side-by-side image & text popup editor with highlighting

- **💾 Export Options**
  - Save scanned images as **multi-page PDFs**
  - Save OCR results as **.txt** files with automatic timestamp naming

- **🖥 User Interface**
  - Multi-image upload with clickable thumbnails
  - Scrollable thumbnail panel (horizontal or vertical)
  - Light/Dark theme toggle
  - Animated scrolling icons
  - Fixed-size, centered layout with consistent spacing

---

## 🛠 Tech Stack

- **Language:** Python 3.x
- **GUI Framework:** PyQt5
- **Image Processing:** OpenCV
- **OCR Engine:** EasyOCR
- **PDF Export:** ReportLab
- **Spell Checking:** JamSpell

---

## 📂 Project Structure

