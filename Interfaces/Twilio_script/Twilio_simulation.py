#------------ UPDATE LOGS---------------------------:
# Adding the waiting music
# Adding the summary 
# Adding telegram bot 
# Adding Faiss and other data processing capablities
# [2.3/8]
# Adding Email and other capablities
# Version 2.3 [MAJOR INTERACTION UPGRADES]   [Email formatting ]

#---------------------------------------------------------------#

#------------------------------- TRAX AI -------------------------------- #
# FUNCTIONS :
# 1. Give directions
# 2. Distance calculations
# 3. Live fest information
# 4. Story Mode EXCLUSIIVE  [USING KEYWORD STORYMODE/STORY MODE]
# 5. Bookmark the location  [USING KEYWORD BOOKMARK]
# 6. Keeping the list of Hobbies of the person and then giving answers based on that 
# 7. Live weather of the persons location.
# WHAT WE CAN ADD LATER ON:
# 1. HOTEL-RESTURANTS COLLABORATIONS [DIRECT CALL TRANSFER] 
import warnings
warnings.filterwarnings("ignore") ### IGNORING ALL WARNINGS / SUPPORT MESSAGES OF PYGAME
import speech_recognition as sr
import pyttsx3
import ollama
from gtts import gTTS
import os
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play
import mysql.connector
import re
from datetime import datetime # Import datetime for formatting
import requests   # for telegram too i'm using this
import threading # for music bgm flag
import time
import pygame # FOR music controlplayback
# import faiss  # For faiss connections
# import pickle   # For faiss connections
import numpy as np  # data processing  
# from sentence_transformers import SentenceTransformer   # creating vector embeddings
# from sklearn.metrics.pairwise import cosine_similarity    # getting the most similar ones from the faiss
import smtplib   # FOR SMTP Email service
from email.message import EmailMessage # For SMTP
# FOR WEB-SCRAPING
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
    

# --- Configuration ---
OLLAMA_MODEL = 'Trax'   # Adding the new model
OLLAMA_URL = 'http://localhost:11434'

# ---- Keywords to detect ---- WILL CHANGE FOR STORY MODE
KEYWORDS = ["talk", "customer executive", "ticket", "transfer", "human", "customer agent", "escalate"]
keyword_count = 0
NUMBER= 0
NAME  = ''
EMAIL = ''

#--- for telegram--- WILL USE IT FOR PIPELINING
BOT_TOKEN = "7825661028:AAFLhWXeRXBe5w3JVTdqolAy9lxuvsVl9EM"  # got this from BotFather
CHAT_ID = "7313225622" 


# --- FOR EMAILING SERVICE EMAILING ITENARY [SMTP] ---
SENDER_EMAIL = 'purohitkavyaa@gmail.com'    # We'll have to make a new id and pass for security
SENDER_PASSWORD = 'abzj yvye xlpv nwkh'   

