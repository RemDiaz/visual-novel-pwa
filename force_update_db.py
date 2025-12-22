import os
import sqlite3
import json

def update_database_structure():
    """Принудительно обновляет структуру БД"""
    print("🔧 Принудительное обновление структуры базы данных...")
    
    db_files = [
        'visual_novel.db',
        'instance/visual_novel.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n🔧 Обрабатываем файл: {db_file}")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Проверяем таблицу scene
                cursor.execute("PRAGMA table_info(scene)")
                columns = [col[1] for col in cursor.fetchall()]
                
                print(f"Существующие колонки: {columns}")
                
                # Добавляем недостающие колонки
                if 'name' not in columns:
                    print("➕ Добавляем колонку 'name'...")
                    try:
                        cursor.execute("ALTER TABLE scene ADD COLUMN name VARCHAR(100) DEFAULT ''")
                        print("✅ Колонка 'name' добавлена")
                    except Exception as e:
                        print(f"⚠️ Не удалось добавить 'name': {e}")
                
                if 'sprites' not in columns:
                    print("➕ Добавляем колонку 'sprites'...")
                    try:
                        cursor.execute("ALTER TABLE scene ADD COLUMN sprites TEXT DEFAULT '[]'")
                        print("✅ Колонка 'sprites' добавлена")
                    except Exception as e:
                        print(f"⚠️ Не удалось добавить 'sprites': {e}")
                
                if 'choices' not in columns:
                    print("➕ Добавляем колонку 'choices'...")
                    try:
                        cursor.execute("ALTER TABLE scene ADD COLUMN choices TEXT DEFAULT '[]'")
                        print("✅ Колонка 'choices' добавлена")
                    except Exception as e:
                        print(f"⚠️ Не удалось добавить 'choices': {e}")
                
                conn.commit()
                
                # Проверяем данные
                cursor.execute("SELECT COUNT(*) FROM scene")
                scene_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM novel")
                novel_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user")
                user_count = cursor.fetchone()[0]
                
                print(f"\n📊 Статистика {db_file}:")
                print(f"   👤 Пользователей: {user_count}")
                print(f"   📚 Новелл: {novel_count}")
                print(f"   🎭 Сцен: {scene_count}")
                
                # Пример данных
                cursor.execute("SELECT id, name FROM scene LIMIT 3")
                scenes = cursor.fetchall()
                if scenes:
                    print(f"\n🔍 Примеры сцен:")
                    for scene_id, name in scenes:
                        print(f"   Сцена {scene_id}: '{name or 'Без названия'}'")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Ошибка обработки {db_file}: {e}")
    
    print("\n🎉 Обновление завершено!")

if __name__ == '__main__':
    update_database_structure()
    