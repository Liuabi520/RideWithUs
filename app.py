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
            try:
                if (user.pw == login_pw):
                    return redirect(url_for('/homepage', login_id))
                else:
                    flash('Error: password not match')
                    return redirect('/')

            except:
                return 'Homepage not implemented yet'
        elif (request.form['btn'] == 'admin'):
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/homepage/<int:id>')
def homepage(id):
    return -1

@app.route("/admin", methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        login_id = request.form['id']
        login_pw = request.form['password']
        login_isDriver = request.form['isDriver']
        print(request.form)
        if login_isDriver == "yes":
            login_isDriver = True
        else:
            login_isDriver = False
        print(login_isDriver)
        new_login = User(id=login_id, pw=login_pw, isDriver=login_isDriver)

        try:
            db.session.add(new_login)
            db.session.commit()
            return redirect('/admin')
        except:
            return "Issue in adding"
    else:
        logins = User.query.order_by(User.id).all()
        return render_template('index.html', tasks=logins)

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