from flask import Blueprint, session, render_template, request, url_for, redirect, flash
from config import db
from models import Orders, Delivary, ChatMessage, Users

delivery = Blueprint('delivery', __name__, template_folder='templates', static_folder='static')


def login_delivery(u):
    session['delivery_logged'] = u


def isLogged():
    return True if session.get('delivery_logged') else False


def logout_delivery():
    session.pop('delivery_logged', None)


@delivery.route('/', methods=["POST", "GET"])
@delivery.route('/index', methods=["POST", "GET"])
def index():
    if not isLogged():
        return redirect(url_for('login'))

    if request.method == "POST":
        name = request.form['name']
        login = request.form['login']
        number = request.form['number']
        days = request.form['days']
        price = request.form['price']
        about = request.form['about']

        deliv = Delivary(
            name=name,
            login=login,
            number=number,
            days=days,
            price=price,
            about=about
        )

        try:
            db.session.add(deliv)
            db.session.commit()
            flash('Доставка добавлена', 'info')
            return redirect(url_for('.index'))
        except:
            flash('Ошибка')
    else:
        info = Delivary.query.all()
        return render_template('delivery/index.html', info=info)


@delivery.route('/createDel/<int:id>', methods=["GET", "POST"])
def createDel(id):
    if not isLogged():
        return redirect(url_for('login'))

    stud = Delivary.query.get(id)

    if request.method == "POST":
        stud.name = request.form['name']
        stud.login = request.form['login']
        stud.number = request.form['number']
        stud.days = request.form['days']
        stud.price = request.form['price']
        stud.about = request.form['about']

        try:
            db.session.commit()
            flash('Доставка изменена', 'info')
            return redirect(url_for('.index'))
        except:
            flash('Ошибка обновления', 'info')
            return render_template("delivery/index.html", stud=stud)

    else:
        return render_template("delivery/createDel.html", stud=stud)

@delivery.route('/deleteDel/<int:id>')
def deleteDel(id):
    if not isLogged():
        return redirect(url_for('login'))

    student_to_delete = Delivary.query.get(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash('Товар удален', 'info')
        return redirect(url_for('.index'))
    except:
        flash('ошибка', 'info')
        return redirect(url_for('.index'))


@delivery.route("/orders", methods=["POST", "GET"])
def orders():
    if not isLogged():
        return redirect(url_for('login'))


    user1 = []
    info1 =[]

    try:
        info = Orders.query.filter_by(state='Ждет подтверждения').all()
        info1 = info

        for i in info1:
            uss = Users.query.filter_by(username=i.login).all()
            user1 += uss

    except:
        print("ОШИБКА")

    else:
        ord = Orders.query.order_by(Orders.id).all()
        return render_template("/delivery/orders.html", ord=ord, list=info1, user1=user1)


@delivery.route('/look/<int:id>')
def look(id):
    if not isLogged():
        return redirect(url_for('login'))

    look = Orders.query.get(id)
    user = Users.query.filter_by(username=look.login).first()
    return render_template('/delivery/look.html', look=look, user=user)


@delivery.route('/accept/<int:id>')
def accept(id):
    if not isLogged():
        return redirect(url_for('login'))

    ord = Orders.query.get(id)
    ord.state = 'На складе'

    try:
        db.session.commit()
        flash('Заказ принят', 'info')
        return redirect(url_for('.orders'))
    except:
        return "Error"


@delivery.route("/information", methods=["POST", "GET"])
def information():
    if not isLogged():
        return redirect(url_for('login'))

    info = []
    user = []
    try:
        info = Orders.query.filter_by(state='Заказ прибыл к месту назначения').all()
        info += Orders.query.filter_by(state='Заказ в пути').all()
        info += Orders.query.filter_by(state='На складе').all()

        for i in info:
            us = Users.query.filter_by(username=i.login).all()
            user += us
    except:
        print("Error")
    return render_template('/delivery/ordersaccept.html', list = info, user=user)


@delivery.route('/delete/<int:id>')
def delete(id):
    if not isLogged():
        return redirect(url_for('login'))

    student_to_delete = Orders.query.get(id)
    student_to_delete.state = 'Заказ отклонен'
    try:
        # db.session.delete(student_to_delete)
        db.session.commit()
        # flash('Заказ отклонен', 'info')
        return redirect(url_for('.orders'))
    except:
        flash('Ошибка удаления', 'info')
        return redirect(url_for('.orders'))


@delivery.route('/delete1/<int:id>')
def delete1(id):
    if not isLogged():
        return redirect(url_for('login'))

    student_to_delete = Orders.query.get(id)
    try:
        db.session.delete(student_to_delete)
        db.session.commit()
        flash('Заказ завершен', 'info')
        return redirect(url_for('.information'))
    except:
        flash('Ошибка удаления', 'info')
        return redirect(url_for('.orders'))


@delivery.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('login'))

    logout_delivery()

    return redirect(url_for('login'))


@delivery.route("/msg", methods=["POST", "GET"])
def msg():
    if not isLogged():
        return redirect(url_for('login'))

    if request.method == "POST":

        username = request.form.get("username")
        msg1 = request.form.get('msg')

        message = ChatMessage(
            username=username,
            msg=msg1,
            name='delivery'
        )
        try:
            if username and msg1:
                db.session.add(message)
                db.session.commit()
                flash('Сообщение отправлено', 'info')
                return redirect(url_for('.msg'))
        except:
            flash('Ошибка отправки', 'info')
            return render_template('/delivery/msg.html')
    else:
        mes1 = ChatMessage.query.filter_by(name='delivery').all()
        mes = ChatMessage.query.filter_by(username='delivery').all()
        return render_template("/delivery/msg.html", mes=mes, mes1=mes1)

    return render_template('/delivery/msg.html')


@delivery.route('/deleteMsg/<int:id>')
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
        return render_template("/delivery/msg.html")


@delivery.route("/delivary", methods=["POST", "GET"])
def delivary():
    if not isLogged():
        return redirect(url_for('login'))

    info = []
    try:
        info = Delivary.query.all()
    except:
        print("ОШИБКА")

    return render_template('/delivery/delivary.html', list = info)


@delivery.route('/create/<int:id>', methods=["GET", "POST"])
def create(id):

    stud = Orders.query.get(id)

    if request.method == "POST":
        stud.state = request.form['state']

        try:
            db.session.commit()
            flash('Данные обновлены', 'info')
            return redirect(url_for('.information'))
        except:
            flash('Ошибка обновления', 'info')
            return render_template("delivery/create.html", stud=stud)

    else:
        return render_template("delivery/create.html", stud=stud)
