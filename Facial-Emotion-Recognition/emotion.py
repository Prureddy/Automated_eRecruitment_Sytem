import cv2
from deepface import DeepFace
import numpy as np
from datetime import datetime

# Load the pre-trained emotion detection model
model = DeepFace.build_model("Emotion")

# Define emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(0)

# Initialize variables to keep track of the number of detected faces and turning angle
num_faces = 0

# Create VideoWriter object to record video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
record = False
out = None

# Warning messages list
warning_messages = []

def log_warning(message):
    # Log warning to a file
    with open('warning_log.txt', 'a') as file:
        file.write(f"{datetime.now()} - {message}\n")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize the frame to reduce GUI size
    frame = cv2.resize(frame, (400, 300))

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Check if no face is detected
    if len(faces) == 0:
        num_faces = 0
        message = "Error: Face not detected"
        cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        warning_messages.append(message)
        log_warning(message)
    elif len(faces) > 1:
        num_faces = len(faces)
        message = "Error: More than one person detected"
        cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        warning_messages.append(message)
        log_warning(message)
    else:
        num_faces = 1
        (x, y, w, h) = faces[0]

        # Calculate the width of the face for horizontal pose detection
        face_width = w

        # Adjust the threshold as needed
        width_threshold = 80

        # Check if the face width is below the threshold
        if face_width < width_threshold:
            message = "Error: Turn head to face the camera"
            cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)
            warning_messages.append(message)
            log_warning(message)

    for (x, y, w, h) in faces:
        # Extract the face ROI (Region of Interest)
        face_roi = gray_frame[y:y + h, x:x + w]

        # Resize the face ROI to match the input shape of the model
        resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)

        # Normalize the resized face image
        normalized_face = resized_face / 255.0

        # Reshape the image to match the input shape of the model
        reshaped_face = normalized_face.reshape(1, 48, 48, 1)

        # Predict emotions using the pre-trained model
        preds = model.predict(reshaped_face)[0]
        emotion_idx = preds.argmax()
        emotion = emotion_labels[emotion_idx]

        # Draw rectangle around face and label with predicted emotion
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Display the resulting frame
    height, width, _ = frame.shape
    cv2.imshow('', frame)

    # Record video option
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        record = not record
        if record:
            # Start recording
            out = cv2.VideoWriter(f"recorded_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.avi", fourcc, 20.0, (width, height))
        else:
            # Stop recording
            if out is not None:
                out.release()
                print("Video recording stopped.")

    # Press 'q' to exit
    elif key == ord('q'):
        break

    # Record video frames if recording is active
    if record and out is not None:
        out.write(frame)

# Release the capture, close all windows, and release the recording output
cap.release()
cv2.destroyAllWindows()
if out is not None:
    out.release()

# Display warning messages
print("\nWarning Messages:")
for message in warning_messages:
 print(message)
