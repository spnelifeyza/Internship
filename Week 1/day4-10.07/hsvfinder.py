import cv2
import numpy as np

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv = param['hsv']
        pixel = hsv[y, x]
        print(f"HSV at ({x},{y}): H={pixel[0]} S={pixel[1]} V={pixel[2]}")

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow("Click to get HSV", frame)

        # HSV verisini mouse fonksiyonuna veriyoruz
        cv2.setMouseCallback("Click to get HSV", mouse_callback, {'hsv': hsv})

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
