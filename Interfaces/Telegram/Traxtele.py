# -------------------- IMPORTS --------------------
import os
import tempfile
import subprocess
import whisper
import requests
import secrets
from langdetect import detect
import mysql.connector
import telebot
from telebot import types
from datetime import datetime

# -------------------- CONFIG --------------------
API_TOKEN = ""
API_KEY_weather = ""
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "Trax"

bot = telebot.TeleBot(API_TOKEN)

# -------------------- DATABASE --------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="Traxtele"
)
cursor = db.cursor(dictionary=True)

# -------------------- AI MODELS --------------------
model = whisper.load_model("base")

# -------------------- UTILITY FUNCTIONS --------------------
def generate_token():
    return secrets.token_hex(16)

def is_authenticated(uid):
    cursor.execute("SELECT * FROM USERS WHERE UID = %s", (uid,))
    return cursor.fetchone()

def get_weather_forecast(location, api_key=API_KEY_weather, days=5):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location,
        "days": days,
        "aqi": "no",
        "alerts": "no"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to retrieve data:", response.status_code, response.text)
        return None

    data = response.json()
    location_name = data['location']['name']
    weather_context = f"*Weather forecast for {location_name}:*\n"

    for day in data['forecast']['forecastday']:
        date = day['date']
        condition = day['day']['condition']['text']
        avg_temp_c = day['day']['avgtemp_c']
        max_temp_c = day['day']['maxtemp_c']
        min_temp_c = day['day']['mintemp_c']
        weather_context += f"{date}: {condition} (Avg: {avg_temp_c}°C, Max: {max_temp_c}°C, Min: {min_temp_c}°C)\n"

    return weather_context

# -------------------- STATIC WELCOME MESSAGE --------------------
WELCOME_MESSAGE = """*Welcome to Trax AI — Your Personal Travel Guide in Your Pocket*

_Ready to explore smarter?_  
Trax AI is here to help you travel with ease, anytime, anywhere. Here's what you can do with Trax:

*Core Features:*
• *Available 24/7* — Ask anything, anytime.  
• *Distance Estimation* — Quickly find how far you are from any place.  
• *Live Fest Information* — Stay updated with festivals and events happening around you.  
• *Story Mode (Exclusive)* — Say “Story Mode” to enter a rich, interactive travel story based on your journey.  
• *Bookmark Locations* — Just say “Bookmark” to save your favorite spots.  
• *Personalized Recommendations* — Tell us your hobbies once, and get travel suggestions tailored to you.  
• *Live Weather Updates* — Get real-time weather information for your current location.

*Coming Soon:*
• *Turn-by-Turn Directions* — Navigate to your destination with ease.  
• *Hotel & Restaurant Collaborations* — Get recommendations and even connect with places directly.

_Pre-book our Call-assistant to use all the features._
"""

