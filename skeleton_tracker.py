import cv2
import mediapipe as mp

def generate_skeleton_feed():
    mp_pose = mp.solutions.pose
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)  # Open the webcam

    with mp_pose.Pose() as pose, mp_face_mesh.FaceMesh() as face_mesh:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False

            # Process pose and face
            pose_results = pose.process(frame)
            face_results = face_mesh.process(frame)

            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Draw skeleton
            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    pose_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                )

            # Draw face mesh
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, 
                        face_landmarks, 
                        mp_face_mesh.FACEMESH_TESSELATION  # Use FACEMESH_TESSELATION or FACEMESH_CONTOURS
                    )

            # Convert frame to bytes for Flask streaming
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
