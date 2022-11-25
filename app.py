from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

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


class Appointment(db.Model):
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    d_id = db.Column(db.Integer, db.ForeignKey('driver.d_id'))
    p_id = db.Column(db.Integer, db.ForeignKey('passenger.d_id'))
    planned_pickup = db.Column(db.String(200), default='')
    planned_destination = db.Column(db.String(200), default='')
    planned_start_time = db.Column(db.String(200), default='')
    planned_payment_amount = db.Column(db.String(200), default='')

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
        return render_template('homepage_passenger.html', tasks=passenger)
    elif request.method == 'POST':
        passenger = Passenger.query.get_or_404(id)
        passenger.name = request.form['name']
        passenger.phoneNumber = request.form['phoneNumber']
        passenger.address = request.form['address']
        passenger.card_info = request.form['card_info']
        try:
            db.session.commit()
            flash("updated")
            return render_template('homepage_passenger.html', tasks=passenger)
        except:
            return "something wrong"


@app.route('/homepage_d/<int:id>', methods=['POST', 'GET'])
def homepage_d(id):
    if request.method == 'GET':
        driver = Driver.query.get_or_404(id)
        return render_template('homepage_driver.html', tasks=driver)
    elif request.method == 'POST':
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
        else:
            login_isDriver = False
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


@app.route('/<int:id>/appointment', methods=['POST', 'GET'])
def appointment(id):
    if request.method == 'POST':
        appointment_pickup = request.form['pickup']
        appointment_dest = request.form['destination']
        appointment_order_time = str(datetime.now())
        appointment_pltime = request.form['pltime']
        appointment_ppay = request.form['plpay']
        order = request.form['btn']
        appoint = request.form['btn']
        if order == "Order Now!":
            new_appointment = Appointment(planned_pickup=appointment_pickup, planned_destination=appointment_dest,
                                          planned_start_time=appointment_order_time,
                                          planned_payment_amount=appointment_ppay, p_id=id)
        elif appoint == "Make an Appointment now!":
            new_appointment = Appointment(planned_pickup=appointment_pickup, planned_destination=appointment_dest,
                                          planned_start_time=appointment_pltime,
                                          planned_payment_amount=appointment_ppay, p_id=id)
        try:
            db.session.add(new_appointment)
            db.session.commit()
            flash("updated")
            return render_template('appointment.html', tasks=new_appointment)
        except:
            return render_template('appointment.html', tasks=new_appointment)
    else:
        appointment = Appointment.query.get_or_404(id)
        return render_template('appointment.html', tasks=appointment)


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
