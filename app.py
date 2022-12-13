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
    accept = db.Column(db.Boolean, default=False)
    done = db.Column(db.Boolean, default=False)

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

            # prepared statement
            query = "SELECT * FROM User WHERE id = :user_id"
            user_ = db.engine.execute(query, user_id=login_id)
            user = user_.first()

            user_pw = user['pw']

            is_driver = user['isDriver']

            # user = User.query.get_or_404(login_id)
            try:
                if (user_pw == login_pw):
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
        # passenger = Passenger.query.get_or_404(id)
        # prepared statement
        query = "SELECT * FROM Passenger WHERE d_id = :psg_id"
        psg_ = db.engine.execute(query, psg_id=id)
        passenger = psg_.first()

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
            # passenger = Passenger.query.get_or_404(id)

            # prepared statement
            query = "SELECT * FROM Passenger WHERE d_id = :psg_id"
            psg_ = db.engine.execute(query, psg_id=id)
            passenger = psg_.first()

            pick_up = request.form['pick_up']
            drop_off = request.form['drop_off']
            payment = request.form['payment_amount']
            if(pick_up and drop_off and payment):
                new_order = Order(p_id=id, pick_up=request.form['pick_up'], drop_off=request.form['drop_off'],
                                  date_created=datetime.now(), payment_amount=payment)
                try:
                    db.session.add(new_order)
                    db.session.commit()
                    flash("you have successfully Post a new order")
                except Exception as e:
                    flash(str(e))
                return redirect(url_for('order_w_o', o_id=new_order.o_id, u_id=new_order.p_id))
            else:
                flash("Lack order information")
                return render_template('homepage_passenger.html', tasks=passenger)

        elif request.form['btn'] == 'post_appointment':
            # passenger = Passenger.query.get_or_404(id)

            # prepared statement
            query = "SELECT * FROM Passenger WHERE d_id = :psg_id"
            psg_ = db.engine.execute(query, psg_id=id)
            passenger = psg_.first()
            #print(passenger)

            planned_start_time = request.form['start_time']
            planned_payment_amount = request.form['planned_payment']
            planned_pickup = request.form['pick_up_app']
            planned_destination = request.form['drop_off_app']

            new_appointment = Appointment(p_id=id, planned_start_time=planned_start_time
                                        , planned_payment_amount=planned_payment_amount, planned_pickup=
                                        planned_pickup, planned_destination=planned_destination)
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
        # driver = Driver.query.get_or_404(id)

        # prepared statement
        query = "SELECT * FROM Driver WHERE d_id = :id"
        dr_ = db.engine.execute(query, id=id)
        driver = dr_.first()
        # Not sure if added function: check if driver already have an order
        order = Order.query.filter(Order.d_id == id).filter(Order.done == False).all()
        if(order):
            flash("you have an ongoing order")
            return render_template('order_ongoing_driver.html', task=order[0])
        else:
            return render_template('homepage_driver.html', tasks=driver)

    elif request.method == 'POST':
        if (request.form['btn'] == 'edit_user_info'):
            driver = Driver.query.get_or_404(id)

            if (request.form['name'] != ''):
                driver.name = request.form['name']
            if (request.form['phoneNumber'] != ''):
                driver.phoneNumber = request.form['phoneNumber']
            if (request.form['address'] != ''):
                driver.address = request.form['address']
            if (request.form['card_info'] != ''):
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
            if order:
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
@app.route('/change_appointment/<o_id>/<p_id>', methods=['GET','POST'])
def change_appointment(p_id, o_id):
    passenger = Passenger.query.get_or_404(p_id)
    if request.method == 'GET':
        return render_template('changeAppointment.html', passenger=p_id, o_id=o_id)
    else:
        appointment = Appointment.query.get_or_404(o_id)
        if (request.form['pick_up_app'] != ''):
            appointment.planned_pickup = request.form['pick_up_app']
        if (request.form['drop_off_app'] != ''):
            appointment.planned_destination = request.form['drop_off_app']
        if(request.form['start_time'] != ''):
            appointment.planned_start_time = request.form['start_time']
        if(request.form['planned_payment'] != ''):
            appointment.planned_payment_amount = request.form['planned_payment']
        db.session.commit()
        appointments = Appointment.query.filter_by(p_id=p_id).all()
        return render_template('appointment.html', tasks=appointments, id=p_id)

