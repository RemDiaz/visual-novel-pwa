import sqlite3
import json
import os

def verify_database():
    print("🔍 Проверка базы данных...")
    
    db_path = 'visual_novel.db'
    
    if not os.path.exists(db_path):
        print("❌ Файл базы данных не найден!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📋 Проверяем структуру таблиц...")
        
        # Проверяем таблицу scene
        cursor.execute("PRAGMA table_info(scene)")
        scene_columns = cursor.fetchall()
        
        print("Таблица 'scene':")
        column_names = []
        for col in scene_columns:
            column_names.append(col[1])
            print(f"  - {col[1]} ({col[2]})")
        
        # Проверяем наличие критических колонок
        required_columns = ['name', 'sprites', 'choices']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"\n❌ Отсутствуют колонки: {missing_columns}")
            print("🔄 Добавляем недостающие колонки...")
            
            for col in missing_columns:
                if col == 'name':
                    cursor.execute("ALTER TABLE scene ADD COLUMN name VARCHAR(100) DEFAULT ''")
                elif col == 'sprites':
                    cursor.execute("ALTER TABLE scene ADD COLUMN sprites TEXT DEFAULT '[]'")
                elif col == 'choices':
                    cursor.execute("ALTER TABLE scene ADD COLUMN choices TEXT DEFAULT '[]'")
                print(f"✅ Добавлена колонка: {col}")
            
            conn.commit()
        
        print("\n📊 Проверяем данные...")
        
        # Проверяем данные пользователя
        cursor.execute("SELECT id, email, nickname FROM user")
        users = cursor.fetchall()
        print(f"👤 Пользователей: {len(users)}")
        for user_id, email, nickname in users:
            print(f"  - ID {user_id}: {email} ({nickname})")
        
        # Проверяем новеллы
        cursor.execute("SELECT id, title, is_published FROM novel")
        novels = cursor.fetchall()
        print(f"\n📚 Новелл: {len(novels)}")
        
        for novel_id, title, is_published in novels:
            status = "Опубликовано" if is_published else "Черновик"
            print(f"  - ID {novel_id}: '{title}' ({status})")
            
            # Сцены этой новеллы
            cursor.execute("SELECT id, name, sprites FROM scene WHERE novel_id = ?", (novel_id,))
            scenes = cursor.fetchall()
            print(f"    Сцен: {len(scenes)}")
            
            for scene_id, name, sprites_json in scenes[:2]:  # Первые 2 сцены
                sprite_count = 0
                if sprites_json and sprites_json != '[]':
                    try:
                        sprites = json.loads(sprites_json)
                        if isinstance(sprites, list):
                            sprite_count = len(sprites)
                    except:
                        pass
                
                sprites_info = f" (спрайтов: {sprite_count})" if sprite_count > 0 else ""
                print(f"    - Сцена {scene_id}: '{name or 'Без названия'}'{sprites_info}")
        
        # Тест на наличие колонки sprites
        cursor.execute("SELECT sprites FROM scene WHERE sprites IS NOT NULL AND sprites != '' LIMIT 1")
        test_result = cursor.fetchone()
        
        if test_result and test_result[0]:
            try:
                sprites = json.loads(test_result[0])
                if isinstance(sprites, list):
                    print(f"\n✅ Колонка 'sprites' работает корректно")
                    if sprites:
                        print(f"   Пример спрайта: {sprites[0].get('name', 'Без имени')}")
            except:
                print(f"\n⚠️ Колонка 'sprites' содержит невалидный JSON")
        
        conn.close()
        
        if len(novels) > 0 and len(users) > 0:
            print("\n✅ База данных в порядке!")
            return True
        else:
            print("\n⚠️ База данных пуста или содержит мало данных")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_database()