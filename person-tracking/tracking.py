import numpy as np
import cv2

# Initialize the HOG descriptor
hog = cv2.HOGDescriptor()

# Set the default people detector as the initial detector
default_detector = cv2.HOGDescriptor_getDefaultPeopleDetector()
current_detector = default_detector
hog.setSVMDetector(current_detector)

# Open webcam video stream
cap = cv2.VideoCapture(0)

# The output will be written to output.avi
out = cv2.VideoWriter(
    'output.avi',
    cv2.VideoWriter_fourcc(*'MJPG'),
    15.,
    (640, 480))

# Initialize variables for object tracking
tracker = None
tracking_started = False
previous_box = None
confidence = 0.0

# Toggle variable to switch between full body and upper body detection
use_full_body_detection = False

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Resize the frame for faster processing
    frame = cv2.resize(frame, (640, 480))

    # Using a grayscale picture for faster detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    if not tracking_started:
        # Detect bodies in the image and get bounding boxes
        # Returns the bounding boxes for the detected objects
        boxes, weights = hog.detectMultiScale(
            frame, winStride=(8, 8), padding=(8, 8), scale=1.05)

        if len(boxes) > 0:
            # Select the first detected box for tracking
            x, y, w, h = boxes[0]
            tracker = cv2.TrackerKCF_create()
            tracker.init(frame, (x, y, w, h))
            tracking_started = True
            previous_box = (x, y, w, h)
            confidence = 1.0

    else:
        # Update the tracker
        success, box = tracker.update(frame)

        if success:
            # Tracking successful
            x, y, w, h = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calculate the displacement of the tracked object
            dx = abs(x - previous_box[0]) / frame.shape[1]
            dy = abs(y - previous_box[1]) / frame.shape[0]

            # Update the confidence based on the displacement
            confidence -= (dx + dy) / 2
            confidence = max(confidence, 0.0)

            # Update the previous box
            previous_box = (x, y, w, h)

            # Display the confidence level on the bounding box
            text = f'W: {confidence:.2f}'
            text_width, text_height = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            cv2.putText(frame, text, (x, y - text_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            # Tracking lost, re-detect the body
            tracking_started = False

    # Write the output video
    out.write(frame.astype('uint8'))

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # If 'q' is pressed, break the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Toggle between full body and upper body detection when 'u' is pressed
    if cv2.waitKey(1) & 0xFF == ord('u'):
        use_full_body_detection = not use_full_body_detection

        if use_full_body_detection:
            current_detector = default_detector
        else:
            current_detector = cv2.HOGDescriptor_getDaimlerPeopleDetector()

        hog.setSVMDetector(current_detector)

# When everything is done, release the capture
cap.release()
# Release the output
out.release()
# Close the windows
cv2.destroyAllWindows()
cv2.waitKey(1)
