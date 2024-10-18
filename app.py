from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import mysql.connector
import os
import bcrypt
import datetime
from uuid import uuid4
from dotenv import load_dotenv
from openai import OpenAI


client = OpenAI(api_key=os.getenv('OAI_API_KEY'))

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

def get_today_date_string():
  today = datetime.date.today()
  day = today.strftime('%d')
  month = today.strftime('%B')
  year = today.strftime('%Y')
  return f"{day}–{month}–{year}"

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

@app.route('/', strict_slashes=False)
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

@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
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

        image_path = os.path.join('static/uploads', secure_filename(image.filename))
        image.save(image_path)
        
        registration_date = get_today_date_string()
        user_id = gen_id()

        query = "INSERT INTO users (`full name`, username, password, phone, gender, image_path, `User ID`, `Created On`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (fullname, username, hashed_password, phone, gender, image_path, user_id, registration_date))
        connection.commit()

        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/mainform', strict_slashes=False)
def mainform():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']
    user_full_name = user_data[1]
    user_profile_picture = user_data[6]
    created_on = user_data[7]

    return render_template('mainform.html', 
                           user_full_name=user_full_name, 
                           user_profile_picture=user_profile_picture, created_on=created_on)


@app.route('/mainform/<course>', methods=['GET', 'POST'])
def quiz(course):
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_index = session.get('current_question_index', 0)

        # If invalid answer, return an error
        if user_answer not in session['options'][current_index]:
            flash("Invalid answer selected. Please choose one of the options.", "error")
            return redirect(url_for('quiz', course=course))

        # Track if the answer is correct
        correct_answer = session['answers'][current_index]
        if user_answer == correct_answer:
            session['score'] += 1  # Increment the score for a correct answer

        # Move to the next question
        session['current_question_index'] += 1
        current_index = session['current_question_index']

        # Check if more questions need to be generated
        if current_index >= len(session['questions']):
            # Generate next batch of 5 questions if we haven't reached the total yet
            total_questions = session.get('total_questions', 20)
            if len(session['questions']) < total_questions:
                try:
                    new_questions, new_options, new_answers = generate_additional_questions(course, 5)
                    session['questions'].extend(new_questions)
                    session['options'].extend(new_options)
                    session['answers'].extend(new_answers)
                except Exception as e:
                    flash(f"Error generating new questions: {str(e)}", "error")
                    return redirect(url_for('mainform'))

        # If the quiz is complete
        if current_index >= session['total_questions']:
            return redirect(url_for('quiz_result', course=course))

        # Otherwise, move to the next question
        return render_template('quiz.html',
                               question=session['questions'][current_index],
                               options=session['options'][current_index],
                               course=course,
                               current_index=current_index,
                               total_questions=session['total_questions'])

    else:
        # Initialize quiz with the first 5 questions
        try:
            session['questions'], session['options'], session['answers'] = generate_initial_quiz(course, 5)
            session['current_question_index'] = 0
            session['total_questions'] = 20  # Set the total number of questions for the quiz
            session['score'] = 0  # Initialize score tracking
            return render_template('quiz.html',
                                   question=session['questions'][0],
                                   options=session['options'][0],
                                   course=course,
                                   current_index=0,
                                   total_questions=20)
        except Exception as e:
            flash(f"Error generating quiz: {str(e)}", "error")
            return redirect(url_for('mainform'))


@app.route('/mainform/<course>/result', methods=['GET'])
def quiz_result(course):
    score = session.get('score', 0)
    total_questions = session.get('total_questions', 0)
    clear_quiz_session()
    return render_template('quiz_result.html', score=score, total_questions=total_questions, course=course)

@app.route('/logout', methods=['GET'])
def logout():
    """logs out user"""
    session.clear()
    return redirect(url_for('login'))


def clear_quiz_session():
    """Clear the quiz session data"""
    session.pop('questions', None)
    session.pop('options', None)
    session.pop('answers', None)
    session.pop('current_question_index', None)
    session.pop('total_questions', None)

def generate_initial_quiz(course, num_questions=5):
    """Generate an initial set of questions for the quiz."""
    prompt = f"Generate {num_questions} advanced {course} questions in this format:\n" \
             "question = ['Q1', 'Q2', ...]\n" \
             "options = [['Q1O1', 'Q1O2', 'Q1O3', 'Q1O4'], ['Q2O1', 'Q2O2', 'Q2O3', 'Q2O4'], ...]\n" \
             "answer = ['Q1A', 'Q2A', ...]\n" \
             "Options should have four unique options, and the answer must be in the options."
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response = completion.choices[0].message.content
    return parse_questions(response)

def generate_additional_questions(course, num_questions=5):
    """Generate an additional set of questions for the quiz."""
    prompt = f"Generate {num_questions} advanced {course} questions in this format:\n" \
             "question = ['Q1', 'Q2', ...]\n" \
             "options = [['Q1O1', 'Q1O2', 'Q1O3', 'Q1O4'], ['Q2O1', 'Q2O2', 'Q2O3', 'Q2O4'], ...]\n" \
             "answer = ['Q1A', 'Q2A', ...]\n" \
             "Options should have four unique options, and the answer must be in the options."
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response = completion.choices[0].message.content
    return parse_questions(response)


def parse_questions(response):
    """Parse the response from the OpenAI API into questions, options, and answers."""
    exec(response)
    return locals()['question'], locals()['options'], locals()['answer']

if __name__ == '__main__':
    app.run(debug=True)
