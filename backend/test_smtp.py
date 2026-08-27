import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("SMTP_HOST")
port = int(os.getenv("SMTP_PORT", 587))
user = os.getenv("SMTP_USER")
password = os.getenv("SMTP_PASSWORD")

try:
    print(f"Connecting to {host}:{port} as {user}...")
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(user, password)
    print("SUCCESS: SMTP Authentication successful!")
    server.quit()
except Exception as e:
    print(f"FAILED: {e}")
