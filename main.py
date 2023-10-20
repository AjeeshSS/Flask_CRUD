from flask import Flask, render_template, request, url_for, redirect, send_from_directory, session

import psycopg2
from werkzeug.utils import secure_filename
import os

from flask_session import Session

con = psycopg2.connect(user="postgres", password='password', host='localhost', port='5432', database='newdb')
con.autocommit = True
cur = con.cursor()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# pip install Flask-Session


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        username = request.form['username']
        age = int(request.form['age'])
        password = request.form['password']
        # register to db.
        # c.execute("insert into table name values .......")
        return redirect(url_for('login'))


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        if session.get("username"):
            return redirect("/")
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        # c.execute("select * from table_name where username = %s and password=%s",(username, password))
        user = c.fetchone()
        if user:
            session["username"] = username
            return redirect(url_for('index'))
        else:
            return "username and pass are incorrect!!"


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/login")


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        cur.execute("SELECT * FROM student")
        student = cur.fetchall()
        return render_template('index.html', student=student)
    else:
        name = request.form['search_item']
        cur.execute("select * from student where name=%s", (name,))
        student = cur.fetchall()
        return render_template('index.html', student=student)


# app.config['UPLOAD_FOLDER'] = 'media'


@app.route('/add', methods=["POST", "GET"])
def add():
    if request.method == 'POST':
        roll = int(request.form['roll'])
        name = request.form['name']
        age = int(request.form['age'])
        mark = int(request.form['mark'])

        # Check if the 'profile_image' file was included in the request
        if 'profile_image' in request.files:
            image = request.files['profile_image']
            image_name = secure_filename(image.filename)
            img_path = os.path.join('media', image_name)
            image.save(img_path)
            cur.execute("INSERT INTO student (roll, name, age, mark, image) VALUES (%s, %s, %s, %s, %s)",
                        (roll, name, age, mark, image_name))
            return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'GET':
        roll = int(user_id)
        cur.execute("select * from student where roll=%s", (roll,))
        student = cur.fetchall()
        return render_template('edit_user.html', student=student)
    else:
        name = request.form['name']
        age = int(request.form['age'])
        mark = int(request.form['mark'])
        roll = int(request.form['roll'])

        cur.execute("UPDATE student SET name=%s, age=%s, mark=%s WHERE roll=%s", (name, age, mark, roll))

        return redirect(url_for('index'))


@app.route('/delete/<int:user_id>')
def delete(user_id):
    roll = int(user_id)
    cur.execute("SELECT image FROM student WHERE roll=%s", (roll,))
    result = cur.fetchone()
    if result:
        profile_image_filename = result[0]
        if profile_image_filename:
            media_dir_path = 'media'
            image_path = os.path.join(media_dir_path, profile_image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
    cur.execute("delete from student where roll=%s", (roll,))
    return redirect(url_for('index'))


@app.route('/<image_name>')
def images(image_name):
    return send_from_directory('media', image_name)


app.run(debug=True)
