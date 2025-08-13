import cv2
import numpy as np

# Open the default camera (webcam)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame to 300x300 pixels for consistent processing
    frame = cv2.resize(frame, (300, 300))

    # Convert the color image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding: pixels >127 become 255, else 0
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Create a 3x3 rectangular kernel (structuring element) for morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Apply Opening: erosion followed by dilation (removes small white noise)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Apply Closing: dilation followed by erosion (fills small black holes)
    closing = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Convert grayscale images to BGR so that text can be overlaid in color
    opening_bgr = cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    closing_bgr = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)

    # Add labels to the images for identification
    cv2.putText(opening_bgr, "Opening", (80, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 255, 0), 1)
    cv2.putText(gray_bgr, "Gray", (110, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255, 255, 0), 1)
    cv2.putText(closing_bgr, "Closing", (80, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 0, 255), 1)

    # Combine the three labeled images horizontally
    combined = np.hstack((opening_bgr, gray_bgr, closing_bgr))

    # Display the combined image in a window
    cv2.imshow("Combined", combined)

    # Exit loop and close window when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV
cap.release()
cv2.destroyAllWindows()