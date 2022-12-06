from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pw = db.Column(db.String(200), nullable=False)
    isDriver = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Login %r>' % self.id


class Passenger(db.Model):
    __tablename__ = 'passenger'
    d_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default='')
    phoneNumber = db.Column(db.String(200), default='')
    address = db.Column(db.String(200), default='')
    card_info = db.Column(db.String(200), default='')
    balance = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Login %r>' % self.d_id


class Driver(db.Model):
    __tablename__ = 'driver'
    d_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default='')
    phoneNumber = db.Column(db.String(200), default='')
    address = db.Column(db.String(200), default='')
    card_info = db.Column(db.String(200), default='')

    # todo: add car's info to Driver
    def __repr__(self):
        return '<Login %r>' % self.d_id


class Order(db.Model):
    o_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    d_id = db.Column(db.Integer, db.ForeignKey('driver.d_id'), default=-1)
    p_id = db.Column(db.Integer, db.ForeignKey('passenger.d_id'))
    pick_up = db.Column(db.String(200), default='')
    drop_off = db.Column(db.String(200), default='')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    accept = db.Column(db.Boolean, default=False)
    done = db.Column(db.Boolean, default=False)
    payment_amount = db.Column(db.Integer)

    def __repr__(self):
        print("HERE")
        return '<Login %r>' % self.o_id


class Appointment(db.Model):
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    d_id = db.Column(db.Integer, db.ForeignKey('driver.d_id'))
    p_id = db.Column(db.Integer, db.ForeignKey('passenger.d_id'))
    planned_pickup = db.Column(db.String(200), default='')
    planned_destination = db.Column(db.String(200), default='')
    planned_start_time = db.Column(db.String(200), default='')
    planned_payment_amount = db.Column(db.Integer)
    status = db.Column(db.String(200), default='')

    def __repr__(self):
        return '<Login %r>' % self.a_id


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if (request.form['btn'] == 'login'):
            login_id = request.form['id']
            login_pw = request.form['password']
            exists = db.session.query(db.exists().where(User.id == login_id)).scalar()
            if (not exists):
                flash('Error: id not exists')
                return redirect('/')

            user = User.query.get_or_404(login_id)
            is_driver = user.isDriver
            try:
                if (user.pw == login_pw):
                    if (is_driver):
                        return redirect(url_for('homepage_d', id=login_id))
                    else:
                        return redirect(url_for('homepage_p', id=login_id))
                else:
                    flash('Error: password not match')
                    return redirect('/')

            except:
                return 'Homepage not implemented yet'
        elif (request.form['btn'] == 'register'):
            return redirect('/register')
    else:
        return render_template('login.html')


@app.route('/homepage_p/<int:id>', methods=['POST', 'GET'])
def homepage_p(id):
    if request.method == 'GET':
        passenger = Passenger.query.get_or_404(id)
        # Not sure if added function: check if driver already have an order
        order = Order.query.filter(Order.p_id == id).filter(Order.done == False).all()
        if (order):
            flash("You have an ongoing order")
            return redirect(url_for('order_w_o', o_id=order[0].o_id, u_id=order[0].p_id))
        else:
            return render_template('homepage_passenger.html', tasks=passenger)
    elif request.method == 'POST':
        if (request.form['btn'] == 'edit_user_info'):
            passenger = Passenger.query.get_or_404(id)
            if (request.form['name'] != ''):
                passenger.name = request.form['name']
            if (request.form['phoneNumber'] != ''):
                passenger.phoneNumber = request.form['phoneNumber']
            if (request.form['address'] != ''):
                passenger.address = request.form['address']
            if (request.form['card_info'] != ''):
                passenger.card_info = request.form['card_info']
            try:
                db.session.commit()
                flash("updated")
                return render_template('homepage_passenger.html', tasks=passenger)
            except:
                return "something wrong"
        elif request.form['btn'] == 'post_order':
            passenger = Passenger.query.get_or_404(id)
            Passenger.pick_up = request.form['pick_up']
            Passenger.drop_off = request.form['drop_off']
            payment = request.form['payment_amount']
            new_order = Order(p_id=id, pick_up=request.form['pick_up'], drop_off=request.form['drop_off'],
                              date_created=datetime.now(), payment_amount=payment)
            try:
                db.session.add(new_order)
                db.session.commit()
                flash("you have successfully Post a new order")
            except Exception as e:
                flash(str(e))
            return redirect(url_for('order_w_o', o_id=new_order.o_id, u_id=new_order.p_id))
        elif request.form['btn'] == 'post_appointment':
            passenger = Passenger.query.get_or_404(id)
            planned_start_time = request.form['start_time']
            planned_payment_amount = request.form['planned_payment']
            planned_pickup = request.form['pick_up_app']
            planned_destination = request.form['drop_off_app']
            if planned_pickup and planned_destination and planned_start_time and planned_payment_amount:
                new_appointment = Appointment(p_id=id, planned_start_time=planned_start_time
                                              , planned_payment_amount=planned_payment_amount, planned_pickup=
                                              planned_pickup, planned_destination=planned_destination,
                                              status='available')
                try:
                    db.session.add(new_appointment)
                    db.session.commit()
                    flash("Inserted a new appointment")
                except Exception as e:
                    flash(e)
            return render_template('homepage_passenger.html', tasks=passenger)


