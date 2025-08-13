import cv2
import numpy as np


class ShapeDetector:
    def __init__(self):
        self.lower = np.array([100, 150, 50])  # Lower HSV bound for blue
        self.upper = np.array([140, 255, 255])  # Upper HSV bound for blue

    # Converts the captured frame to HSV color space, applies a mask for blue color,
    # and returns the masked result with Gaussian blur applied
    def converting_operations(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert from BGR to HSV
        mask = cv2.inRange(hsv, self.lower, self.upper)  # Create mask for pixels within blue range
        result = cv2.bitwise_and(frame, frame, mask=mask)  # Apply the mask to keep only blue regions

        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)  # Convert result to grayscale
        gaussian = cv2.GaussianBlur(gray, (15, 15), 5)  # Apply Gaussian blur to reduce noise

        return mask, result, gaussian

    # Detects the largest contour in the mask and marks it on the frame
    @staticmethod
    def detect_contours(mask, frame):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find external contours
        if contours:
            biggest = max(contours, key=cv2.contourArea)  # Find contour with the largest area
            cv2.drawContours(frame, [biggest], -1, (0, 255, 0), 2)  # Draw the largest contour in green

            area = cv2.contourArea(biggest)  # Calculate area of the contour
            M = cv2.moments(biggest)  # Calculate image moments for centroid

            if M["m00"] != 0:  # Avoid division by zero
                cx = int(M["m10"] / M["m00"])  # X coordinate of centroid
                cy = int(M["m01"] / M["m00"])  # Y coordinate of centroid

                # Display area and mark center with red dot
                cv2.putText(frame, f"Area: {int(area)}", (cx - 50, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    # Detects shapes in the image including circles and polygons, returns the largest area found
    @staticmethod
    def detect_shapes(mask, frame, gaussian):
        max_area = 0  # Initialize variable to track the largest shape area

        # Try to detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            gaussian, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
            param1=50, param2=20, minRadius=5, maxRadius=80
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))  # Round and convert to uint16
            for i in circles[0, :]:
                x = int(i[0])  # Circle center x
                y = int(i[1])  # Circle center y
                r = int(i[2])  # Radius
                area = np.pi * r * r  # Calculate area of the circle
                max_area = max(max_area, area)

                # Draw circle and label it
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.putText(frame, "Circle", (x - 30, y - r - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # If no circles, detect polygonal shapes
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 200:  # Ignore small noise
                    continue

                max_area = max(max_area, area)  # Track the largest area

                approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)  # Approximate shape
                x, y, w, h = cv2.boundingRect(approx)  # Bounding box

                # Determine shape type based on number of sides
                match len(approx):
                    case 3:
                        shape = "Triangle"
                        color = (0, 0, 255)  # Red
                    case 4:
                        oran = w / float(h)
                        if 0.95 < oran < 1.05:
                            shape = "Square"
                            color = (255, 0, 0)  # Blue
                        else:
                            shape = "Rectangle"
                            color = (0, 255, 0)  # Green
                    case _:
                        shape = "Unknown"
                        color = (255, 255, 255)  # White

                # Draw shape and label it
                cv2.drawContours(frame, [approx], -1, color, 2)
                cv2.putText(frame, shape, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return max_area  # Return the largest area found

    # Draws general text on both result and frame, including the largest area detected
    @staticmethod
    def write_text(result, frame, biggest_area):
        cv2.putText(result, "Detecting blue in HSV color space", (20, 40),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Frame", (20, 40),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Biggest Area: {int(biggest_area)}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def run(self):
        cap = cv2.VideoCapture(0)  # Start webcam

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # If frame not read, break loop

            # Function calls
            mask, result, gaussian = self.converting_operations(frame)
            biggest_area = self.detect_shapes(mask, frame, gaussian)
            self.detect_contours(mask, frame)
            self.write_text(result, frame, biggest_area)

            combined = np.hstack([frame, result])
            cv2.imshow("Combined", combined)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release camera and close all windows
        cap.release()
        cv2.destroyAllWindows()

