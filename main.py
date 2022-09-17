from flask import render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user
from admin.admin import admin, login_admin
from config import app, db, generate_password_hash, check_password_hash
from delivery.delivery import delivery
from delivery.delivery import login_delivery
from models import Profiles, Users
from users.users import users

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(delivery, url_prefix='/delivery')

login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = "Авторизируйтесь для доступа к сайту"
login_manager.login_message_category = "success"


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        return redirect('/login')
    return render_template('index.html', title="Главная")


@login_manager.user_loader
def load_user(id):
    return Profiles.query.get(id)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        number = request.form['number']
        psw = request.form['psw']
        psw2 = request.form['psw2']

        if Users.query.filter_by(username=username).all():
            flash('Логин занят. Введите другой логин', 'info')
            return redirect(url_for("register"))
        if Users.query.filter_by(email=email).all():
            flash('Почта занята. Введите другую почту', 'info')
            return redirect(url_for("register"))
        if Users.query.filter_by(number=number).all():
            flash('Номер занят. Введите другой номер', 'info')
            return redirect(url_for("register"))
        if username == 'admin' or username == 'delivery':
            flash('Недопустимый логин. Введите другой логин', 'info')
            return redirect(url_for("register"))
        else:
            try:
                if psw == psw2:
                    hash = generate_password_hash(psw)
                    p = Profiles(username=username, psw=hash)
                    db.session.add(p)
                    db.session.flush()

                    u = Users(name=name, username=username, email=email, number=number,
                              psw=hash, profile_id=p.id)
                    db.session.add(u)
                    db.session.commit()
                    return redirect(url_for("login"))
                else:
                    db.session.rollback()
                    flash('Ваши пароли не совпадают. Попробуйте заново', 'info')
                    return redirect(url_for("register"))
            except:
                flash('При добавлении сведений произошла ошибка', 'info')
                return render_template("register.html", title="Авторизация")

    return render_template('register.html', title="Авторизация")


@app.route("/login", methods=["POST", "GET"])
def login():
    hash = generate_password_hash('123')
    if request.method == 'POST':
        username = request.form.get('username')
        psw = request.form.get('psw')
        if username == 'admin' and check_password_hash(hash, psw):
            login_admin()
            flash('Вы успешно прошли авторизацию')
            return redirect(url_for('.admin.index'))
        if username == 'delivery' and check_password_hash(hash, psw):
            login_delivery('delivery')
            flash('Вы успешно прошли авторизацию')
            return redirect(url_for('.delivery.orders'))
        user = Profiles.query.filter_by(username=username).first()
        if username and check_password_hash(user.psw, psw):
            login_user(user)
            flash('Вы успешно прошли авторизацию')
            return redirect(url_for('.users.index'))
        else:
            flash('Введен неверный логин или пароль')
            return redirect(url_for('login'))

    return render_template('login.html', title="Авторизация")


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена")


if __name__ == "__main__":
    app.run(debug=True)