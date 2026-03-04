import pyotp
import secrets
import string
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import requests
from app import app

def generate_otp_secret():
    """Generate a random base32 string for pyotp."""
    return pyotp.random_base32()

def generate_otp(secret):
    """Generate a 6-digit TOTP code and its expiration time."""
    totp = pyotp.TOTP(secret, interval=180) # 3 minutes valid
    code = totp.now()
    expires_at = datetime.now() + timedelta(minutes=3)
    return code, expires_at

def verify_totp(secret, code):
    """Verify a TOTP code."""
    totp = pyotp.TOTP(secret, interval=180)
    return totp.verify(code)

def send_otp_email(email_addr, code):
    """Send the specific OTP code to an email address via Brevo HTTP API."""
    print(f"DEBUG: Attempting to send email to {email_addr} with OTP {code} via Brevo API")
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": app.config['BREVO_API_KEY'],
        "content-type": "application/json"
    }

    html_content = f'''
    <html><body>
    <h2>Hello!</h2>
    <p>Your One-Time Password for login is: <strong>{code}</strong></p>
    <p>This code will expire in 3 minutes.</p>
    <p>Please do not share this code with anyone.</p>
    <p><em>If you did not initiate this login request, please ignore this email.</em></p>
    </body></html>
    '''

    payload = {
        "sender": {
            "name": "Secure MFA App",
            "email": app.config['BREVO_SENDER_EMAIL']
        },
        "to": [{"email": email_addr}],
        "subject": "Your Login Verification Code",
        "htmlContent": html_content
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"DEBUG: Brevo API HTTP {response.status_code} - Success!")
    except Exception as e:
        print(f"DEBUG EXCEPTION in auth_utils.send_otp_email: {type(e).__name__}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Brevo API Error Detail: {e.response.text}")
        raise e

def generate_random_password(length=12):
    """Generate a random password if needed."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))