# --- function to count keywords---
def contains_keyword(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

        
stop_music_flag = threading.Event()

# ---  function for bgm---
def play_music_loop(audio_file): # CAN STILL PLAY THIS MUSIC FOR ON-CALL WAITING TIME SIMULATION
    """Plays the audio file in a loop until stop_music_flag is set."""
    #print(f"Starting music: {audio_file}") added this for debugging
    try:
        pygame.mixer.init() # Initialize the mixer
        pygame.mixer.music.load(audio_file)
        # -1 means play indefinitely (loop)
        pygame.mixer.music.play(-1)

        # Keep the thread alive while music is playing and flag is not set
        while not stop_music_flag.is_set():
            time.sleep(0.1) # Small delay to prevent busy-waiting and allow flag check

        # Music needs to be stopped explicitly when flag is set
        pygame.mixer.music.stop()
        pygame.mixer.quit() # Uninitialize the mixer
        # print("Music stopped.") added this for debugging

    except pygame.error as e:
        print(f"Error playing sound with Pygame: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Telegram bot integration ---
def send_telegram_message_http(message_text: str):
    """
    Sends a message to the specified Telegram chat using direct HTTP request.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML" # You can use "MarkdownV2" or "Markdown" as well
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# -----  FAISS INTEGRATION --- CAN USE THIS TO EMBED INFORMATION ABOUT HOTELS-RESTAURANTS ALL OVER INDIA 
# Load embedding model
# model = SentenceTransformer("all-MiniLM-L6-v2")  # COMMENTING IT FOR NOW cmf

# Load FAISS index + associated FAQ texts
# index = faiss.read_index("faqs_index.faiss")  # cmf
# with open("faqs_texts.pkl", "rb") as f:
#     faq_texts = pickle.load(f)

# --- FUNCTION FOR FAISS OUTPUT ------
# def faissfunc(query, top_k=3, similarity_threshold=0.6):  cmf
#     query_embedding = model.encode([query])
#     distances, indices = index.search(np.array(query_embedding), top_k)

#     relevant_texts = []
#     for idx in indices[0]:
#         if idx == -1: continue
#         faq_embedding = model.encode([faq_texts[idx]])
#         sim_score = cosine_similarity(query_embedding, faq_embedding)[0][0]
#         if sim_score >= similarity_threshold:
#             relevant_texts.append(faq_texts[idx])

#     # Construct the faisprompt
#     if relevant_texts:
#         faiscontext = "\n\n".join(relevant_texts)
#         send_email(EMAIL,relevant_texts) ### SENDING THE STEPS TO THE USER
#         # print(faiscontext)  # Removing it for debugging
#         faisprompt = f"""Use the following faiscontext and previous conversation to answer the user's question.

# faiscontext:
# {faiscontext}

# User's Question: {query}

# Answer:"""
#     else:
#         # No relevant faiscontext — rely on chat history
#         faisprompt = f"""The user asked a new question. There's no matching FAQ faiscontext, but use the conversation history to help if possible.

# User's Question: {query}

# Answer:"""
#     return faisprompt


# ---  SMTP EMAILING ----
def send_email(EMAIL,solutions):   # CAN USE THIS LATER ON TO SEND NICE ITERANARIES AND HOTEL ADS
    subject = "A Beautiful message from Trax AI"
        # Join solutions and cut off at "Don't tell" or "Don’t tell" (accounts for both apostrophes)
    full_text = "\n".join(solutions)
    cutoff_phrases = ["Don't tell", "Don’t tell"]
    for phrase in cutoff_phrases:
        if phrase in full_text:
            full_text = full_text.split(phrase)[0].strip()
            break

    # Turn the steps into HTML (line by line as <li>)
    lines = full_text.splitlines()
    question = lines[0] if lines else ""
    answer_steps = lines[1:] if len(lines) > 1 else []

    step_list_html = "".join(f"<li>{step.strip()}</li>" for step in answer_steps if step.strip())

    # HTML Email body with simple styling
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #0052cc;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{question}</h2>
            <ul>
                {step_list_html}
            </ul>
            <p>Best regards,<br/>Your Support Team</p>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = EMAIL
    msg.set_content(body,subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        speak(f"\nSteps have been sent successfully to your email: {EMAIL}",use_gtts=True, speed_factor=1.35)
    except Exception as e:
        print(f"\nFailed to send email: {e}")

# --- FOR CONFIRMATION ---
def get_confirmation():
    confirmation = None
    while confirmation is None:
        confirmation = listen_command()
        if confirmation is None:
            print("Received None, trying again...")
    return confirmation.strip().lower()



# ------ FOR ADDING BOOKMARKS ------------
def add_user_bookmark(uid, location):
    """
    Insert a new bookmark for the user into the BOOKMARKS table.
    
    Args:
        uid (int): User ID
        location (str): Location name or URL to bookmark
    
    Returns:
        dict: Operation status and message
    """
    connection = get_db_connection()
    if not connection:
        return {"status": "error", "message": "DB connection failed."}

    try:
        cursor = connection.cursor()

        # Insert new bookmark with current timestamp
        insert_sql = """
            INSERT INTO BOOKMARKS (UID, Location, Timestamp)
            VALUES (%s, %s, %s)
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(insert_sql, (uid, location, current_time))
        connection.commit()

        return {
            "status": "success",
            "message": "Bookmark added successfully.",
            "bookmark": {
                "UID": uid,
                "Location": location,
                "Timestamp": current_time
            }
        }

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": f"Database error: {e}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": "error", "message": f"Unexpected error: {e}"}
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
# ---------------------------------------------------------


# ------ FOR WEATHER UPDATES AT THE LOCATION ----
API_KEY_weather = "3b86024fff7740b691090839252707"
weather_info = ""
def get_weather_forecast(location,api_key=API_KEY_weather, days=14):
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
        return

    data = response.json()
    location_name = data['location']['name']
    f"Weather forecast for {location_name}:\n"

    weather_context = f"Weather forecast for {location_name}:\n"
    for day in data['forecast']['forecastday']:
        date = day['date']
        condition = day['day']['condition']['text']
        avg_temp_c = day['day']['avgtemp_c']
        max_temp_c = day['day']['maxtemp_c']
        min_temp_c = day['day']['mintemp_c']
        weather_context+=f"{date}: {condition} (Avg: {avg_temp_c}°C, Max: {max_temp_c}°C, Min: {min_temp_c}°C)\n"
    print("ADDED WEATHER FORECAST TO CONTEXT FILE")
    return weather_context

# ------------------------------------------------

# CITIES SUPPORTED FOR BMS
supported_cities = [
    "delhi", "ncr", "mumbai", "bangalore", "chennai", "hyderabad", "kolkata",
    "pune", "ahmedabad", "jaipur", "lucknow", "gandhinagar", "kanpur",
    "patna", "ranchi", "bhubaneswar", "vadodara", "surat", "coimbatore",
    "kochi", "trivandrum", "visakhapatnam", "mysore", "mangalore", "nagpur",
    "indore", "gwalior", "chandigarh", "varanasi", "udaipur", "faridabad",
    "gurugram", "jalandhar", "ludhiana", "mohali", "kota", "patiala",
    "rourkela", "guwahati", "jamshedpur", "muzaffarpur", "asansol", "silchar",
    "dehradun", "allahabad", "bhopal"
]


# --------------- FOR CITY EVENT UPDATES ---------------
def fetch_event_names(city, max_events=20):
    url = f"https://in.bookmyshow.com/explore/events-{city}"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--user-agent=Mozilla/5.0')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)

    # Scroll to load more
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    links = soup.select('a[href*="/events/"]')
    seen = set()
    events = []

    for tag in links:
        href = tag.get("href", "")
        if not re.match(r"^/events/[^/]+/ET\d+", href):
            continue

        title = tag.get("title") or tag.text.strip()
        if title and title not in seen:
            seen.add(title)
            events.append(title)

        if len(events) >= max_events:
            break

    # Format the result string
    if events:
        result = f"UPCOMING EVENTS IN {city.upper()}:\n"
        for i, event in enumerate(events, 1):
            result += f"{i}. {event}\n"
        return result.strip()
    else:
        return f"No events found in {city.title()}."

def extract_city_from_command(command):
    command = command.lower()
    for city in supported_cities:
        if city in command:
            return city
    return None

# ------------------------------------------------------------------#

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Skow@',
    'database': 'Trax'
}

# Initialize pyttsx3 engine as a fallback mechanisme bychance if GTTS doesn't works
engine_pyttsx3 = pyttsx3.init()

# --- Adjusting the Speech Rate for pyttsx3 (if used) ---
current_rate = engine_pyttsx3.getProperty('rate')
engine_pyttsx3.setProperty('rate', current_rate + 50)

# Maintaining a chat history and giving it as an input to agent
chat_history = []

# --- Database Functions ---
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

def verify_user(mobile):   # CURRENTLY DOING THE VERIFICATION ON THE BASES OF PHONE_NUMBER WILL ADD MPIN LATER IF REQUIRED
    """
    Verifies if a user with the given mobile number exists in the database.
    Returns (UID, NAME) tuple if found, None otherwise.
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = "SELECT UID, NAME,EMAIL FROM USERS WHERE PHONE_NUMBER = %s"
            cursor.execute(sql, (mobile,))
            result = cursor.fetchone()
            if result:
                print(f"User with mobile '{mobile}' verified. UID: {result[0]}, Name: {result[1]}")
                return result  # (UID, NAME)
            else:
                print(f"No user found with mobile '{mobile}'.")
                return None
        except mysql.connector.Error as e:
            print(f"Database error during user verification: {e}")
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    return None


def register_user(name, phone_number, email):
    """
    Registers a new user into the database if the phone number doesn't already exist.
    Returns UID if registered, False if user already exists or on error.
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the phone number already exists
            cursor.execute("SELECT UID FROM USERS WHERE PHONE_NUMBER = %s", (phone_number,))
            if cursor.fetchone():
                print(f"User with phone number '{phone_number}' already exists.")
                return False

            # Get the next UID
            cursor.execute("SELECT MAX(UID) FROM USERS")
            max_uid_result = cursor.fetchone()
            new_uid = (max_uid_result[0] or 0) + 1

            # Insert the new user
            sql = "INSERT INTO USERS (UID, NAME, PHONE_NUMBER, EMAIL) VALUES (%s, %s, %s, %s)"
            val = (new_uid, name, phone_number, email)
            cursor.execute(sql, val)
            connection.commit()

            print(f"User '{name}' with phone '{phone_number}' registered successfully. UID: {new_uid}")
            return new_uid

        except mysql.connector.Error as e:
            print(f"Database error during registration: {e}")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    return False


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

# --- Speaking and Listening Functions (modified for text input) ---
def speak(text, use_gtts=True, speed_factor=1.0):
    """
    Converts text to speech using gTTS (preferred) or pyttsx3 (fallback).
    Prints the text to console.
    For text-only mode, this will just print.
    """
    print(f"Trax AI: {text}")
    # CUTTING THE BYPASS FOR GTTS AGAIN
    if use_gtts:
        try:
            tts = gTTS(text=text, lang='en', slow=False) # 'slow=False' gives gTTS's fastest native speed
            original_filename = "temp_speech_original.mp3"
            processed_filename = "temp_speech_processed.mp3"
            tts.save(original_filename)

            if speed_factor != 1.0:
                audio = AudioSegment.from_mp3(original_filename)
                
                # Applied speed change. pydub's speedup function adjusts tempo.
                # A small crossfade can help smooth transitions if it causes artifacts.
                sped_audio = audio.speedup(playback_speed=speed_factor, crossfade=50) 
                
                # Export and play the processed (sped-up) audio
                sped_audio.export(processed_filename, format="mp3")
                playsound(processed_filename)
                os.remove(processed_filename) # Clean up the processed file
            else:
                # If no speed adjustment, just play the original gTTS file
                playsound(original_filename)

            os.remove(original_filename) # Clean up the original temporary file
        except Exception as e:
            print(f"Error using gTTS with speed adjustment: {e}. Falling back to pyttsx3.")
            engine_pyttsx3.say(text)
            engine_pyttsx3.runAndWait()
    else:
        engine_pyttsx3.say(text)
        engine_pyttsx3.runAndWait()

# ---- FOR USING TEXT INPUTS -----
def get_text_command():
    """Gets text input from the console."""
    command = input("User: ").lower().strip()
    return command

# --------- FOR LISTENING TO THE USER --------
def listen_command():
    """Listens for voice input and converts it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...", use_gtts=False) # Using pyttsx3 for quick system prompts
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            r.pause_threshold = 2  # Adding the pause threshold 
            audio = r.listen(source, timeout=5, phrase_time_limit=10)   # Changed the phrase limit
            print("Processing audio...")
            command = r.recognize_google(audio).lower()
            print(f"User: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I was not able to understand that audio.", use_gtts=False) # NOT REQUIRED 
            return None
        except sr.WaitTimeoutError:
            return None 
        except sr.RequestError as e:
            speak(f"Could not request results from speech recognition service; {e}", use_gtts=False)
            return None
        except Exception as e:
            speak(f"An error occurred during listening: {e}", use_gtts=False)
            return None

def get_chatbot_response(user_message, current_user_uid=None, current_user_name=None, db_query_result=None, user_preloaded_data=None):
    """
    Sends user message (and optional database query result) to Ollama and gets the chatbot response.
    """
    global chat_history

    #-- Connecting the faiss ----
    # faisprompt = faissfunc(user_message) cmf

    # ---- FOR GETTING LIVE EVENTS INFORMATION -----
    city_found = extract_city_from_command(command)
    if city_found:
        Live_events = fetch_event_names(city_found,20)
    else:
        Live_events = ""

    # --- Building Pre-loaded Data String for LLM Context ---
    preloaded_data_string = ""
    if user_preloaded_data and user_preloaded_data.get("status") == "success":
        preloaded_data_string += "\n\n--- Current User Data (Pre-loaded from Database) ---\n"

        # User Info
        user_info = user_preloaded_data.get("user_info", {})
        preloaded_data_string += "User Information:\n"
        preloaded_data_string += (
            f"  - Name: {user_info.get('NAME', 'N/A')}\n"
            f"  - Phone Number: {user_info.get('PHONE_NUMBER', 'N/A')}\n"
            f"  - Email: {user_info.get('EMAIL', 'N/A')}\n"
        )

        # Hobbies
        hobbies = user_preloaded_data.get("hobbies", [])
        if hobbies:
            preloaded_data_string += "\nUser Hobbies:\n"
            for hobby in hobbies:
                preloaded_data_string += f"  - {hobby}\n"
        else:
            preloaded_data_string += "\n  No hobbies found for this user.\n"

        # Bookmarks
        bookmarks = user_preloaded_data.get("bookmarks", [])
        if bookmarks:
            preloaded_data_string += "\nRecent Bookmarks (Last 5):\n"
            for bm in bookmarks:
                preloaded_data_string += (
                    f"  - Location: {bm['Location']}, Saved on: {bm['Timestamp']}\n"
                )
        else:
            preloaded_data_string += "\n  No bookmarks found for this user.\n"

        preloaded_data_string += f"\nData last updated at: {user_preloaded_data['timestamp']}\n"
        preloaded_data_string += "--- End Pre-loaded User Data ---\n\n"

    elif user_preloaded_data and user_preloaded_data.get("status") == "error":
        preloaded_data_string += f"\n--- Pre-loaded User Data Error: {user_preloaded_data.get('message', 'Unknown error')} ---\n\n"


    # --- Database Schema Information for LLM --- REMOVING THIS Version 1.02
    # --- User Profile Info --- Removed it for now
    
    rules_for_agent = f"""
    Only Answer Within Travel Scope: You must not answer any questions or engage in any discussions that fall outside the domain of travel and tourism. Your responses must be strictly limited to topics a user would typically ask a travel agent about, such as destinations, itineraries, transport, accommodations, travel tips, local culture, food, and weather.

    No External Information: You are strictly prohibited from accessing, searching for, or providing any information not explicitly contained within this system content or preloaded travel-related data. Do not guess or assume answers outside your travel knowledge base.

    Refusal Protocol: If User asks a question that is outside the defined travel scope (e.g., political topics, technical support, personal advice, non-travel hypotheticals), you must politely decline to answer. Use phrases such as:
        "I'm sorry, I can only help with travel-related questions."
        "My purpose is to assist you with your travel plans, so I can't answer that."
        "I'm programmed to focus only on topics related to travel and tourism."

    No Political Discussions: Under no circumstance should you respond to political questions, events, figures, or commentary. Redirect politely and stay within the travel guide role.

    No Opinion or Speculation: Do not offer personal opinions, speculate on non-travel matters, or engage in hypothetical scenarios unless they are directly related to travel (e.g., travel preferences, weather-based advice, etc.).

    Maintain Focus: Your entire interaction must remain focused on delivering a helpful, friendly, and travel-focused experience for the user. You must not deviate from the role of a virtual travel assistant.

    Emotionally Aware and Friendly: You must communicate in a warm, empathetic, and approachable tone. Recognize user emotions and respond accordingly to provide a reassuring and helpful travel planning experience.

    Use Chat History to Assist: If a user is having trouble following instructions or completing a travel-related task, check previous chat history if available and help them accordingly based on the context you have.

    Weather Forecast : If you have the data of the weather forecast for that location which user is asking then tell him in a consice way for travelling purpose.

    Don't use asterisk : When replying don't use Asterisk in the text 
    """

    # Combining all system content components
    full_system_content = rules_for_agent + preloaded_data_string + Live_events + weather_info#  + faisprompt   cmf

    messages_for_ollama = [{'role': 'system', 'content': full_system_content}] + chat_history

    # Adding the user's message to the conversation history
    messages_for_ollama.append({'role': 'user', 'content': user_message})

    # If there's a database query result, add it to the context for the LLM to process
    if db_query_result:
        # Use 'tool_result' role for database outputs for clear distinction
        messages_for_ollama.append({'role': 'tool_result', 'content': str(db_query_result)})


    try:
        client = ollama.Client(host=OLLAMA_URL)
        response_stream = client.chat(
            model=OLLAMA_MODEL,
            messages=messages_for_ollama,
            stream=True
        )

        full_response_content = ""
        # Print the LLM's response chunk by chunk to console as it arrives
        print("Trax AI: ", end="")
        for chunk in response_stream:
            content_chunk = chunk['message']['content']
            print(content_chunk, end="", flush=True)
            full_response_content += content_chunk
        print() # Newline after the full response is printed

        # Update chat history with the user's message and the LLM's full response
        chat_history.append({'role': 'user', 'content': user_message})
        chat_history.append({'role': 'assistant', 'content': full_response_content})
        return full_response_content

    except ollama.ResponseError as e:
        speak(f"Trax AI: Ollama API Error: {e}", use_gtts=False)
        speak("Trax AI: Please check if the model is downloaded and if Ollama server is healthy.", use_gtts=False)
        if chat_history and chat_history[-1]['role'] == 'user':
            chat_history.pop() # Remove the last user message if API call failed
        return "I'm having trouble connecting right now."
    except Exception as e:
        speak(f"Trax AI: An unexpected error occurred with Ollama: {e}", use_gtts=False)
        return "I encountered an internal error."

# --- Main Loop ---
if __name__ == "__main__":
    audio_file_path = "bgm.mp3"
    music_thread = threading.Thread(target=play_music_loop, args=(audio_file_path,))
    query_summary_list = []
    query_summary_location = ''
    user_verified = False
    current_user_name = None
    current_user_mobile = None
    current_user_uid = None
    user_dashboard_data = None # Initialize to None

    # New state variables for sequential verification
    waiting_for_mobile = False
    waiting_for_mpin = False
    waiting_for_bypass = False
    # This flag helps distinguish between initial prompt for verification
    # and re-prompt after failed attempt/invalid input.
    initial_verification_prompt_given = False 
    temp_mobile_for_verification = "" # Temporarily store mobile number for current verification attempt

    # Flags for registration flow
    waiting_for_registration_details = False


    speak("Hello! I am Trax AI", use_gtts=True, speed_factor=1.35)
    speak("Currently I'm in prototype phase", use_gtts=True, speed_factor=1.35)
    speak("I just need to confirm your Mobile number to proceed further", use_gtts=True, speed_factor=1.35)
    
    # Set initial state to wait for mobile number for verification
    waiting_for_mobile = True
    initial_verification_prompt_given = True
    speak("Please state your 10-digit mobile number.", use_gtts=True, speed_factor=1.35)


    while True:
        command = listen_command()
        if command is None:
            speak("I was not able to hear you, can you please repeat that", use_gtts=True, speed_factor=1.35)
            continue

        if "exit" in command or "stop" in command or "goodbye" in command or "no thanks" in command or "no queries" in command:
            speak("It was nice talking to you! Goodbye!", use_gtts=True, speed_factor=1.35)
            break

        if "bookmark" in command :
            speak("Please wait lemme check on my system", use_gtts=True, speed_factor=1.35)
            dg = ','.join(query_summary_list)
            query_summary_location = get_chatbot_response(
            f"Go through this history of the chat and give me the name of the location the user has talked about recently.Location can be anything Any city,state ,place,hotel,resturant,street - This is the chat history :{dg} \n REPLY THIS WITH ONE WORD ANSWER ONLY THE NAME OF LOCATION OTHERWISE IF THERE IS NO LOCATION THEN REPLY WITH LOCATION NOT FOUND",
                current_user_uid=current_user_uid,
                current_user_name=current_user_name,
                user_preloaded_data=user_dashboard_data
            )
            speak(f'Do you want to place a bookmark for : {query_summary_location}', use_gtts=True, speed_factor=1.35) # ADDING THE CONFRIMATION
            confirmation = get_confirmation()
            if "yes" in confirmation or "correct" in confirmation or "right" in confirmation or "yup" in confirmation or "yeah" in confirmation:
                query_status = add_user_bookmark(current_user_uid,query_summary_location)
                speak(f'BOOKMARK ADDED FOR : {query_summary_location}', use_gtts=True, speed_factor=1.35)
            else:
                speak("Oops my bad , Can you please state the location you want to bookmark", use_gtts=True, speed_factor=1.35)
                new_summary_location = get_confirmation()
                query_status = add_user_bookmark(current_user_uid,new_summary_location)
                speak(f'BOOKMARK ADDED FOR : {new_summary_location}', use_gtts=True, speed_factor=1.35)
            continue

        if "weather" in command or "forecast" in command:
            speak("Alright i'll do the weather forecast for you and will keep it in mind for future responses", use_gtts=True, speed_factor=1.35)
            dg = ','.join(query_summary_list)
            query_summary_city = get_chatbot_response(
            f"Go through this history of the chat and reply with the name of the location the user has talked about recently.This is the chat history :{dg} \n REPLY THIS WITH ONE WORD ANSWER ONLY THE NAME OF LOCATION",
                current_user_uid=current_user_uid,
                current_user_name=current_user_name,
                user_preloaded_data=user_dashboard_data
            )
            weather_info = get_weather_forecast(query_summary_city)
            continue

        
        # --- ADDING THE LOGIC FOR FORM ---
        # if contains_keyword(command) and user_verified:
        #     keyword_count += 1

        #     if keyword_count < 2:
        #         speak("I can see you might need support. Let me try to help you before we raise a ticket.", use_gtts=True, speed_factor=1.35)
        #         continue
        #     elif keyword_count >= 2:
        #         speak("It seems like you're facing persistent issues.", use_gtts=True, speed_factor=1.35)
        #         speak("Let me summarise your issue..", use_gtts=True, speed_factor=1.35)
        #         dg = ','.join(query_summary_list)
        #         query_summary = get_chatbot_response(
        #                     f"Summarise this problem user is facing in very very concisely in **one line** you should summarise it like The Users wants too... - {dg}",
        #                     current_user_uid=current_user_uid,
        #                     current_user_name=current_user_name,
        #                     user_preloaded_data=user_dashboard_data
        #                 )
        #         speak(f'Is this the issue you want to raise a ticket for?\n {query_summary}', use_gtts=True, speed_factor=1.35) # ADDING THE CONFRIMATION
        #         #  REMOVING THE BYPASS create_freshdesk_ticket(query_summary,NAME,EMAIL)   [1.25/7]
        #         confirmation = get_confirmation()
        #         # confirmation = listen_command().strip().lower()  #LS   TRYING To COPE WITH FUNCTION
        #         # for text confirmation = get_text_command().strip().lower()
        #         if "yes" in confirmation or "correct" in confirmation or "right" in confirmation or "yup" in confirmation or "yeah" in confirmation:
        #             TICKET_ID = create_freshdesk_ticket(query_summary,NAME,EMAIL)  
        #             speak(f"I have raised your issue, Your complaint ID is : {TICKET_ID}", use_gtts=True, speed_factor=1.25)
        #             speak("Our customer service executive will call you shortly", use_gtts=True, speed_factor=1.35) # will do the issue summary 
        #         else:
        #             speak("Can you please state your query again? so that i can create a ticket for you", use_gtts=True, speed_factor=1.35)
        #             new_summary = get_confirmation()
        #             #new_summary = listen_command().strip().lower()   #LS
        #         # for text    new_summary = get_text_command().strip().lower() 
        #             TICKET_ID = create_freshdesk_ticket(new_summary,NAME,EMAIL)
        #             speak(f"I have raised your issue, Your complaint ID is : {TICKET_ID}", use_gtts=True, speed_factor=1.25)
        #             speak("Our customer service executive will call you shortly", use_gtts=True, speed_factor=1.35) # will do the issue summary
        #         message_to_send = "Hey thanks for contacting us ... \n Our customer executive will contact you shortly \n <b>SHELL L1 AGENT SERVICES</b>."
        #         send_telegram_message_http(message_to_send)
        #         speak("Do you have any other queries?", use_gtts=True, speed_factor=1.35)
        #         endconfirm = get_confirmation()
        #         #endconfirm = listen_command().strip().lower()   #LS
        #         if "no" in endconfirm:
        #             speak("Thank you for using SHELL products , Have a good day", use_gtts=True, speed_factor=1.35)
        #             break
        #         else:
        #             speak("Alright i'm still here to help assist you", use_gtts=True, speed_factor=1.35)
        #             continue  # REMOVING THE BREAK AND ADDING CONTINUATION [1.25/7]

        # --- User Verification Logic (using Mobile and MPIN) ---
        if not user_verified:
            # Check if we are in the middle of a registration attempt
            if waiting_for_registration_details:
                reg_name = None
                reg_mobile = None
                reg_mpin = None

                name_pattern = re.search(r"my name is (\w+(?:\s+\w+){0,2})", command, re.IGNORECASE)
                if name_pattern:
                    reg_name = name_pattern.group(1).title()

                reg_mobile_numbers = re.findall(r'\b\d{10}\b', command)
                if reg_mobile_numbers:
                    reg_mobile = reg_mobile_numbers[0]

                reg_mpin_pattern = re.search(r"(?:mpin to be|my mpin to be)\s*(\d+)", command, re.IGNORECASE)
                if reg_mpin_pattern:
                    reg_mpin = reg_mpin_pattern.group(1)

                if reg_name and reg_mobile and reg_mpin:
                    new_uid = register_user(reg_name, reg_mobile.replace(" ",""), reg_mpin.replace(" ",""))
                    if new_uid:
                        user_verified = True
                        current_user_uid = new_uid
                        current_user_name = reg_name
                        current_user_mobile = reg_mobile.replace(" ","")
                        speak(f"Great! You're now registered as {current_user_name}. Fetching your account details...Please wait", use_gtts=True, speed_factor=1.25)
                        user_dashboard_data = fetch_user_dashboard_data(current_user_uid)
                        # print(f"[DEBUG] User Dashboard Data: {user_dashboard_data}")

                        get_chatbot_response(
                            f"Hello Trax AI! I am {current_user_name}, UID {current_user_uid}. I just registered. What can you tell me?",
                            current_user_uid=current_user_uid,
                            current_user_name=current_user_name,
                            user_preloaded_data=user_dashboard_data
                        )
                        # Reset all registration-related flags
                        waiting_for_registration_details = False
                        waiting_for_mobile = False
                        waiting_for_mpin = False
                        temp_mobile_for_verification = ""

                    else:
                        speak("I couldn't register you at this time. The mobile number might already be in use, or there was an error.", use_gtts=True, speed_factor=1.25)
                        speak("Please try again with your registration details, or type 'exit' to quit.", use_gtts=True, speed_factor=1.25)
                        # Stay in waiting_for_registration_details state to allow re-entry of details
                else:
                    speak("Trax AI: I could not extract all necessary registration details (name, mobile, MPIN). Please try again clearly.", use_gtts=True, speed_factor=1.25)
                    # Stay in waiting_for_registration_details state to allow re-entry of details
                continue # Continue the loop to wait for next command for registration or exit

            # --- If not in registration flow, proceed with login verification ---
            # Handle mobile number input for login
            if waiting_for_mobile:
                mobile_numbers = re.findall(r'\b\d{10}\b', command.replace(" ", ""))
                if mobile_numbers:
                    temp_mobile_for_verification = mobile_numbers[0]
                    speak(f"Got it. Your mobile number is {temp_mobile_for_verification}.", use_gtts=True, speed_factor=1.15)
                    waiting_for_mobile = False
                    waiting_for_mpin = False  # BYPASSING IT FOR NOW
                    waiting_for_bypass= True
                    speak("Now, please state your 4-digit MPIN.", use_gtts=True, speed_factor=1.15)
                else:
                    speak("That doesn't look like a valid 10-digit mobile number. Please try again.", use_gtts=True, speed_factor=1.15)
                    # Stay in waiting_for_mobile state to re-prompt
                    continue # Skip to the next loop iteration to get new command

            # Handle MPIN input after mobile number has been received
            elif waiting_for_bypass:
                # Assuming 4-digit MPIN based on common banking systems
                # BYPASS mpin_match = re.findall(r'\b\d{4}\b', command.replace(" ", ""))
                mpin_match = True
                if mpin_match:
                    # BYPASS mpin_input = mpin_match[0]
                    # BYPASS speak(f"Got it. Your MPIN is {mpin_input}.", use_gtts=True, speed_factor=1.15)

                    # Now that we have both, attempt verification
                    # print(f"Okay, attempting to verify with mobile {temp_mobile_for_verification} and MPIN {mpin_input}.") # NOT SPEAKING THIS AS NOT REQUIRED

                    user_details = verify_user(temp_mobile_for_verification) # Returns (UID, Username)
                    if user_details:
                        user_verified = True
                        current_user_uid = user_details[0]
                        current_user_name = user_details[1] # Get username from verification
                        current_user_mobile = temp_mobile_for_verification # Store mobile as well
                        current_user_email  = user_details[2]

                        speak(f"Welcome back, {current_user_name}! Fetching your latest account information...Please wait", use_gtts=True, speed_factor=1.15)
                        user_dashboard_data = fetch_user_dashboard_data(current_user_uid)
                        # print(f"[DEBUG] User Dashboard Data: {user_dashboard_data}")
                        music_thread.start()
                        # Initial greeting to the LLM with pre-loaded data
                        get_chatbot_response(
                            f"Hello Trax AI! I am {current_user_name}, UID {current_user_uid}.How can you help me , give very consice replies?",
                            current_user_uid=current_user_uid,
                            current_user_name=current_user_name,
                            user_preloaded_data=user_dashboard_data
                        )
                        stop_music_flag.set()  ### USING FOR MUSIC TO STOP
                        # Reset verification state variables as verification is complete
                        waiting_for_mobile = False
                        waiting_for_mpin = False
                        initial_verification_prompt_given = False
                        NUMBER = temp_mobile_for_verification #not removing it for using in ticket
                        NAME = current_user_name
                        EMAIL = current_user_email
                        #temp_mobile_for_verification = "" #Though we can remove here

                    else:
                        speak("Verification failed. Mobile number or MPIN is incorrect. Would you like to register as a new user? Type 'yes' to register or 'no' to try again.", use_gtts=True, speed_factor=1.15)
                        # Reset for re-attempt of verification
                        waiting_for_mobile = False # Temporarily turn off mobile waiting
                        waiting_for_mpin = False # Temporarily turn off mpin waiting
                        temp_mobile_for_verification = "" # Clear temporary mobile number
                        # The next command will determine if registration or re-try login
                else:
                    speak("That doesn't look like a valid 4-digit MPIN. Please try again.", use_gtts=True, speed_factor=1.15)
                    # Stay in waiting_for_mpin state to re-prompt
                    continue # Skip to the next loop iteration to get new command
            
            # --- Handle post-failed verification choice (register or retry login) ---
            # This block will be reached if verify_user returned None AND we are not waiting for mobile/mpin
            # (meaning the last step was the failed verification attempt)
            elif not waiting_for_mobile and not waiting_for_mpin:
                # We've already spoken the "Would you like to register..." part, so just listen for response
                register_response = command # Use the current command from listen_command()

                if "yes" in register_response or "sure" in register_response or "register me" in register_response:
                    speak("To register, please tell me your full name, your mobile number, and an MPIN you'd like to set.", use_gtts=True, speed_factor=1.15)
                    speak("For example: 'My name is <yourname>, my mobile is 98XXXXXXXX and I want my mpin to be XXXX'.", use_gtts=True, speed_factor=1.15)
                    waiting_for_registration_details = True # Set flag for registration flow
                    
                else: # User chose not to register, or provided unclear response, so retry login
                    speak("Trax AI: Okay, let's try logging in again. Please state your 10-digit mobile number.", use_gtts=True, speed_factor=1.25)
                    waiting_for_mobile = True # Go back to asking for mobile number
                    initial_verification_prompt_given = False # Reset for re-attempt

        else: # If user_verified is True, proceed with normal chatbot interaction
            # Pass the latest command along with current user details and pre-loaded data
            query_summary_list.append(command)
            response_text= get_chatbot_response(
                    command,
                    current_user_uid=current_user_uid,
                    current_user_name=current_user_name,
                    user_preloaded_data=user_dashboard_data # Pass the pre-loaded data
                )
            speak(response_text, use_gtts=True, speed_factor=1.25)
