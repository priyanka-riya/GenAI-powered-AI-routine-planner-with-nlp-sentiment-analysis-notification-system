import os
import pickle
import torch
import streamlit as st
import speech_recognition as sr
import time
from task_scheduler import prioritize_tasks, update_priorities_based_on_sentiment
from voice_recognition import recognize_command
from mail import send_email
from calender_sync import sync_with_calendar
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator

# Clear CUDA cache if available
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Load GPT-2 model efficiently
@st.cache_resource
def load_model():
    model_name = "gpt2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
    return model, tokenizer, device

model, tokenizer, device = load_model()
translator = Translator()
analyzer = SentimentIntensityAnalyzer()

# Persistent Task Storage
TASKS_FILE = "tasks.pkl"

def save_tasks(tasks):
    with open(TASKS_FILE, "wb") as f:
        pickle.dump(tasks, f)

def load_tasks():
    return pickle.load(open(TASKS_FILE, "rb")) if os.path.exists(TASKS_FILE) else []

tasks = load_tasks()

# Sentiment Analysis Function
def analyze_sentiment(task):
    score = analyzer.polarity_scores(task)["compound"]
    return "Negative" if score <= -0.3 else "Positive" if score >= 0.3 else "Neutral"

# GPT-2 Task Priority Prediction
def get_priority(task):
    input_text = f"Task: {task}. Prioritize this task as High, Medium, or Low."
    inputs = tokenizer.encode(input_text, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(inputs, max_new_tokens=10)
    
    predicted_priority = tokenizer.decode(outputs[0], skip_special_tokens=True).split(":")[-1].strip()
    
    if "high" in predicted_priority.lower():
        return "High"
    elif "medium" in predicted_priority.lower():
        return "Medium"
    elif "low" in predicted_priority.lower():
        return "Low"
    else:
        return "Medium"  # Default to "Medium" if uncertain

# Language Detection & Translation
def detect_language_and_translate(text):
    if text.strip():
        detected_lang = translator.detect(text).lang
        return translator.translate(text, src=detected_lang, dest="en").text if detected_lang != "en" else text
    return text
# Voice Recognition
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    st.write("🎤 Speak tasks one by one. Say 'next' to move, 'stop' to finish.")
    task_list = []
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                if text.lower() == "stop":
                    break
                elif text.lower() == "next":
                    st.write("➡️ Moving to next task...")
                else:
                    translated_task = detect_language_and_translate(text)
                    priority = get_priority(translated_task)
                    sentiment = analyze_sentiment(translated_task)
                    updated_priority = update_priorities_based_on_sentiment(priority, sentiment)
                    task_list.append(f"{translated_task} (Priority: {updated_priority}, Sentiment: {sentiment})")
                    st.write(f"📝 Task Added: {translated_task} (Priority: {updated_priority}, Sentiment: {sentiment})")
            except sr.UnknownValueError:
                st.write("⚠️ Could not understand. Try again.")
            except sr.RequestError:
                st.write("🚨 Speech Recognition API unavailable.")
    return task_list

# Streamlit UI
st.title("🧠 AI-Powered Routine Planner & To-Do List")

# Task Input Selection
input_type = st.radio("How would you like to add tasks?", ["✍️ Text Input", "🎤 Voice Input"])

if input_type == "✍️ Text Input":
    task_text = st.text_area("Enter your tasks (one per line):")
    time_slot = st.text_input("⏳ Enter time slot (e.g., 10 AM - 3 PM):")
    
    if st.button("✅ Schedule Tasks"):
        for line in task_text.split("\n"):
            if line.strip():
                translated_task = detect_language_and_translate(line.strip())
                priority = get_priority(translated_task)
                sentiment = analyze_sentiment(translated_task)
                updated_priority = update_priorities_based_on_sentiment(priority, sentiment)
                
                tasks.append(f"{translated_task} (Priority: {updated_priority}, Sentiment: {sentiment})")
        
        save_tasks(tasks)
        
        st.write("📅 Your Scheduled Tasks:")
        for task in tasks:
            st.write(f"🔹 {task} - {time_slot}")

elif input_type == "🎤 Voice Input":
    if st.button("🎧 Start Listening"):
        new_tasks = recognize_speech()
        
        if new_tasks:
            time_slot = st.text_input("⏳ Enter time slot (e.g., 10 AM - 3 PM):")
            tasks.extend(new_tasks)
            save_tasks(tasks)
            
            st.write("📅 Your Scheduled Tasks:")
            for task in tasks:
                st.write(f"🔹 {task} - {time_slot}")

# Sentiment Check
if st.button("🔍 Check Sentiment"):
    if any("Negative" in task for task in tasks):
        st.write("💬 No worries, let me schedule it perfectly. Take a deep breath!  Melody - https://www.youtube.com/watch?v=9roOWg7C6Zg,Folk - https://www.youtube.com/watch?v=JOSsS6m5mYk,Love-https://www.youtube.com/watch?v=example_link  😊 ")

# Calendar Sync
if st.button("📅 Sync with Calendar"):
    sync_with_calendar(tasks)
    st.success("✅ Calendar Synced Successfully!")

# Email Notification
email = st.text_input("📧 Enter email to receive your schedule:")
if st.button("📩 Send Email"):
    if email:
        send_email(email, "\n".join(tasks))  
        st.success("✅ Email Sent Successfully!")
