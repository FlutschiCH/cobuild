import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://user:password@host/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    LOVABLE_FRONTEND_URL = os.environ.get('LOVABLE_FRONTEND_URL') or 'http://localhost:3000'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH') or 'cert/cert.pem'
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH') or 'cert/key.pem'
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
