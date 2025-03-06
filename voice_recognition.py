from pydub import AudioSegment
import speech_recognition as sr
import os
import pygame  # For playing music

# Define stress-related keywords
STRESS_KEYWORDS = ["deadline", "urgent", "presentation", "exam", "bug", "pressure", "tension", "critical"]

def play_music(music_file="relaxing_music.mp3"):
    """Plays a relaxing music file."""
    pygame.mixer.init()
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play()
    print("🎵 Playing relaxing music...")

def recognize_command(audio_file="sample.ogg"):
    """Converts an audio file to text and detects stress-related commands."""
    
    # Convert OGG to WAV
    audio = AudioSegment.from_file(audio_file, format="ogg")
    wav_file = "converted_audio.wav"
    audio.export(wav_file, format="wav")

    # Initialize speech recognizer
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Check if task is stressful
        is_stressful = any(keyword in text.lower() for keyword in STRESS_KEYWORDS)
        
        if is_stressful:
            print(f"🚨 Stressful task detected: {text}")
            play_music()  # Play music if stress detected
        else:
            print(f"✅ Task recognized: {text}")

        return text, is_stressful
    
    except sr.UnknownValueError:
        return "Could not understand the audio", False
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition", False

# Test the function
if __name__ == "__main__":
    recognized_text, stress_detected = recognize_command("sample.ogg")  # Replace with your audio file
    print(f"Recognized Text: {recognized_text}")
    print(f"Stress Detected: {'Yes' if stress_detected else 'No'}")
