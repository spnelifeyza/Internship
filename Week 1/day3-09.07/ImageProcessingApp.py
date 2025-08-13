import cv2
import numpy as np

# -------------------- Class: Canny Edge Detection --------------------
class CannyEdgeDetector:
    def __init__(self, size=(300, 400)):  # Set default output frame size
        self.size = size  # Store the size as an instance variable

    def run(self, frame):
        frame = cv2.resize(frame, self.size)  # Resize input frame to standard size
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
        blur = cv2.GaussianBlur(gray, (5, 5), 0)  # Apply Gaussian blur to reduce noise
        edges = cv2.Canny(blur, 15, 100)  # Perform Canny edge detection
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # Convert result to BGR for text overlay
        cv2.putText(edges_bgr, "Canny", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)  # Add label
        return edges_bgr  # Return processed frame

# -------------------- Class: Threshold Comparison --------------------
class ThresholdComparison:
    def __init__(self, size=(800, 600)):  # Set output frame size
        self.size = size  # Save the size

    def run(self, frame):
        frame = cv2.resize(frame, self.size)  # Resize input frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

        # Apply binary thresholding (global)
        _, binary = cv2.threshold(gray, 107, 255, cv2.THRESH_BINARY)

        # Apply adaptive mean thresholding
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, 5, 2)

        # Convert both binary outputs to BGR format for display
        binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        adaptive_bgr = cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)

        # Resize each result to half width of the output size
        binary_bgr = cv2.resize(binary_bgr, (self.size[0] // 2, self.size[1]))
        adaptive_bgr = cv2.resize(adaptive_bgr, (self.size[0] // 2, self.size[1]))

        # Add labels to each image
        cv2.putText(binary_bgr, "Binary", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
        cv2.putText(adaptive_bgr, "Adaptive", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

        # Combine both thresholded images side-by-side
        combined = np.hstack((binary_bgr, adaptive_bgr))
        combined = cv2.resize(combined, self.size)  # Resize to desired output
        return combined

# -------------------- Class: Blur Comparison --------------------
class BlurComparison:
    def __init__(self, size=(1000, 700)):  # Define the default display size
        self.size = size  # Store the size for resizing later

    def run(self, frame):
        frame = cv2.resize(frame, self.size)  # Resize input to standard size

        # Apply Median Blur - useful for removing salt-and-pepper noise
        median = cv2.medianBlur(frame, 5)

        # Apply Gaussian Blur - uses a Gaussian kernel for smoothing
        gaussian = cv2.GaussianBlur(frame, (5, 5), 0)

        # Apply Bilateral Filter - smooths image while preserving edges
        bilateral = cv2.bilateralFilter(frame, 9, 75, 75)

        # Get dimensions for dynamic text positioning
        height, width, _ = frame.shape
        third_width = width // 3  # Divide image width into thirds
        text_y = int(height * 0.1)  # Y position: 10% from top
        font_scale = 2.0  # Font size
        thickness = 5  # Text thickness

        # Add labels to each image
        cv2.putText(median, "Median", (int(third_width * 0.2), text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        cv2.putText(gaussian, "Gaussian", (int(third_width * 0.2), text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        cv2.putText(bilateral, "Bilateral", (int(third_width * 0.2), text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        # Combine all three images horizontally
        combined = np.hstack((median, gaussian, bilateral))
        combined = cv2.resize(combined, self.size)  # Resize to final output size
        return combined  # Return result

# -------------------- Class: Erode & Dilate --------------------
class ErodeDilate:
    def __init__(self, size=(900, 700)):  # Set output size
        self.size = size

    def run(self, frame):
        frame = cv2.resize(frame, self.size)  # Resize input
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        kernel = np.ones((5, 5), np.uint8)  # Create 5x5 kernel

        # Apply erosion and dilation
        eroded = cv2.erode(gray, kernel)
        dilated = cv2.dilate(gray, kernel)

        # Convert to BGR for text overlay
        eroded_bgr = cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR)
        dilated_bgr = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)

        # Add labels with larger font size
        cv2.putText(eroded_bgr, "Erode", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4)
        cv2.putText(dilated_bgr, "Dilate", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4)

        combined = np.hstack((eroded_bgr, dilated_bgr))  # Combine both images side-by-side
        combined = cv2.resize(combined, self.size)  # Resize to match display
        return combined

# -------------------- Class: Opening & Closing --------------------
class OpeningClosing:
    def __init__(self, size=(900, 600)):  # Set the default output size
        self.size = size

    def run(self, frame):
        frame = cv2.resize(frame, self.size)  # Resize the input frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale

        # Apply binary threshold to prepare for morphological operations
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Define morphological kernel

        # Apply morphological opening and closing
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Convert all results to BGR for visualization
        opening_bgr = cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        closing_bgr = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)

        # Resize each section to 1/3 of final output width
        opening_bgr = cv2.resize(opening_bgr, (self.size[0] // 3, self.size[1]))
        gray_bgr = cv2.resize(gray_bgr, (self.size[0] // 3, self.size[1]))
        closing_bgr = cv2.resize(closing_bgr, (self.size[0] // 3, self.size[1]))

        # Add labels
        cv2.putText(opening_bgr, "Opening", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
        cv2.putText(gray_bgr, "Gray", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
        cv2.putText(closing_bgr, "Closing", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

        combined = np.hstack((opening_bgr, gray_bgr, closing_bgr))  # Stack all images
        combined = cv2.resize(combined, self.size)  # Resize to final output
        return combined  # Return the combined result
