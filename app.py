from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.db import db, User, Novel, Scene
from config import Config
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import traceback

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

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def index():
    try:
        novels = Novel.query.filter_by(is_published=True).order_by(Novel.created_at.desc()).all()
    except:
        novels = []
    
    return render_template('index.html', novels=novels)

# ========== РЕГИСТРАЦИЯ ==========
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

# ========== ВХОД ==========
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

# ========== ВЫХОД ==========
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

# ========== ПРОФИЛЬ ==========
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

# ========== СМЕНА ПАРОЛЯ ==========
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('Новые пароли не совпадают', 'error')
            return redirect(url_for('profile'))
        
        if len(new_password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
            return redirect(url_for('profile'))
        
        if current_user.password != old_password:
            flash('Неверный текущий пароль', 'error')
            return redirect(url_for('profile'))
        
        current_user.password = new_password
        db.session.commit()
        flash('Пароль успешно изменен', 'success')
        return redirect(url_for('profile'))
        
    except Exception as e:
        flash(f'Ошибка при смене пароля: {str(e)}', 'error')
        return redirect(url_for('profile'))

# ========== СМЕНА EMAIL ==========
@app.route('/change_email', methods=['POST'])
@login_required
def change_email():
    """Смена email"""
    try:
        new_email = request.form.get('new_email')
        password = request.form.get('password')
        
        if not new_email or not password:
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('profile'))
        
        # Проверяем пароль
        if current_user.password != password:
            flash('Неверный пароль', 'error')
            return redirect(url_for('profile'))
        
        # Проверяем, что email не занят
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Этот email уже используется', 'error')
            return redirect(url_for('profile'))
        
        # Меняем email
        current_user.email = new_email
        db.session.commit()
        
        flash('Email успешно изменен', 'success')
        return redirect(url_for('profile'))
        
    except Exception as e:
        flash(f'Ошибка при смене email: {str(e)}', 'error')
        return redirect(url_for('profile'))

# ========== СМЕНА ТЕЛЕФОНА ==========
@app.route('/change_phone', methods=['POST'])
@login_required
def change_phone():
    """Смена телефона"""
    try:
        new_phone = request.form.get('new_phone')
        
        if not new_phone:
            flash('Поле телефона обязательно', 'error')
            return redirect(url_for('profile'))
        
        # Меняем телефон
        current_user.phone = new_phone
        db.session.commit()
        
        flash('Телефон успешно изменен', 'success')
        return redirect(url_for('profile'))
        
    except Exception as e:
        flash(f'Ошибка при смене телефона: {str(e)}', 'error')
        return redirect(url_for('profile'))
    
# ========== МОИ НОВЕЛЛЫ ==========
@app.route('/my_novels')
@login_required
def my_novels():
    try:
        novels = Novel.query.filter_by(author_id=current_user.id).order_by(Novel.created_at.desc()).all()
        novels_with_counts = []
        for novel in novels:
            scene_count = Scene.query.filter_by(novel_id=novel.id).count()
            novels_with_counts.append({
                'novel': novel,
                'scene_count': scene_count
            })
        return render_template('my_novels.html', novels_with_counts=novels_with_counts)
    except Exception as e:
        print(f"Ошибка в my_novels: {e}")
        flash('Ошибка загрузки новелл', 'error')
        return render_template('my_novels.html', novels_with_counts=[])

# ========== КОНСТРУКТОР ==========
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

# ========== СОЗДАНИЕ НОВЕЛЛЫ ==========
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

