from app import app
from database.db import db, User, Novel, Scene
from datetime import datetime

with app.app_context():
    # Создаем таблицы
    db.create_all()
    
    # Добавляем тестового пользователя
    if not User.query.first():
        user = User(
            email='test@example.com',
            password='password123',
            nickname='TestUser',
            phone='+79991234567',
            language='RU'
        )
        db.session.add(user)
        db.session.commit()
        
        # Добавляем тестовую новеллу
        novel = Novel(
            title='Моя первая новелла',
            author_id=user.id,
            created_at=datetime.now()
        )
        db.session.add(novel)
        db.session.commit()
        
        # Добавляем тестовые сцены
        scenes = [
            Scene(
                novel_id=novel.id,
                background='https://picsum.photos/800/400?random=1',
                text='Это первая сцена моей визуальной новеллы. Добро пожаловать!',
                order=1
            ),
            Scene(
                novel_id=novel.id,
                background='https://picsum.photos/800/400?random=2',
                text='Вы стоите на распутье. Куда пойдёте?',
                order=2
            ),
            Scene(
                novel_id=novel.id,
                background='https://picsum.photos/800/400?random=3',
                text='Вы выбрали путь приключений. Впереди вас ждут испытания!',
                order=3
            )
        ]
        
        for scene in scenes:
            db.session.add(scene)
        
        db.session.commit()
        print('Тестовые данные добавлены!')