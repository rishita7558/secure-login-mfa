from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    # optionally store secret for time-based OTP directly here, but for this simple app
    # we'll generate standard One Time Passwords per session

    def __repr__(self):
        return f"User('{self.username}')"
