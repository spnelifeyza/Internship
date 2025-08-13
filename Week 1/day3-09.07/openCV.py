import cv2
import time
from datetime import datetime

cap = cv2.VideoCapture(0) # take image from cam
prev = time.time()

# get resolution
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH) # width
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # height

filter_mode = '0'      # start with original (no filter)
gray_mode = False      # grayscale mode toggle

while True:
    ret, frame = cap.read()
    # cam is open -> ret:True
    # frame: image taken from cam

    if not ret: # if ret is False
        break

    # waits for a key press from the keyboard for a short time and captures which key was pressed
    key = cv2.waitKey(1) & 0xFF # 0XFF -> min 8-bit

    # Calculate FPS
    current = time.time() # float type
    fps = 1 / (current - prev)
    prev = current

    # Get current time
    now = datetime.now() # datetime object type
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    text_color = (0, 100, 0)
    # Apply filter based on filter_mode
    filtered_frame = frame.copy() # over copy to save main frame
    if filter_mode == '1':
        filtered_frame = cv2.GaussianBlur(filtered_frame, (15, 15), 0)
    elif filter_mode == '2':
        filtered_frame = cv2.Canny(filtered_frame, 100, 200)
        text_color = (255, 255, 255)
    elif filter_mode == '3':
        filtered_frame = cv2.bitwise_not(filtered_frame)
    elif filter_mode == '4':
        filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2HSV)

    if gray_mode and filter_mode not in ['2', '4']:
        filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
        text_color = (0, 0, 0)


    # Display info on the frame
    cv2.putText(filtered_frame, f"FPS: {fps:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1)
    cv2.putText(filtered_frame, f"Resolution: {int(width)}x{int(height)}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1)
    cv2.putText(filtered_frame, current_time, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1)
    cv2.putText(filtered_frame, f"Filter: {filter_mode}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1)

    # Show the frame
    cv2.imshow('Camera', filtered_frame)

    # Key controls
    match chr(key):
        case '0':
            filter_mode = '0'
        case '1':
            filter_mode = '1'
        case '2':
            filter_mode = '2'
        case '3':
            filter_mode = '3'
        case '4':
            filter_mode = '4'
        case 'g':
            gray_mode = not gray_mode
        case 'q':
            break
        case _:
            pass

cap.release()
cv2.destroyAllWindows()
