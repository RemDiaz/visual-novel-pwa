from app import app, db
from database.db import Scene
import json

print("🔧 Исправление данных в базе...")

with app.app_context():
    try:
        scenes = Scene.query.all()
        fixed_count = 0
        
        for scene in scenes:
            # Проверяем, что choices - это JSON строка, а не Python список
            if scene._choices and not isinstance(scene._choices, str):
                print(f"⚠️ Scene {scene.id}: choices имеет тип {type(scene._choices)}")
                # Преобразуем в JSON строку
                if isinstance(scene._choices, list):
                    scene._choices = json.dumps(scene._choices, ensure_ascii=False)
                    fixed_count += 1
                elif scene._choices is None:
                    scene._choices = '[]'
                    fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"✅ Исправлено {fixed_count} сцен")
        else:
            print("✅ Все данные в порядке")
        
        # Показываем статистику
        scenes = Scene.query.all()
        print(f"\n📊 Всего сцен: {len(scenes)}")
        
        for scene in scenes[:5]:  # Первые 5 сцен для проверки
            print(f"Scene {scene.id}: choices = {scene._choices[:50]}...")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.session.rollback()