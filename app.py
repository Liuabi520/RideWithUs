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
    d_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default='')
    phoneNumber = db.Column(db.String(200), default='')
    address = db.Column(db.String(200), default='')
    card_info = db.Column(db.String(200), default='')
    balance = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Login %r>' % self.d_id


@app.route('/', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if(request.form['btn'] == 'login'):
            login_id = request.form['id']
            login_pw = request.form['password']
            exists = db.session.query(db.exists().where(User.id == login_id)).scalar()
            if(not exists):
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

@app.route('/homepage_p/<int:id>',methods=['POST', 'GET'])
def homepage_p(id):
    if request.method=='GET':
        passenger = Passenger.query.get_or_404(id)
        return render_template('homepage_passenger.html',tasks=passenger)
    elif request.method=='POST':
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


@app.route('/homepage_d/<int:id>',methods=['POST', 'GET'])
def homepage_d(id):
    return str(id)

@app.route("/register", methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        login_id = int(request.form['id'])
        login_pw = request.form['password']
        login_isDriver = request.form['isDriver']
        if login_isDriver == "yes":
            login_isDriver = True
            # todo create a new instance of Driver
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

@app.route('/admin',methods=['POST', 'GET'])
def admin():
    if request.method=='POST':
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


if __name__=="__main__":
    app.run(debug=True)