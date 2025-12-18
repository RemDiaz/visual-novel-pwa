from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.db import db, User, Novel, Scene
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница
@app.route('/')
def index():
    novels = Novel.query.all()
    return render_template('index.html', novels=novels)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nickname = request.form['nickname']
        user = User(email=email, password=password, nickname=nickname)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Профиль
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.nickname = request.form['nickname']
        current_user.phone = request.form['phone']
        current_user.language = request.form['language']
        db.session.commit()
    return render_template('profile.html', user=current_user)

# Конструктор
@app.route('/builder')
@login_required
def builder():
    return render_template('builder.html')

# Чтение новеллы
@app.route('/view/<int:novel_id>')
def view_novel(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    scenes = Scene.query.filter_by(novel_id=novel_id).order_by(Scene.order).all()
    return render_template('viewer.html', novel=novel, scenes=scenes)

# API для сохранения сцены
@app.route('/api/save_scene', methods=['POST'])
@login_required
def save_scene():
    data = request.json
    scene = Scene(
        novel_id=data['novel_id'],
        background=data['background'],
        text=data['text'],
        order=data['order']
    )
    db.session.add(scene)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            nickname = request.form['nickname']
            
            # Проверка, существует ли пользователь
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('register.html', error='Пользователь с таким email уже существует')
            
            user = User(email=email, password=password, nickname=nickname)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        except Exception as e:
            return render_template('register.html', error='Ошибка при регистрации')
    
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user and user.password == request.form['password']:
                login_user(user)
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Неверный email или пароль')
        except Exception as e:
            return render_template('login.html', error='Ошибка при входе')
    
    return render_template('login.html')
