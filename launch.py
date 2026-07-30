import os
import subprocess
import time
from pyngrok import ngrok
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")

if not ngrok_token:
    raise ValueError("NGROK_AUTH_TOKEN not found in .env file")

ngrok.set_auth_token(ngrok_token)

print("Starting Streamlit...")
subprocess.Popen(['streamlit', 'run', 'app.py', '--server.port', '8501', '--server.headless', 'true'])

print("Waiting for model to load...")
time.sleep(90)

print("Creating ngrok tunnel...")
public_url = ngrok.connect(8501)
print(f"App is live at: {public_url}")
