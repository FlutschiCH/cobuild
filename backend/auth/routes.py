from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from models import User
from extensions import db, oauth
from config import Config
from flask_login import login_user, logout_user, login_required, current_user
import uuid

auth = Blueprint('auth', __name__)

# Register Google OAuth
oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 409

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'userId': new_user.id}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    print(f"--> Login Attempt: {email}")

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        print(f"    ❌ User not found in DB: {email}")
    elif not user.check_password(password):
        print(f"    ❌ Password mismatch for: {email}")
    else:
        print(f"    ✅ Login credentials valid for: {email}")

    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'subscription_status': user.subscription_status,
                'subscription_plan': user.subscription_plan
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    # Ensure we use the correct protocol/domain if behind a proxy or in dev
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/login/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo') or oauth.google.userinfo()
        
        email = user_info.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user from Google info
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        
        login_user(user, remember=True)
        return redirect('/')
        
    except Exception as e:
        return jsonify({'error': f'Google login failed: {str(e)}'}), 400

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth.route('/me')
def me():
    if not current_user.is_authenticated:
        return jsonify({'authenticated': False}), 401
        
    return jsonify({
        'authenticated': True,
        'user_id': current_user.id,
        'email': current_user.email,
        'role': current_user.role,
        'subscription_status': current_user.subscription_status,
        'subscription_plan': current_user.subscription_plan
    })
