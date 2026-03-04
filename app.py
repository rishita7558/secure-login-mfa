from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Use a strong, unpredictable secret key in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database Configuration
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # For external databases (e.g. Vercel Postgres, Supabase)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif os.environ.get('VERCEL'):
    # Vercel serverless environment is read-only except for /tmp
    # Note: SQLite on Vercel is ephemeral and resets on each invocation!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
else:
    # Standard fallback for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Settings
# We are using the Brevo REST API directly via requests instead of Flask-Mail.
app.config['BREVO_API_KEY'] = os.environ.get('BREVO_API_KEY', '')
app.config['BREVO_SENDER_EMAIL'] = os.environ.get('BREVO_SENDER_EMAIL', 'rishitasaladi2007@gmail.com')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Import models and routes later
from routes import *

# Initialize SQLite tables automatically on server start
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
