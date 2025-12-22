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
    name = db.Column(db.String(100), default='')
    background = db.Column(db.String(200), default='')
    text = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    choices = db.Column(db.Text, default='[]')
    sprites = db.Column(db.Text, default='[]')
    
    # Свойства для удобной работы с JSON данными
    @property
    def choices_list(self):
        """Возвращает choices как список Python"""
        if self.choices and self.choices != '[]':
            try:
                return json.loads(self.choices)
            except:
                return []
        return []
    
    @choices_list.setter
    def choices_list(self, value):
        """Устанавливает choices из списка Python"""
        if isinstance(value, list):
            self.choices = json.dumps(value, ensure_ascii=False)
        else:
            self.choices = '[]'
    
    @property
    def sprites_list(self):
        """Возвращает sprites как список Python"""
        if self.sprites and self.sprites != '[]':
            try:
                sprites = json.loads(self.sprites)
                # Гарантируем наличие isOnCanvas
                if isinstance(sprites, list):
                    for sprite in sprites:
                        if isinstance(sprite, dict):
                            sprite['isOnCanvas'] = sprite.get('isOnCanvas', True)
                return sprites
            except:
                return []
        return []
    
    @sprites_list.setter
    def sprites_list(self, value):
        """Устанавливает sprites из списка Python"""
        if isinstance(value, list):
            # Фильтруем только спрайты на холсте
            canvas_sprites = [s for s in value if s.get('isOnCanvas', True)]
            self.sprites = json.dumps(canvas_sprites, ensure_ascii=False)
        else:
            self.sprites = '[]'

# Добавляем обработчик событий для автоматического преобразования
@event.listens_for(Scene, 'before_insert')
@event.listens_for(Scene, 'before_update')
def before_scene_save(mapper, connection, target):
    """Автоматически преобразуем choices в JSON при сохранении"""
    if hasattr(target, '_choices'):
        if isinstance(target._choices, list):
            target._choices = json.dumps(target._choices, ensure_ascii=False)
        elif target._choices is None:
            target._choices = '[]'
    
    if hasattr(target, '_sprites'):
        if isinstance(target._sprites, list):
            target._sprites = json.dumps(target._sprites, ensure_ascii=False)
        elif target._sprites is None:
            target._sprites = '[]'

