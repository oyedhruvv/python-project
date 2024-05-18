import cv2
import numpy as np
import csv
import random
import pywhatkit as pl
from keras.models import load_model
from youtubesearchpython import VideosSearch
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Define emotions as constants
EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# Load the emotion detection model
model = load_model("model.h5")

# Initialize a Selenium WebDriver (Chrome)
driver = webdriver.Chrome()

def get_user_emotion():
    while True:
        user_feeling = input("How are you feeling today? ").strip().capitalize()
        if user_feeling in EMOTIONS:
            return user_feeling
        else:
            print("Invalid emotion. Please choose from the following:", EMOTIONS)

def capture_video_frames():
    cap = cv2.VideoCapture(0)
    frames = []

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        if not ret:
            print("Can't access the camera")
            user_emotion = get_user_emotion()
            play_random_song(user_emotion)
            break

        frames.append(frame)
        cv2.putText(
            frame,
            "Press q to take a snapshot",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if frames:
        avg_frame = np.mean(frames, axis=0).astype(np.uint8)
        avg_frame = cv2.resize(avg_frame, (640, 480))
        cv2.imwrite("Snapshot.jpg", avg_frame)

        img = cv2.imread("Snapshot.jpg", cv2.IMREAD_GRAYSCALE)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(
            img, scaleFactor=1.1, minNeighbors=5
        )

        if len(faces) > 0:
            face_roi = cv2.resize(img[faces[0][1]:faces[0][1] + faces[0][3], faces[0][0]:faces[0][0] + faces[0][2]], (48, 48), interpolation=cv2.INTER_NEAREST)
            face_roi = np.expand_dims(face_roi, axis=(0, 3))
            prediction = model.predict(face_roi)
            return EMOTIONS[int(np.argmax(prediction))]

        else:
            print("No frames captured.")
            user_emotion = get_user_emotion()
            return user_emotion

def play_song_with_selenium(song_name):
    # Search for the song on YouTube
    driver.get("https://www.youtube.com")
    search_box = driver.find_element_by_name("search_query")
    search_box.send_keys(song_name)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results and click the first video
    time.sleep(3)
    videos = driver.find_elements_by_id("video-title")
    if videos:
        videos[0].click()
        time.sleep(2)

def play_random_song(emotion):
    csv_name = f"Song_Names/{emotion}.csv"
    songs = []

    try:
        with open(csv_name, mode="r", newline="") as file:
            songs = list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"No song recommendations found for emotion: {emotion}")

    if not songs:
        return

    played_songs = set()

    while True:
        remaining_songs = [song for song in songs if song["Song Name"] not in played_songs]
        if not remaining_songs:
            print("No more songs to play.")
            break

        random_song = random.choice(remaining_songs)
        song_name = random_song.get("Song Name")

        print(f"Playing song: {song_name}")
        play_song_with_selenium(song_name)
        played_songs.add(song_name)
        user_choice = input("Press 'Enter' to play another song, or 'x' to exit: ").strip().lower()
        if user_choice == 'x':
            break

def main():
    while True:
        if cv2.VideoCapture(0).isOpened():
            emotion = capture_video_frames()
            print(f"Detected emotion: {emotion}")
            play_random_song(emotion)
        else:
            print("Can't access the camera. Please check your camera.")
            user_emotion = get_user_emotion()
            play_random_song(user_emotion)

try:
    main()
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
