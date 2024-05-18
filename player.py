import csv
import random
import vlc
from pytube import YouTube
from youtubesearchpython import VideosSearch

# Emotion labels
labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

def get_user_feeling():
    # Provide a description of the program's functionality
    print("Welcome to the Emotion-based Song Recommender!")
    while True:
        user_feeling = input("How are you feeling today? (Enter an emotion or 'x' to quit): ").strip().capitalize()

        if user_feeling == 'X':
            print("Goodbye!")
            exit()

        if user_feeling in labels:
            return user_feeling
        else:
            print("Invalid emotion. Please choose from the following: ", labels)

def prefetch_audio_streams(emotion):
    csv_name = f"Song_Names/{emotion}.csv"
    songs = []

    try:
        with open(csv_name, mode="r", newline="") as file:
            songs = list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"No song recommendations found for emotion: {emotion}")
        return []

    audio_streams = []

    for song in songs:
        song_name = song.get("Song Name")
        search_query = f"{song_name} official music video YouTube"
        videos_search = VideosSearch(search_query, limit=1)
        results = videos_search.result()

        if results["result"]:
            video_url = results["result"][0]["link"]
            try:
                yt = YouTube(video_url)
                audio_stream = yt.streams.get_audio_only()
                audio_streams.append((song_name, audio_stream.url))
            except Exception as e:
                print(f"Error in processing song {song_name}, link {video_url}: {str(e)}")

    return audio_streams

def play_random_song(emotion, audio_streams):
    if not audio_streams:
        print("No audio streams available. Exiting.")
        return

    played_songs = set()

    while True:
        remaining_songs = [song for song in audio_streams if song[0] not in played_songs]
        if not remaining_songs:
            print("No more songs to play.")
            break

        random_song = random.choice(remaining_songs)
        song_name, audio_url = random_song
        try:
            print(f"Playing song: {song_name}")
            player = vlc.MediaPlayer(audio_url)
            player.play()
            played_songs.add(song_name)

            user_choice = input("Press 'Enter' to play another song, 'x' to quit: ").strip().lower()
            if user_choice == 'x':
                break
        except Exception as e:
            print(f"Error in playing song {song_name}: {str(e)}")

def main():
    emotion = get_user_feeling()
    audio_streams = prefetch_audio_streams(emotion)
    play_random_song(emotion, audio_streams)

if __name__ == '__main__':
    main()
