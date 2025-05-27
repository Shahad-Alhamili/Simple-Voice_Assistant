import speech_recognition as sr
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
import io 
import pygame

engine = pyttsx3.init()

def ar_speak(text,language='ar'):
    tts = gTTS(text=text, lang='ar', slow=True)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    
    # Play the audio using pygame
    pygame.mixer.music.load(audio_fp)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy(): 
        continue

def speak(text, language="en"):
    engine.setProperty('rate', 170)  # Set speech rate
    engine.setProperty('voice', language)  # Set voice based on language
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio, language="en-US")
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""

def translation_chatbot():
    speak("Welcome to the English-to-Arabic translation bot! Please speak your sentence.")
    while True:
        english_text = listen()
        if english_text == 'bye':
            speak("Goodbye!")
            break
        try:
            arabic_translation = GoogleTranslator(source='en', target='ar').translate(english_text)
            print(f"Translation: {arabic_translation}")
            ar_speak(arabic_translation)
        except Exception as e:
            speak("Sorry, an error occurred with translation.")


def get_headlines(api_key):
    URL = "https://newsapi.org/v2/top-headlines"
    parameters = {'country': 'us', 'apiKey': api_key}
    response = requests.get(URL, params=parameters)
    if response.status_code == 200:
        return [article['title'] for article in response.json().get('articles', [])[:3]]
    else:
        speak(f"Error: {response.status_code}")
        return []

def get_flight_details(api_key, flight_number):
    flight_number = flight_number.replace(" ", "")
    URL = "http://api.aviationstack.com/v1/flights"
    parameters = {'access_key': api_key, 'flight_iata': flight_number}
    response = requests.get(URL, params=parameters)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            flight_info = data['data'][0]
            details = {
                "Airline": flight_info['airline']['name'],
                "Flight Number": flight_info['flight']['iata'],
                "Departure Airport": flight_info['departure']['airport'],
                "Arrival Airport": flight_info['arrival']['airport'],
                "Scheduled Departure": flight_info['departure']['scheduled'],
                "Scheduled Arrival": flight_info['arrival']['scheduled'],
                "Status": flight_info['flight_status']
            }
            for key, value in details.items():
                speak(f"{key}: {value}")
        else:
            speak("No data found for this flight number.")
    else:
        speak(f"Error: {response.status_code}")

def read_headlines(headlines):
    for i, headline in enumerate(headlines[:3], 1):
        speak(f"Headline {i}: {headline}")

def handle_command(query):
    if "translate" in query:
        translation_chatbot()
    elif "news" in query:
        api_key = "40f8e2679a934267bc2f63865a3239f0"
        headlines = get_headlines(api_key)
        if headlines:
            read_headlines(headlines)
    elif "flight" in query:
        speak("Please say your flight number.")
        flight_number = listen()
        api_key = "7954daadf635fe17cb5ad7321afdc3a4"
        get_flight_details(api_key, flight_number)
    elif "read news" in query:
        api_key = "40f8e2679a934267bc2f63865a3239f0"
        headlines = get_headlines(api_key)
        read_headlines(headlines)
    elif "bye" in query:
        speak("Goodbye!")
        return False
    else:
        speak("I'm not sure how to help with that.")
    return True


def virtual_assistant():
    """Main function to run the virtual assistant."""
    speak("Welcome to the Virtual Assistant System! How can I help you today?")
    while True:
        query = listen()
        if query:
            if not handle_command(query):
                break

# Start the virtual assistant
virtual_assistant()
