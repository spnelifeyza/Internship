import cv2
import time
from datetime import datetime
from ImageProcessingApp import (
    CannyEdgeDetector,
    ThresholdComparison,
    BlurComparison,
    ErodeDilate,
    OpeningClosing
)

# -------------------- Main Application Loop --------------------
if __name__ == "__main__":
    print("\n--- Image Processing Application ---")
    print("Press 0: Normal Camera View")
    print("Press 1: Canny Edge Detection")
    print("Press 2: Binary vs Adaptive Thresholding")
    print("Press 3: Blur Comparison (Median, Gaussian, Bilateral)")
    print("Press 4: Erosion & Dilation")
    print("Press 5: Opening & Closing")
    print("Press q: Quit")

    cap = cv2.VideoCapture(0)  # Start capturing video from webcam
    current_mode = 0  # Default to normal camera view

    # Create instances of all processor classes with custom sizes
    processors = {
        1: CannyEdgeDetector(size=(300, 400)),
        2: ThresholdComparison(size=(800, 600)),
        3: BlurComparison(size=(1200, 700)),
        4: ErodeDilate(size=(900, 700)),
        5: OpeningClosing(size=(900, 600))
    }

    prev = time.time()
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # width
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # height


    while True:
        ret, frame = cap.read()  # Read a frame from the webcam
        if not ret:
            break  # Exit if frame is not captured correctly

        key = cv2.waitKey(1) & 0xFF  # Wait for key press

        if key == ord('q'):  # Quit the application
            break
        elif key in [ord(str(i)) for i in range(6)]:
            current_mode = int(chr(key))  # Update processing mode

        # Switch processing mode
        match current_mode:
            case 1:
                output = processors[1].run(frame)
            case 2:
                output = processors[2].run(frame)
            case 3:
                output = processors[3].run(frame)
            case 4:
                output = processors[4].run(frame)
            case 5:
                output = processors[5].run(frame)
            case _:
                output = frame  # Default: show original frame

        # Calculate FPS
        current = time.time()  # float type
        fps = 1 / (current - prev)
        prev = current

        # Get current time
        now = datetime.now()  # datetime object type
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Display info on the frame
        cv2.putText(output, f"FPS: {fps:.2f}", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,125,0), 1)
        cv2.putText(output, f"Resolution: {int(width)}x{int(height)}", (20, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0,125,0), 1)
        cv2.putText(output, current_time, (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,125,0), 1)
        cv2.imshow("Image Processing Application", output)  # Display the processed frame

    cap.release()  # Release the camera
    cv2.destroyAllWindows()  # Close all OpenCV windows