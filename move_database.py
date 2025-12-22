import os
import shutil
import sqlite3

print("📦 Перенос базы данных...")

# Проверяем существующие файлы
source_db = 'instance/visual_novel.db'
target_db = 'visual_novel.db'

print(f"🔍 Исходный файл: {source_db}")
print(f"🎯 Целевой файл: {target_db}")

if os.path.exists(source_db):
    try:
        # Копируем файл
        if os.path.exists(target_db):
            print(f"⚠️ Целевой файл уже существует, создаю резервную копию...")
            backup_name = f"{target_db}.backup"
            if os.path.exists(backup_name):
                os.remove(backup_name)
            os.rename(target_db, backup_name)
            print(f"✅ Резервная копия создана: {backup_name}")
        
        shutil.copy2(source_db, target_db)
        print(f"✅ Файл скопирован из {source_db} в {target_db}")
        
        # Проверяем структуру
        print(f"\n🔍 Проверяем структуру новой БД...")
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        # Проверяем таблицу scene
        cursor.execute("PRAGMA table_info(scene)")
        columns = cursor.fetchall()
        
        print("Таблица 'scene':")
        column_names = [col[1] for col in columns]
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Добавляем недостающие колонки
        if 'name' not in column_names:
            print("🔄 Добавляем колонку 'name'...")
            cursor.execute("ALTER TABLE scene ADD COLUMN name VARCHAR(100) DEFAULT ''")
        
        if 'sprites' not in column_names:
            print("🔄 Добавляем колонку 'sprites'...")
            cursor.execute("ALTER TABLE scene ADD COLUMN sprites TEXT DEFAULT '[]'")
        
        if 'choices' not in column_names:
            print("🔄 Добавляем колонку 'choices'...")
            cursor.execute("ALTER TABLE scene ADD COLUMN choices TEXT DEFAULT '[]'")
        
        conn.commit()
        
        # Проверяем данные
        cursor.execute("SELECT COUNT(*) FROM scene")
        scene_count = cursor.fetchone()[0]
        print(f"\n📊 Сцен в БД: {scene_count}")
        
        conn.close()
        print(f"\n✅ База данных успешно перенесена и обновлена!")
        
    except Exception as e:
        print(f"❌ Ошибка при переносе: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"⚠️ Исходный файл не найден, создаем новую БД...")
    
    # Создаем новую БД с правильной структурой
    from create_db_direct import create_database
    create_database()