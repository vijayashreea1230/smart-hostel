import cv2
from deepface import DeepFace

# Open Webcam
cap = cv2.VideoCapture(0)

print("Emotion Detection Started...")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    try:
        # Detect emotion
        analysis = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False
        )

        emotion = analysis[0]['dominant_emotion']

        # Save emotion into txt file
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root_dir, "emotion.txt"), "w") as file:
            file.write(emotion)

        # Display emotion on webcam
        cv2.putText(
            frame,
            f'Emotion: {emotion}',
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    except Exception as e:
        print("Error:", e)

    # Webcam window
    cv2.imshow("Emotion Detection and Adaptive Room", frame)

    # Press Q to close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()