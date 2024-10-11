from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import mysql.connector
import os
import bcrypt
from uuid import uuid4
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

load_dotenv()

def gen_id():
    return str(uuid4())

def hash_password(password):
    """
    Hash a password for storing.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, user_input_password):
    return bcrypt.checkpw(user_input_password.encode('utf-8'), hashed_password.encode('utf-8'))


MYSQL_USER = os.getenv('MYSQL_FP_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_FP_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_FP_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_TEST_DATABASE')

connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
cursor = connection.cursor()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password(user[3], password):
            session['user'] = user
            return redirect(url_for('mainform'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['full name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        gender = request.form['gender']
        image = request.files['image']

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for('register'))

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            flash("Username already exists")
            return redirect(url_for('register'))

        hashed_password = hash_password(password).decode('utf-8')

        image_path = os.path.join('uploads', secure_filename(image.filename))
        image.save(image_path)
        
        user_id = gen_id()

        query = "INSERT INTO users (`full name`, username, password, phone, gender, image_path, `User ID`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (fullname, username, hashed_password, phone, gender, image_path, user_id))
        connection.commit()

        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/mainform')
def mainform():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']
    user_full_name = user_data[1]
    user_profile_picture = user_data[5]

    return render_template('mainform.html', 
                           user_full_name=user_full_name, 
                           user_profile_picture=user_profile_picture)


@app.route('/quiz/programming')
def programming_quiz():
    return render_template('quiz.html')


if __name__ == '__main__':
    app.run(debug=True)
