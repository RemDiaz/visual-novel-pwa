# update_db.py
import os
import sys
from app import app, db
from sqlalchemy import text

print("🔄 Обновление структуры базы данных...")

with app.app_context():
    # Проверяем существующие колонки в таблице novel
    try:
        result = db.session.execute(text("PRAGMA table_info(novel)"))
        columns = {row[1] for row in result}
        print(f"Существующие колонки в novel: {columns}")
        
        # Добавляем недостающие колонки
        if 'description' not in columns:
            db.session.execute(text("ALTER TABLE novel ADD COLUMN description TEXT DEFAULT ''"))
            print("✅ Добавлена колонка 'description'")
        
        if 'cover_image' not in columns:
            db.session.execute(text("ALTER TABLE novel ADD COLUMN cover_image TEXT DEFAULT ''"))
            print("✅ Добавлена колонка 'cover_image'")
        
        if 'is_published' not in columns:
            db.session.execute(text("ALTER TABLE novel ADD COLUMN is_published BOOLEAN DEFAULT 0"))
            print("✅ Добавлена колонка 'is_published'")
        
        if 'updated_at' not in columns:
            db.session.execute(text("ALTER TABLE novel ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            print("✅ Добавлена колонка 'updated_at'")
        
        # Проверяем таблицу user
        result = db.session.execute(text("PRAGMA table_info(user)"))
        user_columns = {row[1] for row in result}
        print(f"Существующие колонки в user: {user_columns}")
        
        if 'created_at' not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            print("✅ Добавлена колонка 'created_at' в user")
        
        if 'phone' not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN phone TEXT DEFAULT ''"))
            print("✅ Добавлена колонка 'phone' в user")
        
        if 'language' not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN language TEXT DEFAULT 'RU'"))
            print("✅ Добавлена колонка 'language' в user")
        
        # Проверяем таблицу scene
        result = db.session.execute(text("PRAGMA table_info(scene)"))
        scene_columns = {row[1] for row in result}
        print(f"Существующие колонки в scene: {scene_columns}")
        
        if 'choices' not in scene_columns:
            db.session.execute(text("ALTER TABLE scene ADD COLUMN choices TEXT DEFAULT '[]'"))
            print("✅ Добавлена колонка 'choices' в scene")
        
        if 'order' not in scene_columns:
            db.session.execute(text("ALTER TABLE scene ADD COLUMN order INTEGER DEFAULT 0"))
            print("✅ Добавлена колонка 'order' в scene")
        
        db.session.commit()
        print("\n✅ Структура базы данных успешно обновлена!")
        
        # Создаем тестовые данные если их нет
        from database.db import User, Novel, Scene
        import json
        
        if User.query.count() == 0:
            user = User(
                email='test@example.com',
                password='test123',
                nickname='TestUser',
                phone='+79991234567',
                language='RU'
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Создан тестовый пользователь")
        
        if Novel.query.count() == 0:
            novel = Novel(
                title='Демо: Приключение в лесу',
                description='Интерактивная история с выбором пути',
                cover_image='https://picsum.photos/400/300?random=1',
                is_published=True,
                author_id=User.query.first().id
            )
            db.session.add(novel)
            db.session.commit()
            
            # Добавляем сцены
            scenes_data = [
                {
                    'background': 'https://picsum.photos/800/400?random=2',
                    'text': 'Вы стоите на опушке леса. Перед вами две тропинки.',
                    'order': 1,
                    'choices': json.dumps([
                        {'text': 'Пойти налево', 'nextScene': 2},
                        {'text': 'Пойти направо', 'nextScene': 3}
                    ])
                },
                {
                    'background': 'https://picsum.photos/800/400?random=3',
                    'text': 'Вы пошли налево и нашли сундук с сокровищами! Конец.',
                    'order': 2,
                    'choices': json.dumps([])
                },
                {
                    'background': 'https://picsum.photos/800/400?random=4',
                    'text': 'Вы пошли направо и встретили дружелюбного дракона. Конец.',
                    'order': 3,
                    'choices': json.dumps([])
                }
            ]
            
            for scene_data in scenes_data:
                scene = Scene(
                    novel_id=novel.id,
                    background=scene_data['background'],
                    text=scene_data['text'],
                    order=scene_data['order'],
                    choices=scene_data['choices']
                )
                db.session.add(scene)
            
            db.session.commit()
            print("✅ Создана демонстрационная новелла с 3 сценами")
        
        print(f"\n📊 Статистика:")
        print(f"   Пользователей: {User.query.count()}")
        print(f"   Новелл: {Novel.query.count()}")
        print(f"   Сцен: {Scene.query.count()}")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении БД: {e}")
        db.session.rollback()