# -------------------- COMMAND HANDLERS --------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['login'])
def login_request(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton("📱 Share phone number", request_contact=True)
    markup.add(contact_btn)
    bot.send_message(message.chat.id, "Please tap the button below to share your phone number:", reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    contact = message.contact
    phone = contact.phone_number
    uid = message.from_user.id
    name = contact.first_name

    cursor.execute("SELECT * FROM USERS WHERE UID = %s", (uid,))
    user = cursor.fetchone()

    if not user:
        token = generate_token()
        cursor.execute(
            "INSERT INTO USERS (UID, PHONE_NUMBER, NAME, TOKEN) VALUES (%s, %s, %s, %s)",
            (uid, phone, name, token)
        )
        db.commit()
        bot.send_message(uid, "🎉 You've been registered successfully!")
    else:
        bot.send_message(uid, "✅ Welcome back! You're already logged in.")

@bot.message_handler(commands=['logout'])
def logout_user(message):
    uid = message.from_user.id
    cursor.execute("UPDATE USERS SET TOKEN = NULL WHERE UID = %s", (uid,))
    db.commit()
    bot.send_message(uid, "🔓 You've been logged out.")

@bot.message_handler(commands=['add_hobby'])
def add_hobby(message):
    uid = message.from_user.id
    hobby_text = message.text.replace('/add_hobby', '').strip()
    if not hobby_text:
        bot.send_message(uid, "❗ Please write the hobby after /add_hobby.")
        return

    cursor.execute(
        "INSERT INTO HOBBIES (UID, Favs, Timestamp) VALUES (%s, %s, NOW())",
        (uid, hobby_text)
    )
    db.commit()
    bot.send_message(uid, "✅ Hobby added successfully!")

@bot.message_handler(commands=['my_bookmarks'])
def view_bookmarks(message):
    uid = message.from_user.id
    cursor.execute("SELECT Location, Timestamp FROM BOOKMARKS WHERE UID = %s", (uid,))
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(uid, "📭 No bookmarks found.")
        return

    response = "\n".join([f"📍 {row['Location']} — {row['Timestamp']}" for row in rows])
    bot.send_message(uid, response)

#----- EXTRA UTILITIES FUNCTION
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Skow@',
    'database': 'Traxtele'
}
def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# FOR EXTRACTING USER DATA FROM THE DATABASE 
def fetch_user_dashboard_data(uid):
    """Fetch user info, hobbies, and latest 5 bookmarks for dashboard."""
    connection = get_db_connection()
    if not connection:
        return {"status": "error", "message": "DB connection failed."}

    user_data = {
        "user_info": {},
        "hobbies": [],
        "bookmarks": [],
        "status": "success",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        cursor = connection.cursor(dictionary=True)

        # 1. Fetch user info
        sql_user = "SELECT NAME, PHONE_NUMBER, EMAIL FROM USERS WHERE UID = %s"
        cursor.execute(sql_user, (uid,))
        user_info = cursor.fetchone()
        if user_info:
            user_data["user_info"] = user_info
        else:
            user_data["status"] = "error"
            user_data["message"] = "User not found."
            return user_data

        # 2. Fetch hobbies (comma-separated text field)
        sql_hobbies = "SELECT Favs FROM HOBBIES WHERE UID = %s ORDER BY Timestamp DESC"
        cursor.execute(sql_hobbies, (uid,))
        hobbies_result = cursor.fetchall()
        for row in hobbies_result:
            # Split comma-separated hobbies into a list
            hobbies_list = [h.strip() for h in row['Favs'].split(',') if h.strip()]
            user_data["hobbies"].extend(hobbies_list)

        # 3. Fetch last 5 bookmarks
        sql_bookmarks = """
            SELECT Location, Timestamp
            FROM BOOKMARKS
            WHERE UID = %s
            ORDER BY Timestamp DESC
            LIMIT 5
        """
        cursor.execute(sql_bookmarks, (uid,))
        bookmarks = cursor.fetchall()
        for bm in bookmarks:
            user_data["bookmarks"].append({
                "Location": bm['Location'],
                "Timestamp": bm['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            })

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        user_data["status"] = "error"
        user_data["message"] = f"Database error: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        user_data["status"] = "error"
        user_data["message"] = f"Unexpected error: {e}"
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

    return user_data




# -------------------- TEXT & VOICE INPUT HANDLING --------------------
@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.from_user.id
    user_text = message.text.strip()
    user = is_authenticated(uid)

    if "story mode" in user_text.lower() and not user:
        bot.send_message(uid, "🔒 Please /login to use story mode.")
        return

    if user_text.lower().startswith("weather in "):
        location = user_text.split("weather in ", 1)[1]
        forecast = get_weather_forecast(location)
        if forecast:
            bot.send_message(uid, forecast, parse_mode='Markdown')
        else:
            bot.send_message(uid, "⚠️ Couldn't fetch the weather.")
        return

    lang = detect(user_text)
    if "story mode" in user_text.lower():
        prompt = f"You are a local storyteller AI guiding the user through the city. Narrate an engaging story about a famous place near them. Respond in {lang}."
    else:
        prompt = f"You are a multilingual city guide AI. The user said: '{user_text}'. Respond helpfully in {lang}."

    response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
    reply = response.json().get("response", "Sorry, I couldn’t understand that.")
    bot.send_message(uid, reply)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        file = bot.download_file(file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as temp_audio:
            temp_audio.write(file)
            temp_audio_path = temp_audio.name

        wav_path = temp_audio_path.replace(".oga", ".wav")
        subprocess.run(['ffmpeg', '-i', temp_audio_path, wav_path])

        result = model.transcribe(wav_path)
        transcribed_text = result["text"]
        lang = detect(transcribed_text)

        if "story mode" in transcribed_text.lower():
            prompt = f"You are a local storyteller AI guiding the user through the city. Narrate an engaging story about a famous place near them. Respond in {lang}."
        else:
            prompt = f"You are a multilingual city guide AI. The user said: '{transcribed_text}'. Respond helpfully in {lang}."

        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
        reply = response.json().get("response", "Sorry, I couldn’t understand that.")
        bot.send_message(message.chat.id, reply)

        os.remove(temp_audio_path)
        os.remove(wav_path)
    except Exception as e:
        print("Error handling voice message:", e)
        bot.send_message(message.chat.id, "There was an error processing your voice message.")

# -------------------- START BOT --------------------
print("🚀 Telegram bot is now running...")
bot.polling()
