from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from validate_image import is_valid_image, validate_image_upload
from which_score import get_latest_score_query, update_mainform, highest_scorer
import mysql.connector
import os
import bcrypt
import datetime
import time
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
    database=MYSQL_DATABASE,
    pool_name="mypool",
    pool_size=5,
    connection_timeout=3600
)
cursor = connection.cursor()


SCORE_INDICES = {
    'Programming Score': 10,
    'English Score': 11,
    'History Score': 12,
    'Economics Score': 13,
    'Biology Score': 14
}

def get_user():
    try:
        connection.ping(reconnect=True)
        username = request.form['username']
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")

def display_time():
        current_time = time.strftime("%H:%M:%S")
        time.sleep(1)
        return current_time
        


@app.route('/', strict_slashes=False)
def landing():
    return render_template('landing.html')


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
            flash("Passwords do not match", "register_error")
            return redirect(url_for('register'))

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            flash("Username already exists", "register_error")
            return redirect(url_for('register'))

        is_valid, result = validate_image_upload(image)
        if not is_valid:
            flash(result, "register_error")
            return redirect(url_for("register"))

        else:
            image_path = os.path.join('static/uploads', secure_filename(image.filename))
            image.save(image_path)

        hashed_password = hash_password(password).decode('utf-8')
        registration_date = get_today_date_string()
        user_id = gen_id()

        query = """
        INSERT INTO users (`full name`, username, password, phone, gender, image_path, `User ID`, `Created On`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (fullname, username, hashed_password, phone, gender, image_path, user_id, registration_date))
        connection.commit()

        flash("Registration successful!", "register_success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # username = request.form['username']
        password = request.form['password']

        user = get_user()

        if user and check_password(user[3], password):
            session['user'] = user
            return redirect(url_for('mainform'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/mainform', strict_slashes=False)
def mainform():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']


    user_full_name = user_data[1]
    user_profile_picture = user_data[6]
    created_on = user_data[7]
    all_time_score_base = user_data[15]
    total_questions = user_data[16]
    user_id = user_data[8]
    courses = ['programming', 'english', 'history', 'economics', 'biology']
    query = get_latest_score_query()
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()
    result = results[0] if results else None 
    current_time = display_time()

    recent_score = None
    if result:
        score_type = results[1]
        recent_score_base = user_data[SCORE_INDICES.get(score_type, 10)]
        recent_score = (
            "0%" if total_questions == 0 
            else f"{(recent_score_base / 10) * 100:.2f}%"
        )
        
    all_time_score = (
            "0%" if all_time_score_base == 0
            else f"{(all_time_score_base / total_questions) * 100:.2f}%"
    )
    
    top_users = {}
    top_scores = {}

    for course in courses:
        cap_course = course.capitalize()
        total_course_score = f"Total_{cap_course}_Score"
        second_query = highest_scorer(total_course_score)
        cursor.execute(second_query)
        top_result = cursor.fetchall()
        if top_result:
            top_user, top_score = top_result[0]
            top_users[f"top_user_{course}"] = top_user if top_user and top_score > 0 else "N/A"
            top_scores[f"top_score_{course}"] = top_score if top_score else "N/A"
            


    return render_template(
        'mainform.html', 
        user_full_name=user_full_name, 
        user_profile_picture=user_profile_picture, 
        created_on=created_on, 
        all_time_score=all_time_score, 
        recent_score=recent_score,
        top_users=top_users,
        top_scores=top_scores,
        current_time=current_time
    )


@app.route('/mainform/<course>', methods=['GET', 'POST'])
def quiz(course):
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_index = session.get('current_question_index', 0)

        if user_answer not in session['options'][current_index]:
            flash("Invalid answer selected. Please choose one of the options.", "error")
            return redirect(url_for('quiz', course=course))

        correct_answer = session['answers'][current_index]
        if user_answer == correct_answer:
            session['score'] += 1

        session['current_question_index'] += 1
        current_index = session['current_question_index']

        if current_index >= len(session['questions']):
            total_questions = session.get('total_questions', 10)
            if len(session['questions']) < total_questions:
                try:
                    new_questions, new_options, new_answers = generate_additional_questions(course, 10)
                    session['questions'].extend(new_questions)
                    session['options'].extend(new_options)
                    session['answers'].extend(new_answers)
                except Exception as e:
                    flash(f"Error generating new questions: {str(e)}", "error")
                    return redirect(url_for('mainform'))

        if current_index >= session['total_questions']:
            return redirect(url_for('quiz_result', course=course))

        return render_template('quiz.html',
                               question=session['questions'][current_index],
                               options=session['options'][current_index],
                               course=course,
                               current_index=current_index,
                               total_questions=session['total_questions'])

    else:
        try:
            session['questions'], session['options'], session['answers'] = generate_initial_quiz(course, 10)
            session['current_question_index'] = 0
            session['total_questions'] = 10
            session['score'] = 0
            return render_template('quiz.html',
                                   question=session['questions'][0],
                                   options=session['options'][0],
                                   course=course,
                                   current_index=0,
                                   total_questions=10)
        except Exception as e:
            flash(f"Error generating quiz: {str(e)}", "error")
            return redirect(url_for('mainform'))


@app.route('/mainform/<course>/result', methods=['GET'])
def quiz_result(course):
    score = session.get('score', 0)
    total_questions = session.get('total_questions', 0)
    user = session['user']
    id = user[8]
    current_time_stamp = datetime.datetime.now()

    if not course.isalpha():
        raise ValueError("Invalid course name")
    course_score_column = f"{course.capitalize()} Score"
    first_index = course_score_column.split()[0]
    time_of_course_score = f"{first_index}_Score_Time"
    total_course_score = f"Total_{first_index}_Score"

    query = update_mainform(course_score_column, total_course_score, time_of_course_score)
    cursor.execute(query, (score, score, score, total_questions, current_time_stamp, current_time_stamp, id))
    connection.commit()
    
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

def generate_initial_quiz(course, num_questions=10):
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

def generate_additional_questions(course, num_questions=10):
    """Generate an additional set of questions for the quiz."""
    prompt = f"Generate {num_questions} advanced {course} questions in this format:\n" \
             "question = ['Q1', 'Q2', ...]\n" \
             "options = [['Q1O1', 'Q1O2', 'Q1O3', 'Q1O4'], ['Q2O1', 'Q2O2', 'Q2O3', 'Q2O4'], ...]\n" \
             "answer = ['Q1A', 'Q2A', ...]\n" \
             "Options should have four unique options, and the answer must be in the options."
    
    completion = client.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
        presence_penalty=0.6
    )
    
    response = completion.choices[0].message.content
    return parse_questions(response)


def parse_questions(response):
    """Parse the response from the OpenAI API into questions, options, and answers"""
    exec(response)
    return locals()['question'], locals()['options'], locals()['answer']

if __name__ == '__main__':
    app.run(debug=True)
