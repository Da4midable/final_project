from quart import Quart, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os, bcrypt, datetime, asyncio, httpx
from uuid import uuid4
import mysql.connector, os, bcrypt, datetime, asyncio, httpx
from dotenv import load_dotenv



load_dotenv()

the_key = os.getenv('OAI_API_KEY')
app = Quart(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')



# Helper Functions
def gen_id():
    return str(uuid4())

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(hashed_password, user_input_password):
    return bcrypt.checkpw(user_input_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_today_date_string():
    today = datetime.date.today()
    return today.strftime('%d-%B-%Y')

# MySQL Setup
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

# Routes
@app.route('/', strict_slashes=False)
async def landing():
    return await render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        username = form['username']
        password = form['password']

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password(user[3], password):
            session['user'] = user
            return redirect(url_for('mainform'))
        else:
            await flash('Invalid username or password')
    
    return await render_template('login.html')

@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
async def register():
    if request.method == 'POST':
        form = await request.form
        fullname = form['full name']
        username = form['username']
        password = form['password']
        confirm_password = form['confirm_password']
        phone = form['phone']
        gender = form['gender']
        image = await request.files.get('image')

        if password != confirm_password:
            await flash("Passwords do not match")
            return redirect(url_for('register'))

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            await flash("Username already exists")
            return redirect(url_for('register'))

        hashed_password = hash_password(password)
        image_path = os.path.join('uploads', secure_filename(image.filename))
        await image.save(image_path)

        registration_date = get_today_date_string()
        user_id = gen_id()

        query = "INSERT INTO users (`full name`, username, password, phone, gender, image_path, `User ID`, `Created On`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (fullname, username, hashed_password, phone, gender, image_path, user_id, registration_date))
        connection.commit()

        await flash("Registration successful!")
        return redirect(url_for('login'))

    return await render_template('register.html')

@app.route('/mainform', strict_slashes=False)
async def mainform():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']
    user_full_name = user_data[1]
    user_profile_picture = user_data[6]
    created_on = user_data[7]

    return await render_template('mainform.html', 
                           user_full_name=user_full_name, 
                           user_profile_picture=user_profile_picture, 
                           created_on=created_on)

async def generate_questions_async(course, num_questions=5):
    """Asynchronously generate questions from OpenAI API"""
    prompt = f"Generate {num_questions} advanced {course} questions in JSON format:\n" \
             "[{'question': '', 'options': ['','','',''], 'answer': ''}]"
    
    headers = {
        "Authorization": f"Bearer {the_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api.openai.com/v1/chat/completions', 
                                     headers=headers,
                                     json={
                                         'model': 'gpt-3.5-turbo',
                                         'messages': [{'role': 'user', 'content': prompt}],
                                         'temperature': 0.7
                                     })
        data = response.json()
        return parse_questions(data['choices'][0]['message']['content'])

def parse_questions(response):
    """Parse JSON formatted response into questions, options, and answers"""
    import json
    try:
        questions_data = json.loads(response)
        questions = [q['question'] for q in questions_data]
        options = [q['options'] for q in questions_data]
        answers = [q['answer'] for q in questions_data]
        return questions, options, answers
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON response")

@app.route('/mainform/<course>', methods=['GET', 'POST'])
async def quiz(course):
    if request.method == 'POST':
        form = await request.form
        user_answer = form.get('answer')
        current_index = session.get('current_question_index', 0)

        if user_answer not in session['options'][current_index]:
            await flash("Invalid answer selected. Please choose one of the options.", "error")
            return redirect(url_for('quiz', course=course))

        session['answers'][current_index] = user_answer
        correct_answer = session['answers'][current_index]
        if user_answer == correct_answer:
            session['score'] += 1

        session['current_question_index'] += 1
        current_index = session['current_question_index']

        if current_index >= session['total_questions']:
            await flash(f"Quiz completed! Your score is {session['score']} out of {session['total_questions']}.", "success")
            clear_quiz_session()
            return redirect(url_for('mainform'))

        return await render_template('quiz.html', 
                                     question=session['questions'][current_index],
                                     options=session['options'][current_index],
                                     course=course)

    else:
        session['questions'], session['options'], session['answers'] = await generate_questions_async(course, 5)
        session['current_question_index'] = 0
        session['total_questions'] = 20
        session['score'] = 0
        return await render_template('quiz.html', 
                                     question=session['questions'][0],
                                     options=session['options'][0],
                                     course=course)

@app.route('/mainform/<course>/result', methods=['GET'])
async def quiz_result(course):
    score = session.get('score', 0)
    total_questions = session.get('total_questions', 0)
    clear_quiz_session()
    return await render_template('quiz_result.html', score=score, total_questions=total_questions, course=course)

def clear_quiz_session():
    """Clear the quiz session data"""
    session.pop('questions', None)
    session.pop('options', None)
    session.pop('answers', None)
    session.pop('current_question_index', None)
    session.pop('total_questions', None)

if __name__ == '__main__':
    app.run(debug=True)
