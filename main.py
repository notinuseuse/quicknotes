from flask import Flask, request, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
'''
    The password is stored as it is, but in a production environment 
    we will have to encrypt it with something like flask_bcrypt.

'''

app = Flask(__name__)

app.config['SECRET_KEY'] = 'djfioserjfnsdn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(400), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        usernames = [user.username for user in Users.query.all()]

        name = request.form.get('username')
        password = request.form.get('password')  
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            message = "Passwords didn't matched" 
            return render_template('signup.html', message=message)
        elif len(password) <= 6 or len(password)>= 10: 
            message = "the length of password should be from 6 to 10" 
            return render_template('signup.html', message=message)
        elif name in usernames:
            message = "your username should be unique" 
            return render_template('signup.html', message=message)
        else:
            obj = Users(username=name, password=password)
            db.session.add(obj)
            db.session.commit()
            return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        rows_to_delete = Users.query.filter_by(username=name, password=password).all()
        if rows_to_delete == []:
            return render_template('login.html', message="wrong credentials")
        else:
            print(rows_to_delete)
            element = rows_to_delete[0]
            print(element.username, element.password)
            session['username'] = element.username
            return redirect('/notes')
    return render_template('login.html')

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/notes')
def show_files():
    if 'username' in session:
        return render_template('notes.html')
    return redirect('/login')

@app.route('/show_notes')
def show_notes():
    if 'username' in session:
        name = session['username']
        notes_ = Notes.query.filter_by(username=name).all()
        for notes in notes_:
            print(notes.title, notes.content, notes.id)
        return render_template('show_notes.html', notes=notes_)
    return redirect('/login')

@app.route('/delete_note/<int:id>')
def delete_note(id):
    if 'username' in session:
        note = Notes.query.filter_by(id=id).first()
        if note:
            Notes.query.filter_by(id=id).delete()
            db.session.commit()
            name = session['username']
            notes_ = Notes.query.filter_by(username=name).all()
            return render_template('show_notes.html', message='done', notes=notes_)
        return render_template('show_notes.html', message='error')

@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            title = request.form.get('title')
            content = request.form.get('content')
            obj = Notes(username=username, title=title, content=content)
            db.session.add(obj)
            db.session.commit()
            return redirect('/show_notes')
        return render_template('add_note.html')
    return redirect('/login')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/home')

if __name__ == "__main__":
    app.run(debug=True, port=8000)