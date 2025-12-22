import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/visual_novel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False