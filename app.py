from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pw = db.Column(db.String(200), nullable=False)
    isDriver = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Login %r>' % self.id

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        login_id = request.form['id']
        login_pw = request.form['password']
        login_isDriver = request.form['isDriver']
        if login_isDriver == "on":
            login_isDriver = True

        new_login = User(id=login_id, pw=login_pw, isDriver=login_isDriver)

        try:
            db.session.add(new_login)
            db.session.commit()
            return redirect('/')
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
        return redirect('/')
    except:
        return 'There was a problem deleting that registration'

@app.route("/")
def hello_world():
    return render_template('index.html')





if __name__=="__main__":
    app.run(debug=True)