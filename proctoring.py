import cv2
import time
import requests

def start_proctoring(participant_id, server_url):
    """
    Optional standalone proctoring module using OpenCV.
    In a real-world local app, this would run in a separate thread or process.
    """
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Webcam not accessible.")
        return

    last_log_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        event = None
        if len(faces) == 0:
            event = "no_face_detected"
        elif len(faces) > 1:
            event = "multiple_faces_detected"
            
        # Log event to server every 5 seconds if detected
        if event and (time.time() - last_log_time > 5):
            try:
                requests.post(f"{server_url}/api/cheating_log", 
                              json={"participant_id": participant_id, "event_type": event})
                last_log_time = time.time()
                print(f"Proctoring Alert: {event}")
            except Exception as e:
                print(f"Failed to log proctoring event: {e}")

        # Display for local debugging
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('Proctoring Active', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example usage: python proctoring.py <participant_id>
    import sys
    if len(sys.argv) > 1:
        start_proctoring(sys.argv[1], "http://127.0.0.1:5000")
    else:
        print("Please provide participant ID")
