import cv2
import numpy as np

class ShapeDetector:
    def __init__(self):
        # Define HSV color ranges for Red, Green, and Blue.
        # Red has two ranges because it wraps around the hue values in HSV (0-180 in OpenCV).
        self.color_ranges = {
            "red": {
                "lower1": np.array([0, 100, 100]),
                "upper1": np.array([10, 255, 255]),
                "lower2": np.array([160, 100, 100]),
                "upper2": np.array([179, 255, 255])
            },
            "blue": {
                "lower": np.array([100, 150, 50]),
                "upper": np.array([140, 255, 255])
            },
            "green": {
                "lower": np.array([45, 50, 40]),
                "upper": np.array([75, 255, 160])
            }
        }

        # A mapping from hue values to readable color names
        self.color_name_map = {
            "Red": lambda h: 0 <= h <= 10 or 160 <= h <= 179,
            "Green": lambda h: 45 <= h <= 75,
            "Blue": lambda h: 100 <= h <= 140,
        }

    def get_color_name(self, hue):
        # Determine the color name from the hue value
        for name, condition in self.color_name_map.items():
            if condition(hue):
                return name
        return "Unknown"

    def converting_operations(self, frame):
        # Convert the BGR image to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        full_mask = None

        # Apply color masking for each color defined
        for color_name, bounds in self.color_ranges.items():
            if color_name == "red":
                # Red is split into two ranges due to HSV hue wrapping
                mask1 = cv2.inRange(hsv, bounds["lower1"], bounds["upper1"])
                mask2 = cv2.inRange(hsv, bounds["lower2"], bounds["upper2"])
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                # For green and blue, a single range is sufficient
                mask = cv2.inRange(hsv, bounds["lower"], bounds["upper"])

            # Combine all color masks into one
            full_mask = mask if full_mask is None else cv2.bitwise_or(full_mask, mask)

        # Apply the mask to the frame (bitwise AND)
        result = cv2.bitwise_and(frame, frame, mask=full_mask)

        # Convert the result to grayscale for further processing
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to smooth the image for shape detection
        gaussian = cv2.GaussianBlur(gray, (9, 9), 5)

        return full_mask, result, gaussian

    def detect_shapes(self, mask, frame, gaussian):
        max_area = 0  # Keep track of the largest shape found
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        shape_color_label = "Unknown"

        # --- Circle Detection using Hough Transform ---
        circles = cv2.HoughCircles(
            gaussian,              # Input image (should be grayscale and blurred)
            cv2.HOUGH_GRADIENT,    # Detection method
            dp=1.5,                # Inverse ratio of the accumulator resolution
            minDist=50,            # Minimum distance between detected centers
            param1=100,            # Higher threshold for Canny edge detector
            param2=40,             # Accumulator threshold (lower = more false positives)
            minRadius=20,          # Minimum radius to detect
            maxRadius=80           # Maximum radius to detect
        )

        # If any circles were found
        if circles is not None:
            circles = np.uint16(np.around(circles))  # Round the coordinates

            for i in circles[0, :]:
                x, y, r = int(i[0]), int(i[1]), int(i[2])
                area = np.pi * r * r
                hue = hsv[y, x][0]
                color_name = self.get_color_name(hue)
                conf = 90  # We assume high confidence if circle is found

                # Only show the circle if we are confident enough
                if conf >= 70:
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    cv2.putText(frame, f"Confidence: {conf}%", (x - 40, y - r - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                    # Track the largest shape
                    if area > max_area:
                        max_area = area
                        shape_color_label = f"{color_name} Circle"

        else:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 200:
                    continue  # Skip small objects

                # Approximate the shape's contour to reduce noise
                approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
                x, y, w, h = cv2.boundingRect(approx)
                cx, cy = x + w // 2, y + h // 2
                hue = hsv[cy, cx][0]
                color_name = self.get_color_name(hue)

                # Determine shape type by the number of corners
                match len(approx):
                    case 3:
                        shape = "Triangle"
                        conf = 85
                    case 4:
                        ratio = w / float(h)
                        shape = "Square" if 0.95 < ratio < 1.05 else "Rectangle"
                        conf = 90 if shape == "Square" else 80
                    case _:
                        continue  # Skip unknown shapes like polygons

                if conf >= 70:
                    cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Confidence: {conf}%", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                    if area > max_area:
                        max_area = area
                        shape_color_label = f"{color_name} {shape}"

        return max_area, shape_color_label

    @staticmethod
    def detect_contours(mask, frame):
        # Find external contours from the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Select the biggest contour by area
            biggest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(biggest)

            if area < 1000:
                return  # Ignore small areas

            M = cv2.moments(biggest)
            if M["m00"] == 0:
                return  # Avoid division by zero

            # Calculate the centroid of the shape
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw contour, center dot, and area label
            cv2.drawContours(frame, [biggest], -1, (255, 255, 0), 2)
            cv2.putText(frame, f"Area: {int(area)}", (cx - 50, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    @staticmethod
    def write_text(result, frame, biggest_area, shape_label):
        # Display top-left messages on both result and frame
        cv2.putText(result, "Detecting colors in HSV color space", (20, 40),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)


        # Include the biggest area and identified shape
        area_label = f"Biggest Area: {int(biggest_area)}"
        if shape_label != "Unknown":
            area_label += f" ({shape_label})"

        cv2.putText(frame, area_label, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def run(self):
        # Start the webcam
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame: mask -> result image -> blurred grayscale
            mask, result, gaussian = self.converting_operations(frame)

            # Detect shapes and get the largest area + label
            biggest_area, shape_color_label = self.detect_shapes(mask, frame, gaussian)

            # Draw contours of largest object
            self.detect_contours(mask, frame)

            # Write general information text on both images
            self.write_text(result, frame, biggest_area, shape_color_label)

            # Combine frame and result side by side for display
            combined = np.hstack([frame, result])
            cv2.imshow("Combined", combined)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
