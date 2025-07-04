import os

class Config:
    SECRET_KEY = 'your-secret-key'  # замените на os.environ.get("SECRET_KEY") в проде
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    WTF_CSRF_ENABLED = True  # Включить CSRF
