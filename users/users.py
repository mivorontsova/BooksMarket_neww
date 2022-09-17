from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, logout_user, current_user, login_required
from config import generate_password_hash, check_password_hash
from sqlalchemy import func

from config import db
from models import Profiles, ChatMessage, Users, Product, Orders, Delivary, ProductAccept

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')

login_manager = LoginManager(users)


@login_manager.user_loader
def load_user(profile_id):
    return Profiles.query.get(profile_id)


@users.route('/')
@users.route('/index')
@login_required
def index():
    prod = Product.query.order_by(Product.author).all()
    return render_template('users/index.html', prod=prod)


@users.route('/prod/<int:id>')
@login_required
def prod(id):
    prod = Product.query.get(id)
    return render_template('/users/prod.html', prod=prod)


@users.route('/search', methods=["POST", "GET"])
@login_required
def search():
    book = 0
    if request.method == 'POST':
        author = request.form.get('author')
        name = request.form.get('name')
        if author and not name:
            # book = Product.query.filter(author=author1).all()
            book = Product.query.filter(Product.author.ilike(f'%{author}%'))
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/users/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/users/search.html')

        if not author and name:
            book = Product.query.filter(Product.name.ilike(f'%{name}%')).all()
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/users/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/users/search.html')

        if author and name:
            book = Product.query.filter(Product.author.ilike(f'%{author}%'), Product.name.ilike(f'%{name}%')).all()
            if book:
                flash('Результаты найдены', 'info')
                return render_template('/users/search.html', book=book)
            else:
                flash('Результаты не найдены', 'info')
                return render_template('/users/search.html')
    return render_template('/users/search.html')


@users.route('/orders/<int:id>', methods=["POST", "GET"])
@login_required
def orders(id):
    idr = current_user.get_id()

    stud = Users.query.get(idr)

    ac = ProductAccept.query.get(id)

    pr = Product.query.get(ac.id_prod)

    if pr.count == 0:
        flash('Нет в наличии', 'info')
        return redirect(url_for('users.cart'))
    if request.method == "POST":
        login = request.form['login']
        product = request.form['product']
        delivary = request.form['delivary']
        live = request.form['live']

        orders = Orders(
            login=login,
            product=product,
            delivary=delivary,
            live=live,
            state='Ждет подтверждения'
        )

        try:
            pr.count = pr.count - 1
            db.session.add(orders, pr.count)
            db.session.delete(ProductAccept.query.get(id))
            db.session.commit()
            flash('Товар успешно заказан! Посмотреть все заказы Вы можете в профиле', 'info')
            return redirect(url_for('.index'))
        except:
            flash('При оформлении заказа произошла ошибка', 'info')
            return redirect(url_for('.index'))
    else:
        ord = Orders.query.order_by(Orders.id).all()
        flash('Введите данные', 'info')
        return render_template("/users/orders.html", ord=ord, stud=stud, pr=pr)


