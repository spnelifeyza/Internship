# erode and dilate
import cv2
import numpy as np

cap = cv2.VideoCapture(0) # open the default camera (webcam)

while True:
    ret, frame = cap.read() # read the image
    if not ret: # if image can't be read correct -> ret:False
        break

    frame = cv2.resize(frame, (300,300)) # resize image

    kernel = np.ones((5,5), np.uint8) # create 5x5 matrix filled by ones, type: unsigned int 8-bit
    # kernel -> little square matrix used in image processing
    # scrolling through image

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # converting to gray

    erode = cv2.erode(gray, kernel) # object reduction - erosion
    # edges of white area appear to be erased

    dilate = cv2.dilate(gray, kernel) # object expansion
    # new pixels are added to edges of white area

    # putText parameters => image, text, pos, font, scale, color, thickness
    cv2.putText(erode, "Erode", (90, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, 0, 1)
    cv2.putText(dilate, "Dilate", (90, 30), cv2.FONT_HERSHEY_TRIPLEX, 1 , 0, 1)

    combined = np.hstack((erode, dilate)) # merge frames

    cv2.imshow("Comparison", combined) # show combined frame

    if cv2.waitKey(1) & 0xFF == ord('q'): # if user press 'q', quit
        break

cap.release() # close the image
cv2.destroyAllWindows() # close windows
