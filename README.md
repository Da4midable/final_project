# Formidable Quiz

Formidable Quiz is a web application designed to challenge users with quizzes on various topics, including programming, history, economics, biology, and English. The app dynamically generates questions using OpenAI's API, offering users an interactive and educational experience.

## Features

- **Dynamic Quiz Generation**: Questions are dynamically generated for each topic using OpenAI's API, ensuring a fresh experience each time
- **User Authentication**: Users can register and log in to track their progress and scores
- **Multi-Topic Support**: Quizzes are available in multiple categories, including Programming, History, Economics, Biology, and English
- **Timed Quizzes**: Each question in the quiz is timed to ensure a competitive and engaging environment
- **Leaderboards**: A leaderboard feature shows users' rankings based on their performance across topics
- **Responsive UI**: A user-friendly interface built using HTML, CSS, and JavaScript
- **Secure Login**: User passwords are hashed and stored securely in a MySQL database

## Technologies Used

### Programming Languages
- Python
- JavaScript
- HTML
- CSS
- Bash

### Frameworks and Tools
- Flask: Web application development
- Gunicorn: WSGI server for production
- MySQL: Structured data storage and user authentication
- OpenAI API: Dynamic question generation

### Deployment and Architecture
- HAProxy: Load balancing and SSL termination
- Nginx: Web server
- Google Cloud Platform (GCP): Hosting and infrastructure management

### Third-party Services
- OpenAI API: For generating quiz questions dynamically

## Installation

### Prerequisites
- Python 3.x installed on your machine
- MySQL server for database management
- OpenAI API key

### Steps

***1. Clone the repository***:
```bash
git clone https://github.com/your-username/formidable-quiz.git
cd formidable-quiz
```


***2. Set up a virtual environment***:
```bash
python3 -m venv venv
source venv/bin/activate
```

***3. Install the required packages***:
```bash
pip install -r requirements.txt
```

***4. Set up environment variables: Create a .env file in the project root with the following variables***:
```bash
MYSQL_FP_USER=<your-mysql-username>
MYSQL_FP_PASSWORD=<your-mysql-password>
MYSQL_FP_HOST=<your-mysql-host>
MYSQL_TEST_DATABASE=<your-database-name>
OAI_API_KEY=<your-openai-api-key>
FLASK_SECRET_KEY=<your-secret-key>
```
***5. Configure the database: Run the SQL schema to create the necessary tables***:

```bash
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    image_path VARCHAR(250) NOT NULL,
    `Created On` VARCHAR(50) NOT NULL,
    `User ID` VARCHAR(100) UNIQUE,
    `Last Played On` DATETIME,
    `Programming Score` INT DEFAULT 0,
    `English Score` INT DEFAULT 0,
    `History Score` INT DEFAULT 0,
    `Economics Score` INT DEFAULT 0,
    `Biology Score` INT DEFAULT 0,
    `Total_Score` INT DEFAULT 0
);
```

***6. Run the app***:
```
flask run
```

***7. Access the application: Open your browser and navigate to http://127.0.0.1:5000 to view the quiz app***.


### Usage

**Register/Login**: Users must register and log in to access quizzes
**Select Quiz Topic**: Choose from a variety of topics
**Answer Questions**: Each quiz contains dynamically generated questions
**View Scores**: After completing a quiz, view your score and compare it on the leaderboard

### Future Improvements

- Add more categories and levels of difficulty
- Implement multiplayer quiz modes
- Introduce user-customizable quizzes
- Add more detailed analytics for user performance

### Contribution
Contributions are welcome! Please fork this repository, create a feature branch, and submit a pull request.
