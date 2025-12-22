# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.db import db, User, Novel, Scene
from config import Config
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница - показываем опубликованные новеллы
@app.route('/')
def index():
    try:
        novels = Novel.query.filter_by(is_published=True).order_by(Novel.created_at.desc()).all()
    except Exception as e:
        print(f"Ошибка загрузки новелл: {e}")
        novels = []
        flash('Ошибка загрузки новелл', 'error')
    
    return render_template('index.html', novels=novels)

# Мои новеллы
@app.route('/my_novels')
@login_required
def my_novels():
    novels = Novel.query.filter_by(author_id=current_user.id).order_by(Novel.created_at.desc()).all()
    return render_template('my_novels.html', novels=novels)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            nickname = request.form['nickname']
            
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Пользователь с таким email уже существует', 'error')
                return render_template('register.html')
            
            user = User(email=email, password=password, nickname=nickname)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Регистрация успешна!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ошибка регистрации: {str(e)}', 'error')
    
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user and user.password == request.form['password']:
                login_user(user)
                flash('Вход выполнен!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный email или пароль', 'error')
        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'error')
    
    return render_template('login.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

# Профиль
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.nickname = request.form['nickname']
            current_user.phone = request.form['phone']
            current_user.language = request.form['language']
            db.session.commit()
            flash('Данные профиля обновлены', 'success')
        except Exception as e:
            flash(f'Ошибка обновления профиля: {str(e)}', 'error')
    
    return render_template('profile.html', user=current_user)

# Конструктор
@app.route('/builder')
@app.route('/builder/<int:novel_id>')
@login_required
def builder(novel_id=None):
    novel = None
    if novel_id:
        novel = Novel.query.get(novel_id)
        if novel and novel.author_id != current_user.id:
            flash('У вас нет доступа к этой новелле', 'error')
            return redirect(url_for('my_novels'))
    
    return render_template('builder.html', novel=novel)

# Создание новой новеллы
@app.route('/create_novel', methods=['POST'])
@login_required
def create_novel():
    try:
        title = request.form.get('title', 'Без названия')
        description = request.form.get('description', '')
        
        novel = Novel(
            title=title,
            description=description,
            author_id=current_user.id,
            is_published=False
        )
        db.session.add(novel)
        db.session.commit()
        
        flash('Новелла создана! Теперь добавьте сцены.', 'success')
        return redirect(url_for('builder', novel_id=novel.id))
    except Exception as e:
        flash(f'Ошибка создания новеллы: {str(e)}', 'error')
        return redirect(url_for('builder'))

# Сохранение новеллы (API)
@app.route('/api/save_novel/<int:novel_id>', methods=['POST'])
@login_required
def save_novel(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        if novel.author_id != current_user.id:
            return jsonify({'success': False, 'error': 'Нет доступа к этой новелле'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных для сохранения'})
        
        # Обновляем данные новеллы
        novel.title = data.get('title', novel.title)
        novel.description = data.get('description', novel.description)
        novel.is_published = bool(data.get('is_published', novel.is_published))
        novel.updated_at = datetime.utcnow()
        
        # Получаем сцены
        scenes_data = data.get('scenes', [])
        
        # Удаляем старые сцены
        Scene.query.filter_by(novel_id=novel.id).delete()
        
        # Добавляем новые сцены
        for i, scene_data in enumerate(scenes_data):
            scene = Scene(
                novel_id=novel.id,
                background=scene_data.get('background', ''),
                text=scene_data.get('text', ''),
                order=scene_data.get('order', i)
            )
            
            # Устанавливаем choices через сеттер (автоматическое преобразование)
            scene.choices = scene_data.get('choices', [])
            
            db.session.add(scene)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Новелла сохранена успешно',
            'novel_id': novel.id,
            'is_published': novel.is_published
        })
        
    except Exception as e:
        print(f"❌ Ошибка сохранения новеллы: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Получение данных новеллы (API)
@app.route('/api/novel/<int:novel_id>')
@login_required
def get_novel_data(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        if not novel or novel.author_id != current_user.id:
            return jsonify({'error': 'Нет доступа'})
        
        scenes = Scene.query.filter_by(novel_id=novel_id).order_by(Scene.order).all()
        
        scenes_data = []
        for scene in scenes:
            # Используем геттер choices (автоматическое преобразование из JSON)
            scenes_data.append({
                'id': scene.id,
                'background': scene.background or '',
                'text': scene.text or '',
                'order': scene.order or 0,
                'choices': scene.choices  # Автоматически преобразуется из JSON
            })
        
        return jsonify({
            'id': novel.id,
            'title': novel.title or '',
            'description': novel.description or '',
            'cover_image': novel.cover_image or '',
            'is_published': novel.is_published or False,
            'scenes': scenes_data
        })
    except Exception as e:
        return jsonify({'error': str(e)})
# Чтение новеллы
@app.route('/view/<int:novel_id>')
def view_novel(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        
        # Проверяем доступ
        if not novel.is_published and (not current_user.is_authenticated or novel.author_id != current_user.id):
            flash('Эта новелла не опубликована', 'error')
            return redirect(url_for('index'))
        
        scenes = Scene.query.filter_by(novel_id=novel_id).order_by(Scene.order).all()
        
        # Подготавливаем сцены для шаблона
        scenes_for_template = []
        for scene in scenes:
            scene_data = {
                'id': scene.id,
                'text': scene.text or '',
                'background': scene.background or '',
                'order': scene.order,
                'choices': []
            }
            
            # Преобразуем choices из JSON
            if scene._choices and scene._choices != '[]':
                try:
                    choices = json.loads(scene._choices)
                    # Гарантируем правильную структуру
                    if isinstance(choices, list):
                        for choice in choices:
                            if isinstance(choice, dict):
                                # Обрабатываем разные варианты ключей
                                text = choice.get('text', '')
                                next_scene = choice.get('nextScene') or choice.get('next_scene') or 0
                                scene_data['choices'].append({
                                    'text': text,
                                    'nextScene': int(next_scene) if next_scene else 0
                                })
                except Exception as e:
                    print(f"Ошибка парсинга choices для сцены {scene.id}: {e}")
            
            scenes_for_template.append(scene_data)
        
        return render_template('viewer.html', 
                             novel=novel, 
                             scenes=scenes_for_template)
        
    except Exception as e:
        print(f"Ошибка загрузки новеллы: {e}")
        flash('Ошибка загрузки новеллы', 'error')
        return redirect(url_for('index'))

# Удаление новеллы
@app.route('/delete_novel/<int:novel_id>', methods=['POST'])
@login_required
def delete_novel(novel_id):
    try:
        novel = Novel.query.get(novel_id)
        if novel and novel.author_id == current_user.id:
            # Удаляем все сцены новеллы
            Scene.query.filter_by(novel_id=novel.id).delete()
            # Удаляем саму новеллу
            db.session.delete(novel)
            db.session.commit()
            flash('Новелла удалена', 'success')
        else:
            flash('Нет доступа к этой новелле', 'error')
    except Exception as e:
        flash(f'Ошибка удаления: {str(e)}', 'error')
    
    return redirect(url_for('my_novels'))

if __name__ == '__main__':
    with app.app_context():
        # Создаем таблицы если их нет
        db.create_all()
        print("✅ База данных готова")
        
        # Создаем тестового пользователя если нет пользователей
        if User.query.count() == 0:
            user = User(
                email='test@example.com',
                password='test123',
                nickname='TestUser'
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Создан тестовый пользователь")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


# Новый маршрут для быстрой публикации
@app.route('/api/publish_novel/<int:novel_id>', methods=['POST'])
@login_required
def publish_novel(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        if novel.author_id != current_user.id:
            return jsonify({'success': False, 'error': 'Нет доступа'})
        
        novel.is_published = True
        novel.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Новелла опубликована!',
            'novel_id': novel.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/api/publish_novel/<int:novel_id>', methods=['POST'])
@login_required
def publish_novel(novel_id):
    """Быстрая публикация новеллы"""
    try:
        novel = Novel.query.get_or_404(novel_id)
        
        # Проверяем права
        if novel.author_id != current_user.id:
            return jsonify({'success': False, 'error': 'Нет доступа'})
        
        # Проверяем, что есть хотя бы одна сцена
        if not novel.scenes:
            return jsonify({'success': False, 'error': 'Добавьте хотя бы одну сцену перед публикацией'})
        
        # Публикуем
        novel.is_published = True
        novel.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Новелла опубликована!',
            'novel_id': novel.id,
            'title': novel.title
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Функция проверки расширений файлов
def allowed_file(filename, file_type='image'):
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'audio':
        return ext in Config.ALLOWED_AUDIO_EXTENSIONS
    
    return False