@app.route('/homepage_d/<int:id>', methods=['POST', 'GET'])
def homepage_d(id):
    if request.method == 'GET':
        driver = Driver.query.get_or_404(id)
        # Not sure if added function: check if driver already have an order
        order = Order.query.filter(Order.d_id == id).filter(Order.done == False).all()
        if(order):
            flash("you have an ongoing order")
            return render_template('order_waiting_driver.html', o_id=order[0].o_id, u_id=id)
        else:
            return render_template('homepage_driver.html', tasks=driver)

    elif request.method == 'POST':
        if (request.form['btn'] == 'edit_user_info'):
            driver = Driver.query.get_or_404(id)
            driver.name = request.form['name']
            driver.phoneNumber = request.form['phoneNumber']
            driver.address = request.form['address']
            driver.card_info = request.form['card_info']
            try:
                db.session.commit()
                flash("updated")
                return render_template('homepage_driver.html', tasks=driver)
            except:
                return "something wrong"

        elif (request.form['btn'] == 'check_appointment'):
            return redirect(url_for('appointment_d', id=id))

        elif (request.form['btn'] == 'check_order'):
            return redirect(url_for('order_d', id=id))


@app.route('/order_p/<int:id>', methods=['POST', 'GET'])
def order_p(id):
    if request.method == 'GET':
        orders = Order.query.filter_by(p_id=id).all()
        return render_template('order_passenger.html', tasks=orders, id=id)


@app.route('/order_d/<int:id>', methods=['POST', 'GET'])
def order_d(id):
    driver = Driver.query.get_or_404(id)
    if request.method == 'POST':
        if (request.form['btn'] == 'Order_by_early'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.date_created).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
        elif (request.form['btn'] == 'Order_by_latest'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.date_created.desc()).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
        elif (request.form['btn'] == 'Order_by_pick_up'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.pick_up).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
        elif (request.form['btn'] == 'Order_by_drop_off'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.drop_off).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
        elif (request.form['btn'] == 'Order_by_payment'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.payment_amount.desc()).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
        elif (request.form['btn'] == 'refresh'):
            orders = Order.query.filter(Order.accept == False).filter(Order.done == False).order_by(
                Order.date_created).limit(7).all()
            return render_template('order_driver.html', tasks=orders, driver=driver)
    else:
        orders = Order.query.filter(Order.accept == False).filter(Order.done == False).limit(7).all()
        return render_template('order_driver.html', tasks=orders, driver=driver)


@app.route('/accept_order/<d_id>/<o_id>', methods=['POST'])
def accept_order(d_id, o_id):
    driver = Driver.query.get_or_404(d_id)
    if request.method == 'POST':
        if (request.form['btn1'] == 'Accept'):
            order = Order.query.filter(Order.o_id == o_id).all()
            if(order):
                sel_order = Order.query.get_or_404(o_id)
                sel_order.d_id = d_id
                sel_order.accept = True
                db.session.commit()
                flash("Accept successfully")
                return redirect(url_for('order_wo_d', o_id=o_id, u_id=d_id))
            else:
                flash("This order has been canceled")
                orders = Order.query.filter(Order.accept == False).filter(Order.done == False).limit(7).all()
                return render_template('order_driver.html', tasks=orders, driver=driver)

@app.route('/cancel_order/<p_id>/<o_id>', methods=['POST'])
def cancel_order(p_id, o_id):
    if request.method == 'POST':
        if (request.form['btn1'] == 'Cancel'):
            sel_order = Order.query.get_or_404(o_id)
            db.session.delete(sel_order)
            db.session.commit()
            flash("Cancel Order successfully")
            return redirect(url_for('homepage_p', id=p_id))

@app.route('/view_driver_inOrder/<o_id>', methods=['POST'])
def view_driver_inOrder(o_id):
    if request.method == 'POST':
        if (request.form['btn1'] == 'ViewDriverInfo'):
            sel_order = Order.query.get_or_404(o_id)
            driver_id = sel_order.d_id
            return redirect(url_for('profilePage', id=driver_id))


