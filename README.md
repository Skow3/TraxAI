# TraxAI – The Voice-First AI Travel Guide
**TraxAI** is an intelligent, voice-powered travel agent that helps users explore cities with local insight, real-time guidance, and multilingual interaction—all through a simple phone call or voice message.

This project was developed for Hack-a-tone 2025, organized by IIT Delhi and GydeXP.

---

## Project Overview
TraxAI bridges the gap between travelers and authentic local experiences. It is designed for those who want to navigate a new city like a local, without needing another app, fluent language skills, or constant internet connectivity.

Whether you're looking for hidden landmarks, interesting local stories, or personalized recommendations, TraxAI delivers them through natural conversation, contextual awareness, and voice-first interaction.

---

## Key Features

- **Context Awareness**  
  Detects user intent, tone, and mood to offer relevant suggestions and adaptive responses.

- **Conversational Storytelling**  
  Delivers historical and cultural insights through engaging narratives, not static facts.

- **Multilingual Support**  
  Understands and responds in the user’s native language using dynamic translation pipelines.

- **Location-Based Recommendations**  
  Offers real-time suggestions for nearby places based on user location and preferences.

- **Voice-Only Access**  
  Works entirely through voice calls or voice notes, requiring no installation or user setup.

---

## Additional Capabilities

- **Mood-Based Itineraries**  
  Adjusts plans and suggestions based on how the user feels and how their day evolves.
- **Voice-Activated Bookmarks**  
  Allows users to bookmark places or experiences by speaking a command.
- **Audio-Guided Adventures**  
  Offers optional immersive city walks with narrative-driven voice guidance.

---

## Tech Stack
- **Languages and Frameworks:** Python, Streamlit  
- **Speech Processing:** OpenAI Whisper, Speech-Recognition ,Pysound
- **Text-to-Speech / Translation:** Google Cloud TTS,  
- **Voice Integration:** Telegram Voice Bot , Twilio[we can integrate in future
- **Mapping and Location Services:** Book-My-Show webscraping using Selenium  
- **Conversational Logic:** Custom LLM Model , Prompting

---

## How to Run Locally

```bash
git clone https://github.com/your-username/TraxAI.git
cd TraxAI

# Set up environment variables (.env)
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
