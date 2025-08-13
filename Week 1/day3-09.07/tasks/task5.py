# canny edge detection
import cv2
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0) # open the default camera (webcam)

# last_frame = None

while True:
    ret,frame = cap.read() # read the image
    # if image is read correctly -> ret:True

    if not ret: # if ret:False
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to gray
    blur = cv2.GaussianBlur(gray, (5,5), 0) # blur effect
    # (5,5) -> kernel sizes must be odd numbers

    # apply canny
    canny = cv2.Canny(blur, 15, 100)

    # last_frame = frame.copy()

    cv2.imshow('Cam', canny) # show image

    if cv2.waitKey(1) & 0XFF == ord('q'): # if user press 'q', exit the program
        break

cap.release() # close the image
cv2.destroyAllWindows() # close windows

# histogram grafiği alarak piksel yoğunluklarının bulunduğu yere göre
# blurlama işleminin eşik değerlerini tekrardan düzenledim
# if last_frame is not None:
#     row_values = last_frame[:, :]
#
#     plt.hist(gray.ravel(), bins=256, range=[0,256])
#     plt.title("Gray Image Pixel Histogram")
#     plt.xlabel("Pixel Value (0-255)")
#     plt.ylabel("Frekans")
#     plt.grid()
#     plt.show()