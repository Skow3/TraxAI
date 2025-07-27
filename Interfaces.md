# TraxAI Interfaces

TraxAI supports multiple interfaces to enable voice-based, multilingual access across various platforms. This document describes each available interface, how it works, and how to run it locally for development and testing.

---

## Table of Contents

1. [Telegram Bot (Voice Access)](#1-telegram-bot-voice-access)  
2. [Web UI](#2-web-ui)  
3. [Twilio Call Simulation (Python Script)](#3-twilio-call-simulation-python-script)  
4. [Environment Configuration](#4-environment-configuration)  
5. [Recommended File Structure](#5-recommended-file-structure)  
6. [Notes](#6-notes)

---

## 1. Telegram Bot (Voice Access)

This interface allows users to interact with TraxAI via voice messages sent to a Telegram bot.

### How It Works

- The user sends a voice message to the Telegram bot.
- The bot transcribes the message using Whisper (or other STT).
- Based on the message, user mood, and location, TraxAI generates a personalized response.
- The response is returned to the user as text or voice (optional).
- Different options are there such as User-log in, Bookmark, Hobbies


### How to Run
1. Make sure your `.env` includes the following:

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    ```

2. Run the Telegram bot handler script:

    ```bash
    python interfaces/telegram_bot.py
    ```

3. Open Telegram and send a voice message to your bot.  
4. The bot will respond with a relevant message, simulating a smart, local guide.

---

## 2. Web UI

A browser-based interface for voice or text interaction with TraxAI. This is useful for testing the system without relying on messaging platforms.

### How It Works

- Users can upload a voice file, record audio, or type a message.
- The input is sent to the backend for processing.
- The backend returns a response that is displayed on the web page.
- The response is softely spoken too.

### How to Run

1. Start using streamlit:

    ```bash
    streamlit run app.py
    ```

2. Open your browser and go to:

    ```
    http://localhost:5000/
    ```

3. Use the UI to test voice or text-based queries.

---

## 3. Twilio Call Simulation (Python Script)

This is a mock interface that simulates Twilio phone call interactions via a Python script. It's used for local testing since Twilio does not allow dynamic script hosting on the free tier.

### How It Works

- The script simulates a user "calling" the system with predefined or recorded input.
- The backend processes the input as if it came from Twilio's voice pipeline.
- The system returns a synthesized response (text or voice), mimicking a real call flow.

### How to Run

1. Run the Twilio simulation script:

    ```bash
    python interfaces/twilio_simulation.py
    ```

2. Provide sample input or trigger the simulation.

3. For future deployment, the logic in this script can be connected to a live Twilio phone number by configuring webhooks.

4. Include the following in your `.env` for future use:

    ```env
    TWILIO_ACCOUNT_SID=your_sid
    TWILIO_AUTH_TOKEN=your_token
    ```

---

## 4. Environment Configuration

Ensure your `.env` file (placed in the root of your project) includes all the necessary API keys and tokens:

```env
OPENAI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
GOOGLE_TTS_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_key_here
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
