# 🐯 Chandrapur Wildlife Conflict Tracking & Prediction System

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Twilio](https://img.shields.io/badge/Twilio-Voice_IVR-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper_STT-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![scikit-learn](https://img.shields.io/badge/scikit_learn-ML_Modeling-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

An end-to-end AI-powered system designed for forest departments and rural communities around the **Tadoba-Andhari Tiger Reserve (TATR), Chandrapur, Maharashtra**. 

The system combines an **automated multilingual AI Voice Helpline (IVR)**, **Speech-to-Text (Whisper)**, **LLM structured extraction**, **SQLite persistence**, and a **live auto-refreshing geospatial Streamlit dashboard** with **Random Forest conflict prediction**.

---

## 🌟 Key Highlights

### 1. 📞 AI Multilingual Voice Helpline & Emergency Alerting (`webhook.py`, `test_call.py`)
Villagers in rural fringe areas often cannot use smartphone apps with poor internet connectivity. This system provides a standard phone helpline:
* **Interactive Voice Response (IVR)**: Greets callers in Hindi via Twilio Voice API (`/incoming-call`).
* **Speech-to-Text (STT)**: Transcribes spoken messages in Hindi, Marathi, or English using OpenAI **Whisper**.
* **Zero-Shot Information Extraction**: Uses **Gemma 2 (via OpenRouter)** to extract structured data from spoken transcripts into JSON (`animal`, `village`, `severity`, `incident description`).
* **Instant DB Persistence**: Maps village locations to GPS coordinates and inserts incidents directly into SQLite (`data/wildlife.db`).
* **Live Sync**: The Streamlit dashboard automatically re-polls the database every 5 seconds, plotting newly reported conflicts without manual page reload.

### 2. 🗺️ Geospatial Conflict Intelligence Dashboard (`app.py`)
* **Interactive Incident Map**: Folium-powered interactive map with color-coded markers for Tigers, Leopards, Elephants, Sloth Bears, and Wild Boars.
* **Tadoba Core & Buffer Boundaries**: Official GeoJSON boundary visualization for the Core and Andhari Buffer zones.
* **Kernel Density Heatmap**: Identifies active conflict zones and recurring wildlife corridor pressure points.
* **Multivariate Filtering**: Temporal, seasonal, and severity breakdown of all recorded conflicts.

### 3. 🔮 Predictive Hotspot Machine Learning (`model/train.py`)
* **Model**: Random Forest Classifier with cross-validation and hyperparameter constraints to prevent overfitting.
* **Features**: Geographic coordinates (lat/lon), Month, Day of Week, Season, Village, and Severity.
* **Output**: Predicts probable wildlife species and hotspot risks to enable proactive ranger patrolling.

---

## 🏗️ System Architecture

```
[ Rural Caller / Villager ]
           │
           ▼  (Phone Call)
   [ Twilio Voice IVR ]
           │
           ▼  (Audio Webhook)
  [ Flask Server (webhook.py) ]
           │
     ┌─────┴─────────────────────────┐
     ▼                               ▼
[ OpenAI Whisper ]        [ Gemma 2 LLM (OpenRouter) ]
(Audio -> Hindi/Marathi)   (Extract Animal, Village, Severity)
     └─────┬─────────────────────────┘
           │
           ▼  (Structured Record)
 [ SQLite Database (wildlife.db) ]
           │
           ▼  (5-second auto-poll)
[ Streamlit Geospatial Dashboard ] ──> [ Random Forest ML Predictor ]
```

---

## 📁 Repository Structure

```
ForestConflict/
├── app.py                  # Live Streamlit dashboard & map UI
├── webhook.py              # Twilio IVR, Whisper transcription & LLM extraction
├── test_call.py            # Automated script to trigger outbound alerts
├── setup_db.py             # Database initialization & CSV migration script
├── mapdata.py              # Static geospatial coordinate reference
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules for keys, weights, and caches
├── README.md               # Documentation
├── data/
│   ├── generate_data.py    # Synthetic historical incident generator
│   └── tadoba.geojson      # Tadoba reserve boundaries (GeoJSON)
├── model/
│   └── train.py            # Random Forest training & hotspot prediction
└── utils/
    ├── map_utils.py        # Folium mapping & heatmap builders
    ├── filters.py          # Dashboard filtering & metrics widgets
    └── helpline.py         # Helpline utility helpers
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.10+
* (Optional for Voice Helpline) [Twilio Account](https://www.twilio.com/) & [OpenRouter API Key](https://openrouter.ai/)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/<YOUR_USERNAME>/ForestConflict.git
cd ForestConflict

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```
Fill in:
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
MY_PHONE_NUMBER=your_personal_number_to_receive_calls
OPENROUTER_API_KEY=your_openrouter_api_key
NGROK_URL=https://your-ngrok-domain.ngrok-free.dev
```

### 4. Initialize Database
Generate initial conflict dataset and populate SQLite:
```bash
python data/generate_data.py
python setup_db.py
```

### 5. Launch the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📞 Running the Voice Helpline & Live Alerting

1. Start the Flask webhook server:
   ```bash
   python webhook.py
   ```
2. In a separate terminal, expose port 5000 via ngrok:
   ```bash
   ngrok http 5000
   ```
3. Set your Twilio phone number's Voice Webhook to:
   `https://<your-ngrok-subdomain>.ngrok-free.dev/incoming-call`
4. Trigger a test call:
   ```bash
   python test_call.py
   ```
5. Answer the call, speak your message in Hindi/English (e.g., *"Moharli gaon ke pass ek tiger dekha gaya"*), and watch the live Streamlit dashboard automatically update with a new map marker!

---

## 🛡️ License & Acknowledgements
Developed for academic research and forest wildlife management around Tadoba-Andhari Tiger Reserve, Chandrapur.
