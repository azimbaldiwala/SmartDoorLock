import face_recognition
import cv2
import numpy as np
import os
import time 





# Directory to store registered faces
REGISTERED_FACES_DIR = 'registered_faces'

# Ensure the directory exists
if not os.path.exists(REGISTERED_FACES_DIR):
    os.makedirs(REGISTERED_FACES_DIR)

def register_faces_from_folder(folder_path):
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        person_name = os.path.splitext(image_name)[0]
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
       
        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]
            np.save(os.path.join(REGISTERED_FACES_DIR, f'{person_name}.npy'), face_encoding)
            print(f"Face registered for {person_name}")
        else:
            print(f"No face found in the image {image_name}.")

def load_registered_faces():
    registered_faces = {}
    for file_name in os.listdir(REGISTERED_FACES_DIR):
        if file_name.endswith('.npy'):
            person_name = os.path.splitext(file_name)[0]
            face_encoding = np.load(os.path.join(REGISTERED_FACES_DIR, file_name))
            registered_faces[person_name] = face_encoding
    return registered_faces

def recognize_faces(frame, registered_faces):
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
            # Exit loop .. 
            exit()
            


def recognize_in_video(registered_faces):
    cap = cv2.VideoCapture(0)
    
    capture_frames = 5 
    i = 0 
    while i < capture_frames:
        ret, frame = cap.read()
        if not ret:
            break
       
        recognize_faces(frame, registered_faces)
       
        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.2)
        i += 1 
    cap.release()
    cv2.destroyAllWindows()

# Example usage
folder_path = 'photo_rec/'  # Path to the folder containing images for registration


#register_faces_from_folder(folder_path)
registered_faces = load_registered_faces()
recognize_in_video(registered_faces)  # Start face recognition in video# Register faces from the folder


