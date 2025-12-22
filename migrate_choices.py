# migrate_choices.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.db import Scene
import json

print("🔄 Миграция данных базы...")

with app.app_context():
    try:
        scenes = Scene.query.all()
        fixed_count = 0
        error_count = 0
        
        for scene in scenes:
            try:
                # Получаем текущее значение choices
                current_choices = scene._choices
                
                # Проверяем и исправляем если нужно
                if current_choices is None:
                    scene._choices = '[]'
                    fixed_count += 1
                    print(f"✅ Scene {scene.id}: None -> []")
                
                elif isinstance(current_choices, list):
                    # Преобразуем список в JSON
                    scene._choices = json.dumps(current_choices, ensure_ascii=False)
                    fixed_count += 1
                    print(f"✅ Scene {scene.id}: list -> JSON")
                
                elif isinstance(current_choices, str):
                    # Проверяем, является ли строка валидным JSON
                    try:
                        if current_choices.strip():
                            json.loads(current_choices)
                        # Если это валидный JSON, оставляем как есть
                        print(f"✓ Scene {scene.id}: уже валидный JSON")
                    except json.JSONDecodeError:
                        # Если невалидный JSON, заменяем на пустой массив
                        scene._choices = '[]'
                        fixed_count += 1
                        print(f"✅ Scene {scene.id}: невалидный JSON -> []")
                
                else:
                    # Неизвестный тип, заменяем на пустой массив
                    scene._choices = '[]'
                    fixed_count += 1
                    print(f"✅ Scene {scene.id}: тип {type(current_choices)} -> []")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Scene {scene.id}: ошибка миграции - {e}")
        
        if fixed_count > 0 or error_count > 0:
            db.session.commit()
            print(f"\n📊 Результаты миграции:")
            print(f"   Исправлено сцен: {fixed_count}")
            print(f"   Ошибок: {error_count}")
            print(f"   Всего сцен: {len(scenes)}")
        else:
            print("\n✅ Все данные уже в правильном формате")
        
        # Проверяем несколько сцен после миграции
        print(f"\n🔍 Проверка данных после миграции:")
        test_scenes = Scene.query.limit(3).all()
        for scene in test_scenes:
            print(f"   Scene {scene.id}: choices = {scene._choices[:80]}...")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

print("\n🎯 Миграция завершена!")