# ========== API: ЗАГРУЗКА ДАННЫХ НОВЕЛЛЫ ==========
@app.route('/api/novel/<int:novel_id>')
@login_required
def get_novel_data(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        if not novel or novel.author_id != current_user.id:
            return jsonify({'error': 'Нет доступа'}), 403
        
        scenes_data = []
        for i, scene in enumerate(novel.scenes):
            scenes_data.append({
                'id': scene.id,
                'name': scene.name or f'Сцена {i + 1}',
                'background': scene.background or '',
                'text': scene.text or '',
                'order': scene.order or i,
                'choices': scene.choices_list,
                'sprites': scene.sprites_list
            })
        
        response_data = {
            'id': novel.id,
            'title': novel.title or '',
            'description': novel.description or '',
            'cover_image': novel.cover_image or '',
            'is_published': novel.is_published or False,
            'scenes': scenes_data
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка в get_novel_data: {e}")
        return jsonify({'error': str(e)}), 500

# ========== API: СОХРАНЕНИЕ НОВЕЛЛЫ ==========
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
                name=scene_data.get('name', f'Сцена {i+1}'),
                background=scene_data.get('background', ''),
                text=scene_data.get('text', ''),
                order=scene_data.get('order', i)
            )
            
            # Устанавливаем choices и sprites через свойства
            scene.choices_list = scene_data.get('choices', [])
            scene.sprites_list = scene_data.get('sprites', [])
            
            db.session.add(scene)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Новелла сохранена успешно',
            'novel_id': novel.id,
            'is_published': novel.is_published,
            'scenes_count': len(scenes_data)
        })
        
    except Exception as e:
        print(f"❌ Ошибка сохранения новеллы: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ========== ПРОСМОТР НОВЕЛЛЫ ==========
@app.route('/view/<int:novel_id>')
def view_novel(novel_id):
    try:
        novel = Novel.query.get_or_404(novel_id)
        
        # Проверяем доступ
        if not novel.is_published and (not current_user.is_authenticated or novel.author_id != current_user.id):
            flash('Эта новелла не опубликована', 'error')
            return redirect(url_for('index'))
        
        # Подготавливаем сцены для шаблона
        scenes_for_template = []
        for scene in novel.scenes:
            scene_data = {
                'id': scene.id,
                'name': scene.name or f'Сцена {len(scenes_for_template) + 1}',
                'text': scene.text or '',
                'background': scene.background or '',
                'order': scene.order,
                'choices': scene.choices_list,
                'sprites': scene.sprites_list
            }
            scenes_for_template.append(scene_data)
        
        print(f"📖 Загружена новелла '{novel.title}' с {len(scenes_for_template)} сценами")
        
        return render_template('viewer.html', 
                             novel=novel, 
                             scenes=scenes_for_template)
        
    except Exception as e:
        print(f"Ошибка загрузки новеллы: {e}")
        traceback.print_exc()
        flash('Ошибка загрузки новеллы', 'error')
        return redirect(url_for('index'))

# ========== УДАЛЕНИЕ НОВЕЛЛЫ ==========
@app.route('/delete_novel/<int:novel_id>', methods=['POST'])
@login_required
def delete_novel(novel_id):
    try:
        novel = Novel.query.get(novel_id)
        if novel and novel.author_id == current_user.id:
            Scene.query.filter_by(novel_id=novel.id).delete()
            db.session.delete(novel)
            db.session.commit()
            flash('Новелла удалена', 'success')
        else:
            flash('Нет доступа к этой новелле', 'error')
    except Exception as e:
        flash(f'Ошибка удаления: {str(e)}', 'error')
    
    return redirect(url_for('my_novels'))

# ========== ПУБЛИКАЦИЯ НОВЕЛЛЫ ==========
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
            'novel_id': novel.id,
            'title': novel.title
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== СОЗДАНИЕ ДЕМО НОВЕЛЛЫ ==========
def create_demo_novel():
    """Создание демо новеллы если её нет"""
    try:
        demo_novel = Novel.query.filter_by(title='Демо: Приключение в лесу').first()
        if not demo_novel:
            print("Создаю демо новеллу...")
            
            # Находим или создаем тестового пользователя
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                user = User(
                    email='test@example.com',
                    password='test123',
                    nickname='TestUser'
                )
                db.session.add(user)
                db.session.commit()
            
            # Создаем демо новеллу
            demo_novel = Novel(
                title='Демо: Приключение в лесу',
                description='Интерактивная история с выбором пути',
                cover_image='https://picsum.photos/400/300?random=1',
                is_published=True,
                author_id=user.id
            )
            db.session.add(demo_novel)
            db.session.commit()
            
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
                    'text': 'Вы пошли направо и встретили дружелюбного дракона.',
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
            
            for scene_data in demo_scenes:
                scene = Scene(
                    novel_id=demo_novel.id,
                    name=scene_data['name'],
                    background=scene_data['background'],
                    text=scene_data['text'],
                    order=scene_data['order']
                )
                scene.choices_list = scene_data['choices']
                scene.sprites_list = scene_data['sprites']
                db.session.add(scene)
            
            db.session.commit()
            print("✅ Демо новелла создана!")
            
    except Exception as e:
        print(f"❌ Ошибка создания демо новеллы: {e}")

# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_demo_novel()
    
    print("=" * 50)
    print("🚀 Сервер визуальных новелл запускается...")
    print("=" * 50)
    print("🌐 Откройте в браузере:")
    print("   1. http://localhost:5000 - Главная страница")
    print("   2. http://localhost:5000/login - Вход")
    print("   3. http://localhost:5000/register - Регистрация")
    print("=" * 50)
    print("🔑 Тестовый пользователь:")
    print("   Email: test@example.com")
    print("   Пароль: test123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)