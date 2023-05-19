import numpy as np
import cv2

def initialize_hog_descriptor():
    hog = cv2.HOGDescriptor()
    default_detector = cv2.HOGDescriptor_getDefaultPeopleDetector()
    hog.setSVMDetector(default_detector)
    return hog, default_detector

def initialize_video_capture():
    cap = cv2.VideoCapture(0)
    return cap

def initialize_video_writer():
    out = cv2.VideoWriter(
        'output.avi',
        cv2.VideoWriter_fourcc(*'MJPG'),
        30.,
        (720, 480)
    )
    return out

def get_text_position(frame, box):
    x, _, w, _ = box
    frame_width = frame.shape[1]
    center = frame_width // 2
    quarter = center // 2
    text_position = "MIDDLE"

    if x < center - 50:
        text_position = "LEFT"
        frame[:, quarter-5:quarter+5] = (0, 0, 255)  # Red overlay on the left side
    elif x > center + 50:
        text_position = "RIGHT"
        frame[:, quarter-5+center:quarter+5+center] = (255, 0, 0)  # Blue overlay on the right side
    else:
        frame[:, center-5:center+5] = (0, 255, 0)  # Green overlay in the middle

    return text_position

def detect_and_track_people(hog, default_detector, cap, out):
    tracker = None
    tracking_started = False
    previous_box = None
    confidence = 0.0
    use_full_body_detection = True

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (720, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        if not tracking_started:
            boxes, weights = hog.detectMultiScale(
                gray, winStride=(8, 8), padding=(8, 8), scale=1.05)
            
            if len(boxes) > 0:
                x, y, w, h = boxes[0]
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, (x, y, w, h))
                tracking_started = True
                previous_box = (x, y, w, h)
                confidence = 1.0

        else:
            success, box = tracker.update(frame)

            if success:
                x, y, w, h = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text_position = get_text_position(frame, box)
                text_org = (int(frame.shape[1] / 2) - 30, int(frame.shape[0] / 2))
                cv2.putText(frame, text_position, text_org, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                dx = abs(x - previous_box[0]) / frame.shape[1]
                dy = abs(y - previous_box[1]) / frame.shape[0]
                confidence -= (dx + dy) / 2
                confidence = max(confidence, 0.0)
                previous_box = (x, y, w, h)
            else:
                tracking_started = False

        out.write(frame.astype('uint8'))
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(1) & 0xFF == ord('u'):
            use_full_body_detection = not use_full_body_detection

            if use_full_body_detection:
                hog.setSVMDetector(default_detector)
            else:
                hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

def main():
    hog, default_detector = initialize_hog_descriptor()
    cap = initialize_video_capture()
    out = initialize_video_writer()
    detect_and_track_people(hog, default_detector, cap, out)

if __name__ == '__main__':
    main()
