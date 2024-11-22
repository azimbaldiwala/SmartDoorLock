import cv2
import face_recognition
import numpy as np
import os
import sqlite3
from datetime import datetime
from tensorflow.keras.models import model_from_json
from tkinter import Tk, Button, Entry, StringVar, Label, messagebox
import random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import sms


# Load Face Detection Model for Liveness
face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")

# Load Anti-Spoofing Model
json_file = open('antispoofing_models/antispoofing_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
liveness_model = model_from_json(loaded_model_json)
liveness_model.load_weights('antispoofing_models/antispoofing_model.h5')
print("Liveness Model loaded from disk")

# Load Registered Faces Directory
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

# Load initial registered faces
registered_faces = load_registered_faces()

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('access_control.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load RSA keys for encryption and decryption
def load_public_key():
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key

def load_private_key():
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key

# Encrypt and Decrypt PIN
def decrypt_pin(encrypted_pin):
    private_key = load_private_key()
    decrypted = private_key.decrypt(
        encrypted_pin,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()

# Log Access Attempts
def log_access_attempt(username, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("SELECT UID FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    uid = user["UID"] if user else None
    cursor.execute('''
        INSERT INTO access_control (UID, attempt_time, attempt_date, result)
        VALUES (?, ?, ?, ?)
    ''', (uid, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d"), result))
    conn.commit()
    conn.close()

# Verify User PIN
def verify_pin(username, entered_pin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pin FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        encrypted_pin = user['pin']
        decrypted_pin = decrypt_pin(encrypted_pin)
        return entered_pin == decrypted_pin
    return False

# Verify Access Permissions
def verify_access(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "User not found"

    if user["is_access_granted"] == 0:
        return False, "Access revoked"

    if user["is_24_hours"] == 1:
        return True, "24-hour access granted"

    current_time = datetime.now().time()
    access_start = datetime.strptime(user["access_start"], "%H:%M").time() if user["access_start"] else None
    access_end = datetime.strptime(user["access_end"], "%H:%M").time() if user["access_end"] else None

    if access_start and access_end:
        if access_start <= current_time <= access_end:
            return True, "Access granted within time range"
        else:
            return False, "Access denied - Outside allowed time range"

    return False, "No valid access time set"

# Virtual Keypad GUI for PIN Entry
def open_keypad(username):
    root = Tk()
    root.title("Enter PIN")
    root.geometry("300x400")
    entered_pin = StringVar()

    def on_enter_pin():
        if verify_pin(username, entered_pin.get()):
            messagebox.showinfo("Access Granted", "PIN verified. Door Unlocked!")
            sms.send_sms(f"Access Granted, PIN verified. Door Unlocked! by {username}", "+919574428910")
            log_access_attempt(username, "Success")
            root.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN.")
            sms.send_sms(f"Access Denied, Incorrect PIN by {username}", "+919574428910")
            log_access_attempt(username, "Failed - Incorrect PIN")
            entered_pin.set("")  # Clear PIN entry for retry
    
    Label(root, text="Enter PIN for Verification", font=("Arial", 14)).pack(pady=10)
    Entry(root, textvariable=entered_pin, show="*", font=("Arial", 18), width=8).pack(pady=10)

    buttons = list(range(10))
    random.shuffle(buttons)

    for i, num in enumerate(buttons):
        Button(root, text=str(num), font=("Arial", 18), width=5, height=2,
               command=lambda n=num: entered_pin.set(entered_pin.get() + str(n))
              ).place(x=80*(i % 3), y=100 + 60*(i // 3))
    
    Button(root, text="Enter", font=("Arial", 18), width=5, height=2, command=on_enter_pin).place(x=80, y=300)
    root.mainloop()

# Recognition and Liveness Checking in Video
video = cv2.VideoCapture(0)
checking = False  # Flag to start recognition on "a" press

while True:
    ret, frame = video.read()
    if not ret:
        break
    
    # Check for the "a" key to start recognition
    key = cv2.waitKey(1) & 0xFF
    if key == ord('a'):
        checking = True
        print("Motion Detected!")
        print("Starting recognition!")

    if checking:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        face_recognized = False
        for (x, y, w, h) in faces:
            face = frame[y-5:y+h+5, x-5:x+w+5]
            resized_face = cv2.resize(face, (160, 160))
            resized_face = resized_face.astype("float") / 255.0
            resized_face = np.expand_dims(resized_face, axis=0)
            
            # Predict liveness
            preds = liveness_model.predict(resized_face)[0]
            if preds > 0.5:
                log_access_attempt("Unknown", "Failed - Spoof detected")
                checking = False  # End this iteration for spoof detection
                break
            else:
                rgb_frame = frame[:, :, ::-1]  # Convert from BGR to RGB
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(list(registered_faces.values()), face_encoding)
                    name = "Unknown"
                    
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = list(registered_faces.keys())[first_match_index]
                        face_recognized = True

                    if name != "Unknown":
                        access_granted, access_message = verify_access(name)
                        if access_granted:
                            open_keypad(name)  # Open keypad for PIN entry
                        else:
                            log_access_attempt(name, f"Failed - {access_message}")
                            messagebox.showerror("Access Denied", access_message)
                        checking = False  # End this iteration
                        break

        if not face_recognized:
            log_access_attempt("Unknown", "Failed - Face not recognized")
            checking = False  # End this iteration for unrecognized face

        # Reload the registered faces directory after each check
        registered_faces = load_registered_faces()

    cv2.imshow('Liveness and Face Recognition', frame)
    
    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
