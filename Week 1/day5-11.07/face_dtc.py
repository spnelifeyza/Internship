import cv2
import time

class FaceDetection:
    def __init__(self, counter=1):
        """
        Initialize face and eye detectors, counters, timer, and sticker resources.
        """

        # Load pre-trained Haar Cascade classifiers for face and eye detection
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier("haarcascade_eye_tree_eyeglasses.xml")

        # Counter for saving multiple images (manual save mode)
        self.counter = counter

        # Record the timestamp when the program starts
        self.start_time = time.time()

        # Boolean to ensure auto-saving happens only once
        self.saved_once = False

        # Mode selector: 0 = normal, 1/2/3 = different stickers
        self.sticker_mode = 0

        # Load emoji stickers with alpha transparency (RGBA)
        self.stickers = {
            1: cv2.imread("emojis/smile.png", cv2.IMREAD_UNCHANGED),
            2: cv2.imread("emojis/flat.png", cv2.IMREAD_UNCHANGED),
            3: cv2.imread("emojis/sad.png", cv2.IMREAD_UNCHANGED)
        }

    def detect_faces_and_eyes(self, gray, original, frame):
        """
        Detect faces and eyes in the frame. Draw rectangles or apply stickers.
        Automatically saves a photo once, 6 seconds after the program starts.
        """

        # Detect faces in the grayscale frame
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=6, minSize=(100,100))

        # Proceed only if at least one face is detected
        if len(faces) > 0:

            # After 6 seconds from program start, save the first face image (once)
            if not self.saved_once and (time.time() - self.start_time >= 6):
                cv2.imwrite("face_dtc1.jpg", original)
                self.saved_once = True

            for (x, y, w, h) in faces:
                if self.sticker_mode == 0:
                    # Rectangle mode — draw rectangle around face and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 130), 3)
                    cv2.putText(frame, "Face", (x + w - 60, y + 20),
                                cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 130), 3)

                    # Define face region of interest (ROI) for eye detection
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]

                    # Detect eyes inside the face region
                    eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15,15), maxSize=(80,80))

                    for (ex, ey, ew, eh) in eyes:
                        # Draw rectangles around eyes
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 125, 0), 2)
                        cv2.putText(roi_color, "Eye", (ex + ew - 70, ey + 20),
                                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 125, 0), 2)

                else:
                    # Sticker mode is active — get selected sticker
                    sticker = self.stickers[self.sticker_mode]

                    # Resize sticker larger than face (covers whole head)
                    resized = cv2.resize(sticker, (int(w * 1.4), int(h * 1.6)))

                    # Offset sticker position slightly upward and centered
                    offset_x = int(x - w * 0.2)
                    offset_y = int(y - h * 0.4)

                    # Apply sticker onto original frame
                    original = self.overlay_transparent(original, resized, offset_x, offset_y)

    @staticmethod
    def overlay_transparent(original, resized, x, y):
        """
        Overlays a transparent sticker image onto the original frame at position (x, y).
        Handles boundaries and alpha blending.
        """
        original_h, original_w = original.shape[:2]
        sticker_h, sticker_w = resized.shape[:2]

        # Handle negative X (left of screen)
        if x < 0:
            resized = resized[:, -x:]        # Remove left portion
            sticker_w = resized.shape[1]     # Update width
            x = 0

        # Handle negative Y (above screen)
        if y < 0:
            resized = resized[-y:, :]        # Remove top portion
            sticker_h = resized.shape[0]     # Update height
            y = 0

        # If completely out of bounds, do nothing
        if x >= original_w or y >= original_h:
            return original

        # Crop sticker if it goes beyond the right or bottom edge
        if x + sticker_w > original_w:
            sticker_w = original_w - x
            resized = resized[:, :sticker_w]

        if y + sticker_h > original_h:
            sticker_h = original_h - y
            resized = resized[:sticker_h]

        # Split RGB and Alpha channels from the sticker
        sticker_rgb = resized[:, :, :3]              # Color
        alpha_mask = resized[:, :, 3:] / 255.0       # Transparency (0.0–1.0)

        # Blend the sticker over the region using alpha mask
        original[y:y + sticker_h, x:x + sticker_w] = (
            (1.0 - alpha_mask) * original[y:y + sticker_h, x:x + sticker_w] +
            alpha_mask * sticker_rgb
        )

        return original

    def save_image(self, key, original):
        """
        Manually saves the current frame when 's' key is pressed.
        """
        if key == ord('s'):
            self.counter += 1
            cv2.imwrite(f"face_dtc{self.counter}.jpg", original)

    def run(self):
        """
        Main loop: opens webcam, processes each frame, shows results,
        and handles keyboard input for controls.
        """
        # Open default camera (index 0)
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # Stop if camera fails

            # Convert frame to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Keep a copy of the original frame (for overlay)
            original = frame.copy()

            # Perform face and eye detection
            self.detect_faces_and_eyes(gray, original, frame)

            # Show the processed frame (with rectangles or sticker)
            cv2.imshow("Face and Eye Detection", original if self.sticker_mode != 0 else frame)

            # Wait for key press
            key = cv2.waitKey(1) & 0xFF

            # Handle key input
            match chr(key):
                case '0':
                    self.sticker_mode = 0  # Turn off sticker
                case '1':
                    self.sticker_mode = 1  # Use smile sticker
                case '2':
                    self.sticker_mode = 2  # Use flat face sticker
                case '3':
                    self.sticker_mode = 3  # Use sad face sticker
                case 's':
                    self.save_image(key, original)  # Manual image save
                case 'q':
                    break  # Quit the program
                case _:
                    continue  # Ignore other keys

        # Clean up resources
        cap.release()
        cv2.destroyAllWindows()
