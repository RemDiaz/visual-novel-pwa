import os
import time

print("🔄 Полный сброс и пересоздание базы данных...")

# 1. Останавливаем Flask приложение если запущено
print("🛑 Убедитесь что Flask приложение остановлено (Ctrl+C)")

# 2. Удаляем старые файлы
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

# 3. Создаем папку instance если нужно
os.makedirs('instance', exist_ok=True)

# 4. Запускаем создание новой БД
print("\n🔄 Запускаем create_db_direct.py...")
os.system('python create_db_direct.py')

# 5. Копируем в instance для совместимости
print("\n📦 Копируем БД в папку instance для совместимости...")
if os.path.exists('visual_novel.db'):
    import shutil
    try:
        shutil.copy2('visual_novel.db', 'instance/visual_novel.db')
        print("✅ БД скопирована в instance/visual_novel.db")
    except Exception as e:
        print(f"⚠️ Не удалось скопировать: {e}")

print("\n🎉 База данных полностью пересоздана!")
print("\n🔑 Данные для входа:")
print("   Email: test@example.com")
print("   Пароль: test123")
print("\n🚀 Запустите приложение: python app.py")
print("🌐 Откройте: http://localhost:5000")