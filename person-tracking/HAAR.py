import cv2

def initialize_face_cascade():
    face_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')
    return face_cascade

def initialize_video_capture(cam_index):
    cap = cv2.VideoCapture(cam_index)
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
    x, y, w, h = box
    frame_width = frame.shape[1]
    center = frame_width // 2
    quarter = center // 2
    text_position = "MIDDLE"

    if x + w / 2 < center - 50:
        text_position = "LEFT"
        frame[:, quarter-5:quarter+5] = (0, 0, 255)  # Red overlay on the left side
        text_org = (x, y + h + 25)  # Adjust the y-coordinate to move the text lower
    elif x + w / 2 > center + 50:
        text_position = "RIGHT"
        frame[:, quarter-5+center:quarter+5+center] = (255, 0, 0)  # Blue overlay on the right side
        text_org = (x, y + h + 25)  # Adjust the y-coordinate to move the text lower
    else:
        frame[:, center-5:center+5] = (0, 255, 0)  # Green overlay in the middle
        text_org = (x, y + h + 25)  # Adjust the y-coordinate to move the text lower

    return text_position, text_org


def detect_and_track_people(face_cascade, cap, out):
    tracker = None
    tracking_started = False
    previous_box = None
    confidence = 0.0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (720, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not tracking_started:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                x, y, w, h = faces[0]
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
                text_position, text_org = get_text_position(frame, box)
                cv2.putText(frame, text_position, text_org, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                dx = abs(x - previous_box[0]) / frame.shape[1]
                dy = abs(y - previous_box[1]) / frame.shape[0]
                confidence -= (dx + dy) / 2
                confidence = max(confidence, 0.0)
                previous_box = (x, y, w, h)
            else:
                tracking_started = False

        out.write(frame)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def main():
    face_cascade = initialize_face_cascade()

    # Prompt for selecting the webcam
    print("Select a webcam (0, 1, 2, ...):")
    cam_index = int(input())

    cap = initialize_video_capture(cam_index)
    out = initialize_video_writer()
    detect_and_track_people(face_cascade, cap, out)

if __name__ == '__main__':
    main()
