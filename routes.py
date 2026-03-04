from flask import render_template, url_for, flash, redirect, request, session
from app import app, db, bcrypt, limiter
from models import User
from auth_utils import generate_otp_secret, generate_otp, verify_totp, send_otp_email
import datetime

@app.route('/')
def home():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation checks
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username is already taken. Please choose another one.', 'error')
        elif email_exists:
            flash('Email is already registered. Please log in instead.', 'error')
        else:
            # Secure insertion
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password_hash=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # No account found with this username
            flash('No account found with that username. Please register first.', 'error')
        elif user.email != email or not bcrypt.check_password_hash(user.password_hash, password):
            # User exists but email or password is wrong
            flash('Incorrect email or password. Please try again.', 'error')
        else:
            # Primary auth success - Generate OTP
            otp_secret = generate_otp_secret()
            session['otp_secret'] = otp_secret
            session['pre_auth_user'] = user.username
            session['otp_retries'] = 0
            
            # Generate OTP code
            code, expires_at = generate_otp(otp_secret)
            session['otp_expires_at'] = expires_at.timestamp()
            
            # Send Email
            try:
                send_otp_email(user.email, code)
                flash('An OTP has been sent to your email address.', 'info')
            except Exception as e:
                print(f"Mail error: {e}")
                flash('Failed to send OTP email. Please check server configuration.', 'error')
            
            return redirect(url_for('verify_otp_route'))
            
    return render_template('login.html', title='Login')

@app.route('/verify_otp', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def verify_otp_route():
    if 'pre_auth_user' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        secret = session.get('otp_secret')
        expires_at = session.get('otp_expires_at')
        retries = session.get('otp_retries', 0)
        
        # Check expiration
        if datetime.datetime.now().timestamp() > expires_at:
            session.pop('pre_auth_user', None)
            flash('OTP expired. Please login again.', 'error')
            return redirect(url_for('login'))
            
        # Check retries
        if retries >= 3:
            session.pop('pre_auth_user', None)
            flash('Maximum OTP attempts reached. Please login again.', 'error')
            return redirect(url_for('login'))
            
        if verify_totp(secret, entered_otp):
            # OTP verified successfully
            session['authenticated'] = True
            session['user'] = session['pre_auth_user']
            # Clean up pre-auth state
            session.pop('pre_auth_user', None)
            session.pop('otp_secret', None)
            
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            session['otp_retries'] = retries + 1
            flash(f'Invalid OTP. Attempts remaining: {3 - session["otp_retries"]}', 'error')
            
    return render_template('otp.html', title='Verify OTP')

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', title='Dashboard', username=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
