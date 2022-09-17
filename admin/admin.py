from flask import Blueprint, session, render_template, request, url_for, redirect, flash
from config import db
from models import Product, Profiles, Users, ChatMessage, Delivary, Orders


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


def login_admin():
    session['admin_logged'] = 1


def isLogged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)


@admin.route('/')
@admin.route('/index')
def index():
    if not isLogged():
        return redirect(url_for('login'))

    info = []
    user = []
    try:
        info = Orders.query.filter_by(state="На складе").all()
        info += Orders.query.filter_by(state='Заказ в пути').all()
        info += Orders.query.filter_by(state='Заказ прибыл к месту назначения').all()

        for i in info:
            us = Users.query.filter_by(username=i.login).all()
            user += us
    except:
        print("Ошибка")

    return render_template('admin/index.html', list=info, user=user)


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('index'))


@admin.route("/usersList", methods=["POST", "GET"])
def usersList():
    if not isLogged():
        return redirect(url_for('login'))

    us = Users.query.order_by(Users.profile_id).all()
    return render_template('admin/usersList.html', us=us)


@admin.route('/deleteUser/<int:id>')
def deleteUser(id):
    if not isLogged():
        return redirect(url_for('login'))

    user_to_delete = Users.query.get(id)
    profiles_to_deleto = Profiles.query.get(id)
    try:
        db.session.delete(user_to_delete)
        db.session.delete(profiles_to_deleto)
        db.session.commit()
        flash('Пользователь удален', 'info')
        return redirect(url_for('.usersList'))
    except:
        flash('Ошибка удаления', 'info')
        return render_template('/admin/usersList.html')


@admin.route("/delivery", methods=["POST", "GET"])
def delivery():
    if not isLogged():
        return redirect(url_for('login'))

    deliv = Delivary.query.order_by(Delivary.price).all()
    return render_template('/admin/delivery.html', list=deliv)


@admin.route("/msg", methods=["POST", "GET"])
def msg():
    if not isLogged():
        return redirect(url_for('login'))

    if request.method == "POST":

        username = request.form.get("username")
        msg1 = request.form.get('msg')

        message = ChatMessage(
            username=username,
            msg=msg1,
            name='admin'
        )
        try:
            if username and msg1:
                db.session.add(message)
                db.session.commit()
                flash('Сообщение отправлено', 'info')
                return redirect(url_for('.msg'))
        except:
            return "ОШИБКА"
    else:
        mes1 = ChatMessage.query.filter_by(name='admin').all()
        mes = ChatMessage.query.filter_by(username='admin').all()
        return render_template("admin/msg.html", mes=mes, mes1=mes1)


@admin.route('/deleteMsg/<int:id>')
def deleteMsg(id):
    if not isLogged():
        return redirect(url_for('login'))

    msg_to_delete = ChatMessage.query.get(id)
    try:
        db.session.delete(msg_to_delete)
        db.session.commit()
        flash('Сообщение удалено', 'info')
        return redirect(url_for('.msg'))
    except:
        flash('Ошибка удаления', 'info')
        return redirect(url_for('.msg'))


@admin.route("/product", methods=["POST", "GET"])
def product():
    if not isLogged():
        return redirect(url_for('login'))

    if request.method == "POST":
        author = request.form['author']
        name = request.form['name']
        time = request.form['time']
        house = request.form['house']
        price = request.form['price']
        anonce = request.form['anonce']
        count = request.form['count']

        produc = Product(
            author=author,
            name=name,
            time=time,
            house=house,
            price=price,
            anonce=anonce,
            count=count
        )

        try:
            db.session.add(produc)
            db.session.commit()
            flash('Товар добавлен', 'info')
            return redirect(url_for('.product'))
        except:
            flash('При добавление данных произошла ошибка', 'info')
            return render_template("admin/product.html")
    else:

        prod = Product.query.order_by(Product.author).all()
        return render_template("admin/product.html", prod=prod)


@admin.route('/create/<int:id>', methods=["GET", "POST"])
def create(id):
    if not isLogged():
        return redirect(url_for('login'))

    stud = Product.query.get(id)

    if request.method == "POST":
        stud.author = request.form['author']
        stud.name = request.form['name']
        stud.time = request.form['time']
        stud.house = request.form['house']
        stud.price = request.form['price']
        stud.anonce = request.form['anonce']
        stud.count = request.form['count']

        try:
            db.session.commit()
            flash('Товар изменен', 'info')
            return redirect(url_for('.product'))
        except:
            flash('Ошибка обновления', 'info')
            return render_template("admin/create.html", stud=stud)

    else:
        return render_template("admin/create.html", stud=stud)


@admin.route('/delete/<int:id>')
def delete(id):
    if not isLogged():
        return redirect(url_for('login'))

    proverka = Orders.query.filter_by(product=id).all()

    if proverka:
        flash('Товар нельзя удалить', 'info')
        return redirect(url_for('.product'))
    else:
        student_to_delete = Product.query.get(id)
        try:
            db.session.delete(student_to_delete)
            db.session.commit()
            flash('Товар удален', 'info')
            return redirect(url_for('.product'))
        except:
            flash('Ошибка удаления', 'info')
            return redirect(url_for('.product'))


@admin.route('/prod/<int:id>')
def prod(id):
    if not isLogged():
        return redirect(url_for('login'))

    prod = Product.query.get(id)
    return render_template('admin/prod.html', prod=prod)


@admin.route('/search', methods=["POST", "GET"])
def search():

    book = 0

    if request.method == 'POST':
        author = request.form.get('author')
        name = request.form.get('name')

        if author and not name:
            book = Product.query.filter(Product.name.ilike(f'%{author}%')).all()
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/admin/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/admin/search.html')

        if not author and name:
            book = Product.query.filter(Product.name.ilike(f'%{name}%')).all()
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/admin/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/admin/search.html')

        if author and name:
            book = Product.query.filter(Product.name.ilike(f'%{author}%'), Product.name.ilike(f'%{name}%')).all()
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/admin/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/admin/search.html')

    return render_template('/admin/search.html')


