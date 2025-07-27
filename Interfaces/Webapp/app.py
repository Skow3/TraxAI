import streamlit as st
from gtts import gTTS
from tempfile import NamedTemporaryFile
import os
from fpdf import FPDF
import ollama
import speech_recognition as sr

# ------------------------- Language Mapping -----------------------------
language_code_map = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-cn",
    "Arabic": "ar"
}

# ------------------------- Streamlit Page Config ------------------------
st.set_page_config(page_title="TraxAI City Guide", layout="centered")
col1, col2, col3 = st.columns([2,1,2])
with col2:
    st.image("tw.png", width=200, use_container_width =False)
st.markdown(
    '<h1 style="text-align:center;>TraxAI Assistant</h1>'
    '<h5 style="color:var(--text);text-align:center;">Your 24/7 Personal Travel Guide</h5>',
    unsafe_allow_html=True
)
# ------------------------- Sidebar Settings -----------------------------
st.sidebar.title("Settings")
language = st.sidebar.selectbox("Output Language", list(language_code_map.keys()))
language_code = language_code_map[language]

interaction_mode = st.sidebar.radio("Choose Input Mode", ["Text Chat", "Voice Chat"])
voice_speed = st.sidebar.slider("Voice Speed", min_value=0.5, max_value=1.5, step=0.1, value=1.0)
st.sidebar.markdown("📲 [Chat on Telegram](https://t.me/explore_india_voicebot)")

# ------------------------- Session State -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------- Ollama Response ------------------------------
def generate_response(prompt):
    full_prompt = f"You are TraxAI, a helpful, multilingual city guide. Respond in {language}."
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

# ------------------------- TTS Function --------------------------------
def speak_text(text, lang_code, speed):
    tts = gTTS(text=text, lang=lang_code, slow=(speed < 0.8))
    with NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# ------------------------- PDF Export ----------------------------------
def export_pdf(chat_history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for sender, msg in chat_history:
        pdf.multi_cell(0, 10, f"{sender}: {msg}")
    with NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdf.output(f.name)
        return f.name

# ------------------------- MP3 Export ----------------------------------
def export_mp3(text, lang_code, speed):
    return speak_text(text, lang_code, speed)

# ------------------------- Voice Input ---------------------------------
def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak now...")
        audio = recognizer.listen(source, timeout=5)
    try:
        st.success("Voice received. Processing...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("Sorry, couldn't understand.")
        return ""
    except sr.RequestError:
        st.error("Voice service not available.")
        return ""

# ------------------------- Chat Interface ------------------------------
user_input = ""
if interaction_mode == "Text Chat":
    with st.form("text_form", clear_on_submit=True):
        user_input = st.text_input("💬 Type your message:")
        submit = st.form_submit_button("Send")
        if submit and user_input:
            st.session_state.chat_history.append(("You", user_input))
            reply = generate_response(user_input)
            st.session_state.chat_history.append(("TraxAI", reply))
            audio_file = speak_text(reply, language_code, voice_speed)
            st.audio(audio_file, format="audio/mp3", autoplay=True)

elif interaction_mode == "Voice Chat":
    if st.button("🎤 Start Voice Input"):
        user_input = recognize_voice()
        if user_input:
            st.session_state.chat_history.append(("You", user_input))
            reply = generate_response(user_input)
            st.session_state.chat_history.append(("TraxAI", reply))
            st.write("TraxAI:", reply)
            audio_file = speak_text(reply, language_code, voice_speed)
            st.audio(audio_file, format="audio/mp3", autoplay=True)

# ------------------------- Chat History -------------------------------
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("🕘 Chat History")
    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {message}")

# ------------------------- Export Buttons ------------------------------
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Download Chat PDF"):
        pdf_path = export_pdf(st.session_state.chat_history)
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="chat.pdf")
with col2:
    if st.button("🔊 Download Audio"):
        text = " ".join([msg for sender, msg in st.session_state.chat_history if sender == "TraxAI"])
        mp3_path = export_mp3(text, language_code, voice_speed)
        with open(mp3_path, "rb") as f:
            st.download_button("Download MP3", f, file_name="chat.mp3")

# ------------------------- Auto-Enter Script ---------------------------
st.markdown("""
    <script>
    const inputBox = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (inputBox) {
        inputBox.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                window.parent.document.querySelector('button[kind="primary"]').click();
            }
        });
    }
    </script>
""", unsafe_allow_html=True)
