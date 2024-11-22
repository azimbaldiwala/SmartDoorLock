import cv2
import face_recognition
import numpy as np
import os
import time
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import model_from_json

# Load Face Detection Model for Liveness
face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")

# Load Anti-Spoofing Model
json_file = open('antispoofing_models/antispoofing_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
liveness_model = model_from_json(loaded_model_json)
liveness_model.load_weights('antispoofing_models/antispoofing_model.h5')
print("Liveness Model loaded from disk")

# Load Registered Faces
REGISTERED_FACES_DIR = 'registered_faces'
if not os.path.exists(REGISTERED_FACES_DIR):
    os.makedirs(REGISTERED_FACES_DIR)

def load_registered_faces():
    registered_faces = {}
    for file_name in os.listdir(REGISTERED_FACES_DIR):
        if file_name.endswith('.npy'):
            person_name = os.path.splitext(file_name)[0]
            face_encoding = np.load(os.path.join(REGISTERED_FACES_DIR, file_name))
            registered_faces[person_name] = face_encoding
    return registered_faces

registered_faces = load_registered_faces()

# Recognition and Liveness Checking in Video
video = cv2.VideoCapture(0)
while True:
    ret, frame = video.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        face = frame[y-5:y+h+5, x-5:x+w+5]
        resized_face = cv2.resize(face, (160, 160))
        resized_face = resized_face.astype("float") / 255.0
        resized_face = np.expand_dims(resized_face, axis=0)
        
        # Predict liveness
        preds = liveness_model.predict(resized_face)[0]
        if preds > 0.5:
            label = 'spoof'
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        else:
            label = 'real'
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Proceed with face recognition if liveness is real
            rgb_frame = frame[:, :, ::-1]  # Convert from BGR to RGB
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(list(registered_faces.values()), face_encoding)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = list(registered_faces.keys())[first_match_index]
                
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)
                
                if name != "Unknown":
                    print("Door Unlocked!")
                    cv2.putText(frame, "Door Unlock", (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)
                    # Exit after successful recognition
                    video.release()
                    cv2.destroyAllWindows()
                    exit()

    cv2.imshow('Liveness and Face Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
