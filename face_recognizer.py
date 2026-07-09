import cv2
import numpy as np
import os
import pickle
import face_recognition as fr

TRAINER_FILE = 'trainer.pkl'


class FaceRecognizer:
    def __init__(self):
        # Directory to store face samples
        self.dataset_path = 'dataset'
        # File to store trained model (encodings)
        self.trainer_file = TRAINER_FILE
        # Cached encodings loaded once per session
        self._known_encodings = None
        self._known_ids = None

        # Create dataset directory if it doesn't exist
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)

    # ------------------------------------------------------------------
    # Face detection
    # ------------------------------------------------------------------
    def detect_face(self, img):
        """Detect faces in an image.

        Returns:
            faces  – list of (x, y, w, h) tuples
            gray   – grayscale version of the input image
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Use dlib's HOG detector via face_recognition (more robust than Haar)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locations = fr.face_locations(rgb, model='hog')
        # face_recognition returns (top, right, bottom, left); convert to (x, y, w, h)
        faces = []
        for (top, right, bottom, left) in locations:
            faces.append((left, top, right - left, bottom - top))
        return faces, gray

    # ------------------------------------------------------------------
    # Capture training samples
    # ------------------------------------------------------------------
    def capture_samples(self, student_id, sample_count=30):
        """Capture face samples for a student using the webcam.

        Returns the number of samples saved.
        """
        cap = cv2.VideoCapture(0)
        count = 0

        student_path = os.path.join(self.dataset_path, str(student_id))
        if not os.path.exists(student_path):
            os.makedirs(student_path)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            faces, gray = self.detect_face(frame)

            for (x, y, w, h) in faces:
                count += 1
                cv2.imwrite(f"{student_path}/sample_{count}.jpg", gray[y:y + h, x:x + w])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, f"Sample {count}/{sample_count}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            cv2.imshow('Capturing Samples', frame)

            if cv2.waitKey(1) & 0xFF == 27 or count >= sample_count:
                break

        cap.release()
        cv2.destroyAllWindows()
        # Invalidate cached encodings when new samples are added
        self._known_encodings = None
        self._known_ids = None
        return count

    # ------------------------------------------------------------------
    # Train model (build encodings)
    # ------------------------------------------------------------------
    def train_model(self):
        """Build face encodings from all samples in the dataset directory.

        Returns True on success, False otherwise.
        """
        student_ids = [d for d in os.listdir(self.dataset_path)
                       if os.path.isdir(os.path.join(self.dataset_path, d))]

        if not student_ids:
            print("No samples found for training")
            return False

        all_encodings = []
        all_ids = []

        for student_id in student_ids:
            student_path = os.path.join(self.dataset_path, student_id)
            image_files = [f for f in os.listdir(student_path)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

            for image_file in image_files:
                image_path = os.path.join(student_path, image_file)
                image = fr.load_image_file(image_path)
                encodings = fr.face_encodings(image)

                if encodings:
                    all_encodings.append(encodings[0])
                    all_ids.append(int(student_id))

        if not all_encodings:
            print("No faces found for training")
            return False

        # Save encodings to disk
        with open(self.trainer_file, 'wb') as f:
            pickle.dump({'encodings': all_encodings, 'ids': all_ids}, f)

        # Cache in memory
        self._known_encodings = all_encodings
        self._known_ids = all_ids

        print(f"Model trained with {len(all_encodings)} samples for {len(set(all_ids))} students")
        return True

    # ------------------------------------------------------------------
    # Load encodings into memory
    # ------------------------------------------------------------------
    def _load_encodings(self):
        """Load encodings from disk into memory if not already cached."""
        if self._known_encodings is not None:
            return True
        if not os.path.exists(self.trainer_file):
            return False
        try:
            with open(self.trainer_file, 'rb') as f:
                data = pickle.load(f)
            self._known_encodings = data['encodings']
            self._known_ids = data['ids']
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    # ------------------------------------------------------------------
    # Recognize a face in a single image
    # ------------------------------------------------------------------
    def recognize_face(self, img):
        """Recognize faces in an image.

        Returns a list of (student_id, confidence_percent, (x, y, w, h)) tuples.
        """
        if not self._load_encodings():
            return []

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb, model='hog')
        face_encodings = fr.face_encodings(rgb, face_locations)

        recognized_faces = []
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            distances = fr.face_distance(self._known_encodings, encoding)
            best_idx = np.argmin(distances)
            best_distance = distances[best_idx]

            # face_distance: 0 = perfect match, 1 = no match
            # Treat distance < 0.6 as a match (≈ 40 % confidence threshold)
            confidence = (1 - best_distance) * 100

            x, y, w, h = left, top, right - left, bottom - top
            if best_distance < 0.6:
                recognized_faces.append((self._known_ids[best_idx], confidence, (x, y, w, h)))
            else:
                recognized_faces.append((None, confidence, (x, y, w, h)))

        return recognized_faces

    # ------------------------------------------------------------------
    # Real-time webcam recognition loop
    # ------------------------------------------------------------------
    def real_time_recognition(self, callback=None):
        """Open the webcam and run real-time face recognition.

        Press ESC to stop.
        """
        if not self._load_encodings():
            print("Model not trained yet or failed to load. Capture samples and train first.")
            return

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            recognized_faces = self.recognize_face(frame)

            for item in recognized_faces:
                if len(item) == 3:
                    id_, confidence, (x, y, w, h) = item
                    color = (0, 255, 0) if id_ is not None else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                    if id_ is not None:
                        text = f"ID: {id_} ({confidence:.2f}%)"
                        cv2.putText(frame, text, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        if callback:
                            callback(id_, confidence)
                    else:
                        cv2.putText(frame, "Unknown", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    # ------------------------------------------------------------------
    # Liveness Detection Helpers (EAR)
    # ------------------------------------------------------------------
    def eye_aspect_ratio(self, eye):
        """Compute Eye Aspect Ratio (EAR) for liveness check"""
        A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
        B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
        C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
        ear = (A + B) / (2.0 * C)
        return ear

    def recognize_face_with_liveness(self, img):
        """Recognize faces in an image and calculate the Eye Aspect Ratio (EAR).

        Returns a list of (student_id or None, confidence, (x, y, w, h), ear) tuples.
        If model is not loaded, returns entries with None id so bounding boxes still draw.
        """
        loaded = self._load_encodings()

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb, model='hog')
        face_encodings = fr.face_encodings(rgb, face_locations)
        face_landmarks_list = fr.face_landmarks(rgb, face_locations)

        recognized_faces = []
        for idx, ((top, right, bottom, left), encoding) in enumerate(zip(face_locations, face_encodings)):
            x, y, w, h = left, top, right - left, bottom - top
            ear = 1.0
            if idx < len(face_landmarks_list):
                landmarks = face_landmarks_list[idx]
                if 'left_eye' in landmarks and 'right_eye' in landmarks:
                    left_ear = self.eye_aspect_ratio(landmarks['left_eye'])
                    right_ear = self.eye_aspect_ratio(landmarks['right_eye'])
                    ear = (left_ear + right_ear) / 2.0
            if loaded:
                distances = fr.face_distance(self._known_encodings, encoding)
                best_idx = np.argmin(distances)
                best_distance = distances[best_idx]
                confidence = (1 - best_distance) * 100
                if best_distance < 0.65:
                    recognized_faces.append((self._known_ids[best_idx], confidence, (x, y, w, h), ear))
                else:
                    recognized_faces.append((None, confidence, (x, y, w, h), ear))
            else:
                recognized_faces.append((None, 0.0, (x, y, w, h), ear))

        return recognized_faces

