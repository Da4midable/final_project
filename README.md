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

1. Clone the repository:
```bash
git clone https://github.com/your-username/formidable-quiz.git
cd formidable-quiz

Set up a virtual environment:

python3 -m venv venv
source venv/bin/activate

