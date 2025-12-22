import os
import sqlite3
import json
import time

print("🗑️  Очистка старых файлов...")

# Сначала пробуем удалить/переименовать старые файлы
db_files = [
    'visual_novel.db',
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
                timestamp = int(time.time())
                backup_name = f"{db_file}.backup_{timestamp}"
                os.rename(db_file, backup_name)
                print(f"✓ Переименован в: {backup_name}")
            except:
                print(f"✗ Не удалось переименовать {db_file}")

print("\n🔄 Создание базы данных через прямой SQL...")

# Создаем подключение
conn = sqlite3.connect('visual_novel.db')
cursor = conn.cursor()

print("📊 Создаем таблицы...")

# 1. Таблица user
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    phone VARCHAR(20) DEFAULT '',
    language VARCHAR(2) DEFAULT 'RU',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
print("✅ Таблица 'user' создана")

# 2. Таблица novel
cursor.execute('''
CREATE TABLE IF NOT EXISTS novel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    cover_image VARCHAR(200) DEFAULT '',
    is_published BOOLEAN DEFAULT 0,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user(id)
)
''')
print("✅ Таблица 'novel' создана")

# 3. Таблица scene (С ВСЕМИ НУЖНЫМИ КОЛОНКАМИ!)
cursor.execute('''
CREATE TABLE IF NOT EXISTS scene (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    novel_id INTEGER NOT NULL,
    name VARCHAR(100) DEFAULT '',
    background VARCHAR(200) DEFAULT '',
    text TEXT DEFAULT '',
    "order" INTEGER DEFAULT 0,
    choices TEXT DEFAULT '[]',
    sprites TEXT DEFAULT '[]',
    FOREIGN KEY (novel_id) REFERENCES novel(id)
)
''')
print("✅ Таблица 'scene' создана")

# Проверяем структуру
print("\n📋 Проверяем структуру таблицы 'scene':")
cursor.execute("PRAGMA table_info(scene)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Проверяем наличие всех колонок
column_names = [col[1] for col in columns]
required_columns = ['name', 'sprites']
for col in required_columns:
    if col not in column_names:
        print(f"\n⚠️ Колонка '{col}' отсутствует, добавляем...")
        if col == 'name':
            cursor.execute("ALTER TABLE scene ADD COLUMN name VARCHAR(100) DEFAULT ''")
        elif col == 'sprites':
            cursor.execute("ALTER TABLE scene ADD COLUMN sprites TEXT DEFAULT '[]'")
        print(f"✅ Колонка '{col}' добавлена")

print("\n👤 Добавляем тестового пользователя...")
# Добавляем тестового пользователя
try:
    cursor.execute(
        "INSERT INTO user (email, password, nickname, phone, language) VALUES (?, ?, ?, ?, ?)",
        ('test@example.com', 'test123', 'TestUser', '+79991234567', 'RU')
    )
    user_id = cursor.lastrowid
    print(f"✅ Пользователь добавлен (ID: {user_id})")
except sqlite3.IntegrityError:
    # Пользователь уже существует
    cursor.execute("SELECT id FROM user WHERE email = ?", ('test@example.com',))
    user_id = cursor.fetchone()[0]
    print(f"✅ Пользователь уже существует (ID: {user_id})")

print("\n📚 Добавляем демо-новеллу...")
# Добавляем демо-новеллу
cursor.execute(
    '''INSERT INTO novel (title, description, cover_image, is_published, author_id) 
       VALUES (?, ?, ?, ?, ?)''',
    ('Демо: Приключение в лесу', 
     'Интерактивная история с выбором пути',
     'https://picsum.photos/400/300?random=1',
     1,  # is_published = True
     user_id)
)
novel_id = cursor.lastrowid
print(f"✅ Новелла добавлена (ID: {novel_id})")

print("\n🎭 Добавляем демо-сцены...")
# Демо-сцены
demo_scenes = [
    {
        'name': 'Начало приключения',
        'background': 'https://picsum.photos/800/400?random=2',
        'text': 'Вы стоите на опушке леса. Перед вами две тропинки. Куда пойдете?',
        'order': 1,
        'choices': json.dumps([
            {'text': 'Пойти налево', 'nextScene': 2},
            {'text': 'Пойти направо', 'nextScene': 3}
        ]),
        'sprites': json.dumps([
            {
                'id': 'sprite_1',
                'url': 'https://picsum.photos/150/200?random=10',
                'name': 'Путешественник',
                'x': 300,
                'y': 150,
                'width': 120,
                'height': 180,
                'rotation': 0,
                'zIndex': 1,
                'isOnCanvas': True
            }
        ])
    },
    {
        'name': 'Сокровище',
        'background': 'https://picsum.photos/800/400?random=3',
        'text': 'Вы пошли налево и нашли сундук с сокровищами! Поздравляем!',
        'order': 2,
        'choices': json.dumps([]),
        'sprites': json.dumps([
            {
                'id': 'sprite_2',
                'url': 'https://picsum.photos/150/200?random=11',
                'name': 'Сокровище',
                'x': 400,
                'y': 100,
                'width': 150,
                'height': 150,
                'rotation': 0,
                'zIndex': 1,
                'isOnCanvas': True
            }
        ])
    },
    {
        'name': 'Встреча с драконом',
        'background': 'https://picsum.photos/800/400?random=4',
        'text': 'Вы пошли направо и встретили дружелюбного дракона. Он предлагает вам помощь в обмен на историю.',
        'order': 3,
        'choices': json.dumps([
            {'text': 'Рассказать историю', 'nextScene': 4},
            {'text': 'Поблагодарить и уйти', 'nextScene': 5}
        ]),
        'sprites': json.dumps([
            {
                'id': 'sprite_3',
                'url': 'https://picsum.photos/150/200?random=12',
                'name': 'Дракон',
                'x': 350,
                'y': 120,
                'width': 180,
                'height': 200,
                'rotation': 0,
                'zIndex': 1,
                'isOnCanvas': True
            }
        ])
    }
]

for i, scene_data in enumerate(demo_scenes):
    cursor.execute(
        '''INSERT INTO scene (novel_id, name, background, text, "order", choices, sprites) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (novel_id, 
         scene_data['name'],
         scene_data['background'],
         scene_data['text'],
         scene_data['order'],
         scene_data['choices'],
         scene_data['sprites'])
    )
    print(f"  ✅ Добавлена сцена: {scene_data['name']}")

print("\n📝 Добавляем черновик-новеллу...")
# Добавляем черновик
cursor.execute(
    '''INSERT INTO novel (title, description, is_published, author_id) 
       VALUES (?, ?, ?, ?)''',
    ('Черновик: Городские тайны', 
     'История о загадках старого города',
     0,  # is_published = False
     user_id)
)
draft_novel_id = cursor.lastrowid
print(f"✅ Черновик добавлен (ID: {draft_novel_id})")

# Добавляем пустые сцены для черновика
for i in range(3):
    cursor.execute(
        '''INSERT INTO scene (novel_id, name, text, "order", choices, sprites) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (draft_novel_id,
         f'Сцена {i + 1}',
         f'Текст сцены {i + 1}...',
         i + 1,
         '[]',
         '[]')
    )

print(f"✅ Добавлено 3 пустые сцены для черновика")

# Сохраняем изменения
conn.commit()

print("\n📊 Показываем статистику...")
# Статистика
cursor.execute("SELECT COUNT(*) FROM user")
user_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM novel")
novel_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM scene")
scene_count = cursor.fetchone()[0]

print(f"   👤 Пользователей: {user_count}")
print(f"   📚 Новелл: {novel_count}")
print(f"   🎭 Сцен: {scene_count}")

print("\n🔍 Пример данных из таблицы 'scene':")
cursor.execute("SELECT id, name, sprites FROM scene LIMIT 3")
for row in cursor.fetchall():
    scene_id, name, sprites_json = row
    sprite_count = 0
    if sprites_json and sprites_json != '[]':
        try:
            sprites = json.loads(sprites_json)
            if isinstance(sprites, list):
                sprite_count = len(sprites)
        except:
            pass
    print(f"   Сцена {scene_id}: '{name}' (спрайтов: {sprite_count})")

conn.close()

print("\n🎉 База данных успешно создана!")
print("\n🔑 Данные для входа:")
print(f"   Email: test@example.com")
print(f"   Пароль: test123")
print(f"\n🌐 Запустите приложение: python app.py")
print(f"   Затем откройте: http://localhost:5000")