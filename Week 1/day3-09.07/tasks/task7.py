# comparing blur filters: median VS gaussian VS bilateral
import cv2
import numpy as np

cap = cv2.VideoCapture(0) # open the default camera (webcam)

while True:
    ret, frame = cap.read() # read the image
    if not ret: #if image can't be read correct -> ret:False
        break

    frame = cv2.resize(frame, (400,400)) # resize image

    median = cv2.medianBlur(frame, 5) # median blur filter
    gaussian = cv2.GaussianBlur(frame, (5,5), 0) # gaussian blur filter
    bilateral = cv2.bilateralFilter(frame, 9, 75, 75) # bilateral blur filter

    # write text on images
    cv2.putText(median, "Median", (155,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,100,0), 2)
    cv2.putText(gaussian, "Gaussian", (155,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,100,0), 2)
    cv2.putText(bilateral, "Bilateral", (155,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,100,0), 2)

    # merge frames
    combined = np.hstack((median, gaussian, bilateral))
    cv2.imshow("Comparison", combined) # show frames

    if cv2.waitKey(1) % 0XFF == ord('q'): # if user press 'q', quit
        break

cap.release() # close the image
cv2.destroyAllWindows() # close windows