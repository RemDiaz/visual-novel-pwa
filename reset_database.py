#!/usr/bin/env python3
"""
Скрипт для полного сброса и пересоздания базы данных с демо новеллой
"""
import os
import sys
import shutil
import time
from pathlib import Path

def reset_database():
    print("🔄 Полный сброс и пересоздание базы данных...")
    
    # 1. Останавливаем приложение если запущено
    print("🛑 Убедитесь что Flask приложение остановлено (Ctrl+C)")
    
    # 2. Удаляем старые файлы БД
    print("\n🗑️ Удаляем старые файлы БД...")
    db_files = [
        'visual_novel.db',
        'instance/visual_novel.db',
        'test.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✓ Удален: {db_file}")
            except Exception as e:
                print(f"✗ Не удалось удалить {db_file}: {e}")
                try:
                    backup_name = f"{db_file}.backup_{int(time.time())}"
                    os.rename(db_file, backup_name)
                    print(f"✓ Переименован в: {backup_name}")
                except:
                    print(f"✗ Не удалось переименовать {db_file}")
    
    # 3. Создаем папки
    os.makedirs('instance', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    # 4. Импортируем и создаем базу данных
    print("\n🔄 Создаем новую БД...")
    try:
        # Добавляем путь для импорта
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app import app, db, User, Novel, Scene
        from datetime import datetime
        import json
        
        with app.app_context():
            # Создаем таблицы
            db.create_all()
            print("✅ Таблицы созданы")
            
            # Создаем тестового пользователя
            if User.query.filter_by(email='test@example.com').first() is None:
                user = User(
                    email='test@example.com',
                    password='test123',
                    nickname='TestUser',
                    phone='+79991234567',
                    language='RU'
                )
                db.session.add(user)
                db.session.commit()
                print("✅ Тестовый пользователь создан")
            
            user_id = User.query.filter_by(email='test@example.com').first().id
            
            # Создаем демо новеллу
            if Novel.query.filter_by(title='Демо: Приключение в лесу').first() is None:
                novel = Novel(
                    title='Демо: Приключение в лесу',
                    description='Интерактивная история с выбором пути',
                    cover_image='https://picsum.photos/400/300?random=1',
                    is_published=True,
                    author_id=user_id
                )
                db.session.add(novel)
                db.session.commit()
                print("✅ Демо новелла создана")
            
            novel_id = Novel.query.filter_by(title='Демо: Приключение в лесу').first().id
            
            # Создаем демо сцены
            demo_scenes = [
                {
                    'name': 'Начало приключения',
                    'background': 'https://picsum.photos/800/400?random=2',
                    'text': 'Вы стоите на опушке леса. Перед вами две тропинки. Куда пойдете?',
                    'order': 1,
                    'choices': [
                        {'text': 'Пойти налево', 'nextScene': 2},
                        {'text': 'Пойти направо', 'nextScene': 3}
                    ],
                    'sprites': [
                        {
                            'id': 'sprite_1',
                            'url': 'https://picsum.photos/150/200?random=10',
                            'name': 'Путешественник',
                            'x': 300, 'y': 150,
                            'width': 120, 'height': 180,
                            'rotation': 0, 'zIndex': 1,
                            'isOnCanvas': True
                        }
                    ]
                },
                {
                    'name': 'Сокровище',
                    'background': 'https://picsum.photos/800/400?random=3',
                    'text': 'Вы пошли налево и нашли сундук с сокровищами! Поздравляем!',
                    'order': 2,
                    'choices': [],
                    'sprites': [
                        {
                            'id': 'sprite_2',
                            'url': 'https://picsum.photos/150/200?random=11',
                            'name': 'Сокровище',
                            'x': 400, 'y': 100,
                            'width': 150, 'height': 150,
                            'rotation': 0, 'zIndex': 1,
                            'isOnCanvas': True
                        }
                    ]
                },
                {
                    'name': 'Встреча с драконом',
                    'background': 'https://picsum.photos/800/400?random=4',
                    'text': 'Вы пошли направо и встретили дружелюбного дракона. Он предлагает вам помощь в обмен на историю.',
                    'order': 3,
                    'choices': [
                        {'text': 'Рассказать историю', 'nextScene': 4},
                        {'text': 'Поблагодарить и уйти', 'nextScene': 5}
                    ],
                    'sprites': [
                        {
                            'id': 'sprite_3',
                            'url': 'https://picsum.photos/150/200?random=12',
                            'name': 'Дракон',
                            'x': 350, 'y': 120,
                            'width': 180, 'height': 200,
                            'rotation': 0, 'zIndex': 1,
                            'isOnCanvas': True
                        }
                    ]
                }
            ]
            
            # Удаляем старые сцены если есть
            Scene.query.filter_by(novel_id=novel_id).delete()
            
            # Добавляем новые сцены
            for scene_data in demo_scenes:
                scene = Scene(
                    novel_id=novel_id,
                    name=scene_data['name'],
                    background=scene_data['background'],
                    text=scene_data['text'],
                    order=scene_data['order'],
                    choices_list=scene_data['choices'],
                    sprites_list=scene_data['sprites']
                )
                db.session.add(scene)
                print(f"  ✅ Добавлена сцена: {scene_data['name']}")
            
            db.session.commit()
            print("✅ Демо сцены добавлены")
            
            # Копируем БД в папку instance для совместимости
            if os.path.exists('visual_novel.db'):
                shutil.copy2('visual_novel.db', 'instance/visual_novel.db')
                print("✅ БД скопирована в instance/visual_novel.db")
            
            # Статистика
            user_count = User.query.count()
            novel_count = Novel.query.count()
            scene_count = Scene.query.count()
            
            print(f"\n📊 Статистика новой БД:")
            print(f"   👤 Пользователей: {user_count}")
            print(f"   📚 Новелл: {novel_count}")
            print(f"   🎭 Сцен: {scene_count}")
    
    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 База данных успешно пересоздана!")
    print("\n🔑 Данные для входа:")
    print(f"   Email: test@example.com")
    print(f"   Пароль: test123")
    print(f"\n📖 Демо новелла доступна на главной странице")
    print(f"\n🚀 Запустите приложение:")
    print(f"   python app.py")
    print(f"\n🌐 Откройте: http://localhost:5000")
    return True

if __name__ == '__main__':
    reset_database()