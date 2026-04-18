import cv2
import mediapipe as mp
import winsound
import time
import threading
import tkinter as tk

# Some GLOBAL VARIABLES -
running = False
closed_start_time = None

# MEDIAPIPE SETUP -
mp_mesh = mp.solutions.face_mesh
mesh = mp_mesh.FaceMesh()

LEFT_EYE = [33, 160, 158, 133, 153, 144]

# Eye's Data
def eye_ratio(landmarks, eye):
    y1 = landmarks[eye[1]].y
    y2 = landmarks[eye[5]].y

    x1 = landmarks[eye[0]].x
    x2 = landmarks[eye[3]].x

    return abs(y1 - y2) / abs(x1 - x2)

# For opening Camera
def run_camera():
    global running, closed_start_time

    cam = cv2.VideoCapture(0)

    start_time = time.time()
    last_alarm_time = start_time

    while running:
        time.sleep(0.01)
        current_time = time.time()

        if current_time - last_alarm_time >= 300:
            print("30 minuts completed! Please take water.")
            winsound.Beep(2000, 3000)
            last_alarm_time = current_time

        ret, frame = cam.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = mesh.process(rgb)

        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                ratio = eye_ratio(landmarks, LEFT_EYE)

                if ratio < 0.20:
                    text = "Eyes Closed"
                    color = (0, 0, 255)

                    if closed_start_time is None:
                        closed_start_time = time.time()

                    cl_time = time.time() - closed_start_time

                    if cl_time > 2:
                        winsound.Beep(1000, 2000)

                else:
                    text = "Eyes Open"
                    color = (0, 255, 0)
                    closed_start_time = None

                cv2.putText(frame, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Eye Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    end_time = time.time()
    t = (end_time - start_time) / 60
    print(f"Total running time: {t:.2f} minutes")

# Buttons-
def start():
    global running

    l1 = tk.Label(root, text="Please Wait...",font=("Arial Black", 15), fg="black", bg="yellow")
    l1.pack(pady=20)
    root.after(8000, l1.destroy)

    if not running:
        running = True
        camera_thread = threading.Thread(target=run_camera, daemon=True)
        camera_thread.start()


def stop():
    global running

    l2 = tk.Label(root, text="Thank you...",font=("Arial Black", 15), fg="black", bg="yellow")
    l2.pack(pady=20)
    root.after(3000, l2.destroy)
    running = False


# For window GUI
root = tk.Tk()
root.title("Smart Eye Monitoring System")
root.geometry("450x270")
root.config(bg="yellow")
title = tk.Label(root, text="Smart Eye Moniter",
                 font=("Algerian", 25, "bold"),fg="blue",bg="yellow")
title.pack(pady=20)

str_b1 = tk.Button(root, text="Start", command=start,
                      width=10,font=("Arial", 16, "bold"), bg="green", fg="white")
str_b1.pack(pady=10)

str_b2 = tk.Button(root, text="Stop", command=stop,
                     width=10,font=("Arial", 16, "bold"), bg="red", fg="white")
str_b2.pack(pady=10)

root.mainloop()