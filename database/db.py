from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
import os
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), default='')
    language = db.Column(db.String(2), default='RU')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    novels = db.relationship('Novel', backref='author', lazy=True)

class Novel(db.Model):
    __tablename__ = 'novel'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    cover_image = db.Column(db.String(200), default='')
    is_published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scenes = db.relationship('Scene', backref='novel', lazy=True, order_by='Scene.order')

class Scene(db.Model):
    __tablename__ = 'scene'
    
    id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    background = db.Column(db.String(200), default='')
    text = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    _choices = db.Column('choices', db.Text, default='[]')  # Переименуем поле
    
    # Свойство для работы с choices как со списком
    @hybrid_property
    def choices(self):
        if self._choices and self._choices != '[]':
            try:
                return json.loads(self._choices)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @choices.setter
    def choices(self, value):
        if isinstance(value, list):
            self._choices = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            # Проверяем, является ли строка валидным JSON
            try:
                json.loads(value)  # Проверка валидности
                self._choices = value
            except (json.JSONDecodeError, TypeError):
                self._choices = '[]'
        else:
            self._choices = '[]'

# Добавляем обработчик событий для автоматического преобразования
@event.listens_for(Scene, 'before_insert')
@event.listens_for(Scene, 'before_update')
def before_scene_save(mapper, connection, target):
    """Автоматически преобразуем choices в JSON при сохранении"""
    if hasattr(target, '_choices'):
        # Если choices установлено через сеттер, оно уже преобразовано
        # Но на всякий случай проверим
        if isinstance(target._choices, list):
            target._choices = json.dumps(target._choices, ensure_ascii=False)
        elif target._choices is None:
            target._choices = '[]'