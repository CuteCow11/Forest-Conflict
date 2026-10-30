import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load your Twilio credentials from your .env file
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
target_number = os.getenv("MY_PHONE_NUMBER")
ngrok_url = os.getenv("NGROK_URL", "https://your-ngrok-url.ngrok-free.dev")

if not account_sid or not auth_token:
    raise ValueError("Twilio credentials missing. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in your .env file.")

client = Client(account_sid, auth_token)

# Trigger outbound call via Twilio
call = client.calls.create(
    to=target_number,
    from_=twilio_number,
    url=f"{ngrok_url.rstrip('/')}/incoming-call"
)

print(f"Calling {target_number} now! Call SID: {call.sid}")