@app.route('/cancel_order/<p_id>/<o_id>', methods=['POST'])
def cancel_order(p_id, o_id):
    if request.method == 'POST':
        if (request.form['btn1'] == 'Cancel'):
            # sel_order = Order.query.get_or_404(o_id)

            # prepared statement
            query = "DELETE FROM 'Order' WHERE o_id = :id"
            db.engine.execute(query, id=o_id)

            db.session.commit()
            flash("Cancel Order successfully")
            return redirect(url_for('homepage_p', id=p_id))

@app.route('/view_driver_inOrder/<o_id>', methods=['POST'])
def view_driver_inOrder(o_id):
    if request.method == 'POST':
        if (request.form['btn1'] == 'ViewDriverInfo'):
            sel_order = Order.query.get_or_404(o_id)
            driver_id = sel_order.d_id
            return redirect(url_for('profilePage_driver', id=driver_id))


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

    # prepared statement
    query = "DELETE FROM User WHERE id = :u_id"
    db.engine.execute(query, u_id=id)
    db.session.commit()
    return redirect('/admin')


@app.route('/deleteOrder/<int:Uid>/<int:id>', methods=['GET'])
def deleteOrder(Uid, id):
    # prepared statement
    query = "DELETE FROM 'Order' WHERE o_id = :id"
    db.engine.execute(query, id=id)
    return redirect('/order_p/' + str(Uid))


@app.route('/appointment/<int:id>', methods=['POST', 'GET'])
def appointment(id):
    if request.method == 'GET':
        appointments = Appointment.query.filter_by(p_id=id).all()
    elif request.method =='POST':
        if(request.form['btn'] == 'Order_by_pick_up'):
            appointments = Appointment.query.filter_by(p_id=id).order_by(Appointment.planned_start_time).all()
        elif(request.form['btn'] == 'Order_by_drop_off'):
            appointments = Appointment.query.filter_by(p_id=id).order_by(Appointment.planned_destination).all()
        elif(request.form['btn'] == 'Order_by_payment'):
            appointments = Appointment.query.filter_by(p_id=id).order_by(Appointment.planned_payment_amount).all()
        elif(request.form['btn'] == 'Filter Payment Amount'):
            appointments = Appointment.query.filter_by(p_id=id).filter(Appointment.planned_payment_amount >= request.form['Lowest Payment']).filter(Appointment.planned_payment_amount <= request.form['Highest Payment']).all()
    return render_template('appointment.html', tasks=appointments, id=id)

@app.route('/appointment_d/<int:id>', methods=['POST', 'GET'])
def appointment_d(id):
    driver = Driver.query.get_or_404(id)
    if request.method == 'POST':
        if (request.form['btn'] == 'Order_by_early'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_start_time).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
        elif (request.form['btn'] == 'Order_by_latest'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_start_time.desc()).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
        elif (request.form['btn'] == 'Order_by_pick_up'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_pickup).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
        elif (request.form['btn'] == 'Order_by_drop_off'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_destination).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
        elif (request.form['btn'] == 'Order_by_payment'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_payment_amount.desc()).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
        elif (request.form['btn'] == 'refresh'):
            appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).order_by(
                Appointment.planned_start_time).limit(7).all()
            return render_template('appointment_driver.html', tasks=appointments, driver=driver)
    else:
        appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).limit(7).all()
        return render_template('appointment_driver.html', tasks=appointments, driver=driver)


