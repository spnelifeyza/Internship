# comparing thresholds: binary VS adaptive
import cv2
import numpy as np

cap = cv2.VideoCapture(0) # open the default camera (webcam)

while True:
    ret, frame = cap.read() # read the image
    if not ret: # if ret:False
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to gray

    # binary threshold
    _, binary = cv2.threshold(gray, 107, 255, cv2.THRESH_BINARY)

    # adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        5,2 # LOOK FOR IT
    )

    cv2.putText(binary, "Binary Threshold", (210,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) # write the text on binary field
    cv2.putText(adaptive, "Adaptive Threshold", (210,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) # write the text on adaptive field

    combined = np.hstack((binary, adaptive)) # merge two frames
    cv2.imshow("Threshold Comparison", combined) # show combined frame


    if cv2.waitKey(1) & 0XFF == ord('q'): # if user press 'q', quit
        break

cap.release() # close the image
cv2.destroyAllWindows() # close windows