from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    #completed = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<Login %r>' % self.id

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        login_id = request.form['id']
        login_psw = request.form['password']
        new_login = Todo(id=login_id, content=login_psw)

        try:
            db.session.add(new_login)
            db.session.commit()
            return redirect('/')
        except:
            return "Issue in adding"
    else:
        logins = Todo.query.order_by(Todo.id).all()
        return render_template('index.html', tasks=logins)

@app.route('/delete/<int:id>')
def delete(id):
    # get the value by id, if not found then 404
    delete_login = Todo.query.get_or_404(id)

    try:
        db.session.delete(delete_login)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that registration'

if __name__=="__main__":
    app.run(debug=True)