@app.route('/get_appointment/<d_id>/<a_id>', methods=['POST'])
def get_appointment(d_id, a_id):
    driver = Driver.query.get_or_404(d_id)
    if request.method == 'POST':
        if request.form['btn1'] == 'Get this appointment':
            appointment = Appointment.query.filter(Appointment.a_id == a_id).all()
            if appointment:
                sel_app = Appointment.query.get_or_404(a_id)
                sel_app.d_id = d_id
                sel_app.accept = True
                db.session.commit()
                flash("Get successfully")
                appointments = Appointment.query.filter(Appointment.accept == False).filter(Appointment.done == False).limit(7).all()
                return render_template('appointment_driver.html', tasks=appointments, driver=driver)
            else:
                flash("Appointment deleted")
                appointments = Order.query.filter(Appointment.accept == False).filter(Appointment.done == False).limit(7).all()
                return render_template('appointment_driver.html', tasks=appointments, driver=driver)


@app.route('/deleteAppointment/<int:Uid>/<int:id>', methods=['GET'])
def deleteAppointment(Uid, id):
    # get the value by id, if not found then 404
    # prepared statement
    query = "DELETE FROM Appointment WHERE a_id = :id"
    db.engine.execute(query, id=id)
    return redirect('/appointment/' + str(Uid))


@app.route('/profilePage/<int:id>', methods=['GET'])
def profilePage(id):
    if request.method == 'GET':
        # passenger = Passenger.query.get_or_404(id)
        # prepared statement
        query = "SELECT * FROM Passenger WHERE d_id = :psg_id"
        psg_ = db.engine.execute(query, psg_id=id)
        passenger = psg_.first()
        return render_template('profile.html', tasks=passenger)
    else:
        return "something wrong"
@app.route('/profilePage_driver/<int:id>', methods=['GET'])
def profilePage_driver(id):
    if request.method == 'GET':
        # driver = Driver.query.get_or_404(id)
        # prepared statement
        query = "SELECT * FROM Driver WHERE d_id = :id"
        dr_ = db.engine.execute(query, id=id)
        driver = dr_.first()
        return render_template('profile_driver.html', tasks=driver)
    else:
        return "something wrong"

@app.route('/Myappointment_d/<int:id>', methods=['GET','POST'])
def Appointment_driver(id):
    if request.method == 'GET':
        appointments = Appointment.query.filter_by(d_id=id).all()
        return render_template('MyAppointment_d.html', tasks=appointments, id = id)
    else:
        if(request.form['btn'] == 'Order_by_pick_up'):
            appointments = Appointment.query.filter_by(d_id=id).order_by(Appointment.planned_start_time).all()
        elif(request.form['btn'] == 'Order_by_drop_off'):
            appointments = Appointment.query.filter_by(d_id=id).order_by(Appointment.planned_destination).all()
        elif(request.form['btn'] == 'Order_by_payment'):
            appointments = Appointment.query.filter_by(d_id=id).order_by(Appointment.planned_payment_amount).all()
        elif(request.form['btn'] == 'Filter Payment Amount'):
            appointments = Appointment.query.filter_by(d_id=id).filter(Appointment.planned_payment_amount >= request.form['Lowest Payment']).filter(Appointment.planned_payment_amount <= request.form['Highest Payment']).all()
        return render_template('MyAppointment_d.html', tasks=appointments, id=id)
        

@app.route('/order_waiting_ongoing/<int:o_id>/<int:u_id>', methods=['POST', 'GET','PUT'])
def order_w_o(o_id, u_id):
    order = Order.query.get_or_404(o_id)
    if (request.method == 'GET'):
        if order.d_id == -1:
            return render_template('order_waiting.html', o_id=o_id, u_id=u_id)
        else:
            driver_id = order.d_id
            driver = Driver.query.get_or_404(driver_id)
            return render_template('order_ongoing.html', o_id=o_id, u_id=u_id, driver=driver, order=order)
    else:
        if(request.form['btn1']):
            if(request.form['btn1'] == 'Change Information'):
                order = Order.query.get_or_404(o_id)
                if(request.form['pick_up'] != ''):
                    order.pick_up = request.form['pick_up']
                if(request.form['drop_off'] != ''):
                    order.drop_off = request.form['drop_off']
                db.session.commit()
                return render_template('order_waiting.html', o_id=o_id, u_id=u_id) 
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
            return render_template('order_ongoing_driver.html', task=order)
        else:
            flash("order complete!")
            return redirect(url_for('homepage_d', id=u_id))


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
