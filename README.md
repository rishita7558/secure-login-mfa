# Secure MFA Authentication System

A premium Flask-based authentication dashboard demonstrating primary login combined with Email-based One-Time Password (OTP) Multi-Factor Authentication.

## Core Features
*   **Primary Auth**: Secure Bcrypt password hashing and SQLite user storage.
*   **MFA (Multi-Factor)**: Time-based 6-digit OTPs distributed securely via the Brevo REST API.
*   **Security Mechanisms**:
    *   OTP Expirations (3-minute lifetime).
    *   Max Retry Lockouts (3 attempts).
    *   Brute-force rate limiting via `Flask-Limiter`.
*   **Premium UI**: Custom responsive Glassmorphism design and Google Fonts.

## Local Installation & Setup
1. Clone the repository.
2. Initialize the virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Initialize the development database dummy user:
   ```bash
   python db_init.py
   ```
4. Run the Flask Server:
   ```bash
   python app.py
   ```
5. Navigate to `http://localhost:5000` to demo the login.

## Production / Deployment (Render.com)
This application requires a Python backend to execute safely (it cannot be hosted on static hosts like GitHub Pages). It is pre-configured with `gunicorn` for seamless deployment to platforms like **Render.com**.

1. Create a [Render](https://render.com/) account.
2. Link your GitHub repository and Select **Web Service**.
3. Use the following configuration:
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
4. Render will seamlessly build and deploy the Python app and generate a secure, live HTTPS link!
