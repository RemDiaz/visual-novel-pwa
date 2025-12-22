# rebuild_db.py
import os
import sys
from pathlib import Path

# Удаляем старые файлы БД
db_files = [
    'visual_novel.db',
    'test.db',
    'instance/visual_novel.db',
    'instance/test.db'
]

for db_file in db_files:
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✓ Удален: {db_file}")
        except Exception as e:
            print(f"✗ Не удалось удалить {db_file}: {e}")

# Создаем абсолютно чистую БД
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Создаем временное приложение для построения БД
temp_app = Flask(__name__)
temp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visual_novel.db'
temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(temp_app)

# Определяем модели
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), default='')
    language = db.Column(db.String(2), default='RU')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

class Scene(db.Model):
    __tablename__ = 'scene'
    
    id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    background = db.Column(db.String(200), default='')
    text = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    choices = db.Column(db.Text, default='[]')

# Создаем БД
with temp_app.app_context():
    # Создаем все таблицы
    db.create_all()
    print("\n✓ Созданы таблицы:")
    print("  - user")
    print("  - novel")
    print("  - scene")
    
    # Проверяем структуру
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    print("\n✓ Структура таблиц:")
    for table_name in inspector.get_table_names():
        print(f"\n{table_name}:")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']} ({column['type']})")
    
    # Добавляем тестовые данные
    user = User(
        email='test@example.com',
        password='test123',
        nickname='TestUser'
    )
    db.session.add(user)
    db.session.commit()
    print(f"\n✓ Создан пользователь: {user.email}")
    
    novel = Novel(
        title='Пример визуальной новеллы',
        description='Это демонстрационная новелла',
        is_published=True,
        author_id=user.id
    )
    db.session.add(novel)
    db.session.commit()
    print(f"✓ Создана новелла: {novel.title}")
    
    print("\n✓ Тестовые данные:")
    print(f"  Пользователей: {User.query.count()}")
    print(f"  Новелл: {Novel.query.count()}")

print("\n✅ База данных успешно пересоздана!")
print("Теперь запустите: python app.py")