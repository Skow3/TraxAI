# How to Run TraxAI Locally

This guide walks you through setting up and running TraxAI on your local machine.

---

## 1. Prerequisites

Make sure you have the following installed:

- Python 3.10 or higher  
- `pip` package manager  
- Git  
- A virtual environment tool (optional but recommended)

You will also need API keys for:

- TelegramBot  
- WeatherAPI (for location forecast awareness)  
- Text-to-Speech (Google Cloud TTS or equivalent)  

---

## 2. Clone the Repository

```bash
git clone https://github.com/your-username/TraxAI.git
cd TraxAI
```

## 3. SET-UP Environment variables
```txt
GOOGLE_TTS_API_KEY=your_key_here
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TELEGRAM_BOT_TOKEN=your_token_here
WEATHERAPI_ACESSTOKEN =your_token_here
```

## 4. Install Dependencies
Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows
```

Then install the dependencies:
```bash
pip install -r requirements.txt
```