@users.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@users.route('/msg', methods=["POST", "GET"])
@login_required
def msg():
    uid = current_user.get_id()

    so = Profiles.query.get(uid)

    if request.method == "POST":

        username = request.form.get("username")
        msg1 = request.form.get('msg')

        message = ChatMessage(
            username=username,
            msg=msg1,
            name=so.username
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
        mes1 = ChatMessage.query.filter_by(name=so.username).all()
        mes = ChatMessage.query.filter_by(username=so.username).all()
        return render_template("users/msg.html", mes=mes, mes1=mes1)


@users.route('/deleteMsg/<int:id>')
@login_required
def deleteMsg(id):
    msg_to_delete = ChatMessage.query.get(id)
    try:
        db.session.delete(msg_to_delete)
        db.session.commit()
        flash('Сообщение удалено', 'info')
        return redirect(url_for('.msg'))
    except:
        return "Ошибка удаления"


@users.route('/deleteOrd1/<int:id>')
@login_required
def deleteOrd1(id):
    student_to_delete = Orders.query.get(id)
    pr = Product.query.get(student_to_delete.product)
    try:
        db.session.delete(student_to_delete)
        pr.count = pr.count + 1
        db.session.commit()
        flash('Ваш заказ успешно отменен', 'info')
        return redirect(url_for('.create'))
    except:
        return "ОШИБКА"


@users.route('/deleteOrd/<int:id>')
@login_required
def deleteOrd(id):
    student_to_delete = Orders.query.get(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash('Вы подтвердили получение заказа', 'info')
        return redirect(url_for('.create'))
    except:
        flash('Вы отменили заказ', 'info')
        return redirect(url_for('.create'))


@users.route('/create', methods=["GET", "POST"])
@login_required
def create():
    prod = []
    info1 = []
    info2 = []
    prod1 = []

    id = current_user.get_id()

    stud = Users.query.get(id)
    p = Profiles.query.get(stud.profile_id)

    orderss = Orders.query.filter_by(login=stud.username, state="Ждет подтверждения").all()

    info = Orders.query.filter_by(login=stud.username, state="На складе").all()
    info += Orders.query.filter_by(login=stud.username, state='Заказ в пути').all()
    info += Orders.query.filter_by(login=stud.username, state='Заказ прибыл к месту назначения').all()

    info1 = orderss
    info2 = info

    for i in info1:
        sa = Users.query.filter_by(username=i.login).all()
        prod += sa

    for i in info2:
        sa1 = Users.query.filter_by(username=i.login).all()
        prod1 += sa1

    if request.method == "POST":
        stud.name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        stud.psw = request.form['psw']
        psw2 = request.form['psw2']

        hash = generate_password_hash(psw2)

        if Users.query.filter_by(email=email).all() and Users.query.filter_by(
                email=email).all() != Users.query.filter_by(id=id).all():
            flash('Почта занята. Введите другую почту', 'info')
            return redirect(url_for(".create"))
        else:
            stud.email = email

        if Users.query.filter_by(number=number).all() and Users.query.filter_by(
                number=number).all() != Users.query.filter_by(id=id).all():
            flash('Номер занят. Введите другой номер', 'info')
            return redirect("/users/create")
        else:
            stud.number = number

        try:
            if check_password_hash(stud.psw, psw2):
                db.session.commit()
                flash('Ваши данные успешно обновлены', 'info')
                return redirect(url_for('.create'))
            else:
                flash('Пароли не совпадают', 'info')
                return render_template("users/create.html", stud=stud, list=orderss, info=info, prod=prod, prod1=prod1)
        except:
            flash('Ошибка обновления', 'info')
            return render_template("users/create.html", stud=stud, list=orderss, info=info, prod=prod, prod1=prod1)
    else:
        return render_template("users/create.html", stud=stud, list=orderss, info=info, prod=prod, prod1=prod1)


@users.route("/delivary", methods=["POST", "GET"])
@login_required
def delivary():
    info = []
    try:
        info = Delivary.query.all()
    except:
        print("ОШИБКА")

    return render_template('/users/delivary.html', list=info)


@users.route('/accept/<int:id>')
@login_required
def accept(id):
    idr = current_user.get_id()
    us = Users.query.get(idr)
    book_to_accept = Product.query.get(id)
    bookAccept = ProductAccept(
        state='Заказ в корзине',
        id_prod=book_to_accept.id,
        username=us.username
    )
    try:
        db.session.add(bookAccept)
        db.session.commit()
        flash('Товар был успешно добавлен в корзину', 'info')
        return redirect(url_for('.index'))
    except:
        flash('Произошла ошибка', 'info')
        return redirect(url_for('.index'))


@users.route("/cart", methods=["POST", "GET"])
@login_required
def cart():
    info = []
    prod = []

    uid = current_user.get_id()
    so = Profiles.query.get(uid)
    try:
        list = ProductAccept.query.filter_by(username=so.username).all()
        info = list

        for i in list:
            # print(i.id_prod)
            sa = Product.query.filter_by(id=i.id_prod).all()
            prod += sa

    except:
        print('ОШИБКА')
    return render_template('/users/cart.html', list=info, prod=prod)


@users.route('/deleteCart/<int:id>')
@login_required
def deleteCart(id):
    student_to_delete = ProductAccept.query.get(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash('Товар был удален из Вашей корзины', 'info')
        return redirect(url_for('.cart'))
    except:
        return "ОШИБКА"