@app.route("/register", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        login_id = int(request.form['id'])
        login_pw = request.form['password']
        login_isDriver = request.form['isDriver']
        if login_isDriver == "yes":
            login_isDriver = True
            temp = Driver(d_id=login_id)
            db.session.add(temp)
            db.session.commit()
        else:
            login_isDriver = False
            temp = Passenger(d_id=login_id)
            db.session.add(temp)
            db.session.commit()

        new_login = User(id=login_id, pw=login_pw, isDriver=login_isDriver)

        try:
            db.session.add(new_login)
            db.session.commit()
            flash("you have successfully registered")
            return redirect('/register')
        except:
            flash("wrong user id")
            return redirect("/register")
    else:
        logins = User.query.order_by(User.id).all()
        return render_template('index.html', tasks=logins)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        login_id = request.form['id']
        login_pw = request.form['password']
        login_isDriver = request.form['isDriver']
        if login_isDriver == "yes":
            login_isDriver = True
            temp = Driver(d_id=login_id)
            db.session.add(temp)
            db.session.commit()
        else:
            login_isDriver = False
            temp = Passenger(d_id=login_id)
            db.session.add(temp)
            db.session.commit()
        new_login = User(id=login_id, pw=login_pw, isDriver=login_isDriver)

        try:
            db.session.add(new_login)
            db.session.commit()
            flash("you have successfully registered")
            return redirect('/admin')
        except:
            flash("wrong user info")
            return redirect("/admin")
    else:
        logins = User.query.order_by(User.id).all()
        return render_template('admin.html', tasks=logins)


@app.route('/delete/<int:id>')
def delete(id):
    # get the value by id, if not found then 404
    delete_login = User.query.get_or_404(id)

    try:
        db.session.delete(delete_login)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'There was a problem deleting that registration'


@app.route('/deleteOrder/<int:Uid>/<int:id>', methods=['GET'])
def deleteOrder(Uid, id):
    # get the value by id, if not found then 404
    app.logger.info(Uid)
    order = Order.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/order_p/' + str(Uid))
    except:
        return 'There was a problem deleting that registration'


@app.route('/appointment/<int:id>', methods=['POST', 'GET'])
def appointment(id):
    if request.method == 'GET':
        appointments = Appointment.query.filter_by(p_id=id).all()
    return render_template('appointment.html', tasks=appointments, id=id)

@app.route('/appointment_d/<int:id>', methods=['POST', 'GET'])
def appointment_d(id):
    if request.method == 'GET':
        appointments = Appointment.query.filter().limit(5).all()
        return render_template('appointment_driver.html', tasks=appointments)
    elif request.method == 'POST':
        if (request.form['btn'] == 'Order_by_id'):
            appointments = Appointment.query.order_by(Appointment.a_id).all()
            return render_template('appointment_driver.html', tasks=appointments)
        elif (request.form['btn'] == 'Order_by_id'):
            appointments = Appointment.query.order_by(Appointment.planned_start_time).all()
            return render_template('appointment_driver.html', tasks=appointments)

@app.route('/deleteAppointment/<int:Uid>/<int:id>', methods=['GET'])
def deleteAppointment(Uid, id):
    # get the value by id, if not found then 404
    app.logger.info(Uid)
    appoint = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appoint)
        db.session.commit()
        return redirect('/appointment/' + str(Uid))
    except:
        return 'There was a problem deleting that registration'


@app.route('/profilePage/<int:id>', methods=['GET'])
def profilePage(id):
    if request.method == 'GET':
        passenger = Passenger.query.get_or_404(id)
        return render_template('profile.html', tasks=passenger)
    else:
        return "something wrong"


@app.route('/order_waiting_ongoing/<int:o_id>/<int:u_id>', methods=['POST', 'GET'])
def order_w_o(o_id, u_id):
    order = Order.query.get_or_404(o_id)
    if (request.method == 'GET'):
        if order.d_id == -1:
            return render_template('order_waiting.html', o_id=o_id, u_id=u_id)
        else:
            return render_template('order_ongoing.html', o_id=o_id, u_id=u_id)
    else:
        order.done = True
        db.session.commit()
        flash("your order has completed")
        user = User.query.get_or_404(u_id)
        if user.isDriver:
            return redirect(url_for('homepage_d', id=u_id))
        else:
            return redirect(url_for('homepage_p', id=u_id))

@app.route('/order_w_o_driver/<int:o_id>/<int:u_id>', methods=['GET'])
def order_wo_d(o_id, u_id):
    order = Order.query.get_or_404(o_id)
    if (request.method == 'GET'):
        if order.done == False:
            return render_template('order_waiting_driver.html', o_id=o_id, u_id=u_id)
        else:
            flash("order complete!")
            return redirect(url_for('homepage_d', id=u_id))


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
