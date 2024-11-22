
# IoT-Based Smart Lock for Enhanced Security

## Project Overview
This project is a novel IoT-based smart locking system designed with **two-factor authentication** to enhance security. The system utilizes **face recognition** and a **PIN code** for user authentication. 

When a user approaches, a motion sensor activates the camera to capture an image of the individual. This image, along with the user’s PIN, is used for authentication. If authentication is successful, the lock opens, and a notification is sent to the administrator. In case of unauthorized access, an alert is sent instead. 

### Key Features:
- **Two-Factor Authentication**:
  - Combines face recognition and PIN verification.
- **Face Liveness Detection**:
  - Ensures the captured image is from a live person and not a spoof.
- **Secure PIN Storage**:
  - PINs are encrypted and stored securely using **RSA encryption**.
- **Real-Time Notifications**:
  - Sends alerts for unauthorized access attempts.
- **Administrator Notifications**:
  - Keeps the administrator informed of access events.

---

## Tools & Technologies
- **Programming Language**: Python
- **Hardware**: Raspberry Pi
- **Encryption**: RSA for secure PIN storage and authentication
- **Other Components**:
  - Motion Sensor
  - Pi Camera

---

## Installation and Setup
1. Clone the repository or extract the project files.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Connect the Raspberry Pi hardware components (motion sensor, camera).
4. Update the configuration file with the necessary settings.

---

## Usage
1. The system activates when motion is detected.
2. The Pi camera captures an image of the user.
3. The image is processed using the face recognition algorithm.
4. The user enters their PIN, which is validated using RSA encryption.
5. Based on authentication:
   - **Authorized Users**: The lock opens, and a message is sent to the administrator.
   - **Unauthorized Users**: The system sends an alert.

---

## Future Enhancements
- Integration with cloud storage for scalable logging.
- Addition of fingerprint recognition as a third authentication factor.
- Voice-based authentication support.

---

## Authors
This project was developed as part of the **Nirma University Summer 2024 Program**, funded by Nirma University, Ahmedabad. For further queries, contact [your_email@example.com].
