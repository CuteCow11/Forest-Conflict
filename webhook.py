# Author: Krish Shukla
# Roll Number: 240101017

import os
import json
import tempfile
import requests
import whisper
import numpy as np
import pandas as pd
import sqlite3  # <-- ADDED for database support
from openai import OpenAI
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables (Make sure OPENROUTER_API_KEY is in your .env!)
load_dotenv()

app = Flask(__name__)

ACCOUNT_SID        = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN         = os.getenv("TWILIO_AUTH_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_PATH            = "data/wildlife.db"  # <-- CHANGED to point to your SQLite database

VILLAGE_COORDS = {
    "Moharli":   (20.1500, 79.3300),
    "Navegaon":  (20.0900, 79.2900),
    "Kolara":    (20.2000, 79.3500),
    "Jamni":     (20.2500, 79.4000),
    "Pangdi":    (20.3000, 79.3000),
    "Madnapur":  (20.1800, 79.4500),
    "Khadsangi": (20.3500, 79.5000),
    "Agarzari":  (20.1200, 79.3800),
    "Zari":      (20.2800, 79.2800),
    "Tadoba":    (20.2300, 79.3700),
    "Devada":    (20.3800, 79.4200),
    "Kesalwada": (20.1500, 79.5000),
    "Sindewahi": (20.2800, 79.4800),
    "Pombhurna": (20.3500, 79.5200),
}

COLOR_MAP = {
    "Tiger":      "red",
    "Leopard":    "orange",
    "Elephant":   "gray",
    "Wild Boar":  "green",
    "Sloth Bear": "purple",
}


@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    """Twilio calls this when someone dials your number."""
    response = VoiceResponse()

    # Greet the caller in Hindi
    response.say(
        "Namaskar. Aap Chandrapur Van Vibhag ke helpline par hain. "
        "Kripya apna sandesh beep ke baad bolein. "
        "Apna gaon, janwar, aur ghatna ka vivran dijiye.",
        language="hi-IN"
    )

    # Record the message (max 60 seconds)
    response.record(
        max_length=60,
        action="/handle-recording",
        recording_status_callback="/recording-complete",
        transcribe=False,
    )

    return Response(str(response), mimetype='text/xml')


@app.route("/handle-recording", methods=["POST"])
def handle_recording():
    """Called after recording completes."""
    response = VoiceResponse()
    response.say(
        "Dhanyavaad. Aapka sandesh record ho gaya hai. "
        "Van vibhag jald hi aapke paas aayega.",
        language="hi-IN"
    )
    response.hangup()
    return Response(str(response), mimetype='text/xml')


@app.route("/recording-complete", methods=["POST"])
def recording_complete():
    """Called when recording is fully processed — transcribe + extract + save."""
    recording_url = request.form.get("RecordingUrl")
    caller        = request.form.get("Called", "Unknown")

    print(f"📞 New call from: {caller}")
    print(f"🎙️ Recording URL: {recording_url}")

    if not recording_url:
        return "No recording URL", 400

    # ── Step 1: Download recording ────────────────────
    audio_response = requests.get(
        recording_url + ".mp3",
        auth=(ACCOUNT_SID, AUTH_TOKEN)
    )

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".mp3"
    ) as tmp:
        tmp.write(audio_response.content)
        tmp_path = tmp.name

    # ── Step 2: Transcribe with Whisper ───────────────
    print("🤖 Transcribing with Whisper...")
    whisper_model = whisper.load_model("base")
    result        = whisper_model.transcribe(tmp_path)
    transcript    = result["text"]
    os.unlink(tmp_path)

    print(f"📝 Transcript: {transcript}")

    # ── Step 3: Extract with OpenRouter (Gemma 3) ─────
    print("✨ Extracting with Gemma 2...")
    
    # Initialize the OpenRouter Client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
You are helping the Chandrapur Forest Department register wildlife
conflict incidents from call transcripts. The caller may speak in
Hindi, Marathi, or English.

Extract these fields from the transcript:
- animal: one of [Tiger, Leopard, Elephant, Wild Boar, Sloth Bear]
- incident: brief description in English
- village: village name mentioned
- severity: one of [Low, Medium, High]

Return ONLY valid JSON, no markdown, no explanation.

Transcript: \"\"\"{transcript}\"\"\"
"""
    
    # Call a more reliable free OpenRouter model
    try:
        completion = client.chat.completions.create(
            model="google/gemma-2-9b-it:free", # <-- CHANGED to bypass rate limits
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        text = completion.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        
        extracted = json.loads(text)
    except Exception as e:
        print(f"⚠️ Extraction Error: {e}")
        extracted = {
            "animal":   "Unknown",
            "incident": transcript[:100],
            "village":  "Unknown",
            "severity": "Medium",
        }

    print(f"✅ Extracted: {extracted}")

    # ── Step 4: Save to SQLite Database ───────────────────────────
    village = extracted.get("village", "Tadoba")
    animal  = extracted.get("animal", "Unknown")
    lat, lon = VILLAGE_COORDS.get(village, (20.25, 79.38))
    lat = round(lat + np.random.uniform(-0.01, 0.01), 4)
    lon = round(lon + np.random.uniform(-0.01, 0.01), 4)
    color = COLOR_MAP.get(animal, "blue")
    incident = extracted.get("incident", "Unknown")
    severity = extracted.get("severity", "Medium")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Connect to database and insert the new row securely
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO incidents (date, village, animal, incident, lat, lon, severity, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (date_str, village, animal, incident, lat, lon, severity, color))
        
        conn.commit()
    except Exception as e:
        print(f"⚠️ Database Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    print(f"✅ Incident registered to Database: {animal} at {village}")
    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000, debug=False)