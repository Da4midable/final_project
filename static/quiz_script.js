const questions = [
    {
        question: "What is the output of 2 + 2 in Python?",
        options: ["2", "4", "22", "None of the above"],
        correctAnswer: "4"
    },
    {
        question: "Which of the following is a valid Python function?",
        options: ["def function[]", "function()", "def function()", "function():"],
        correctAnswer: "def function()"
    },
    {
        question: "Which data type is immutable?",
        options: ["List", "Dictionary", "Set", "Tuple"],
        correctAnswer: "Tuple"
    }
];

let currentQuestionIndex = 0;
let score = 0;
let timerInterval;
let timeLeft = 180; // 3 minutes in seconds

// Initialize the quiz
function loadQuestion(index) {
    const questionElement = document.getElementById('quiz-question');
    const optionsElement = document.getElementById('options');

    // Set the question text
    questionElement.textContent = questions[index].question;

    // Clear previous options
    optionsElement.innerHTML = '';

    // Populate new options
    questions[index].options.forEach(option => {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = 'option';
        input.value = option;

        label.appendChild(input);
        label.appendChild(document.createTextNode(option));
        optionsElement.appendChild(label);
        optionsElement.appendChild(document.createElement('br'));
    });
}

// Timer logic
function startTimer() {
    timerInterval = setInterval(() => {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        document.getElementById('timer').textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            moveToNextQuestion();
        }
    }, 1000);
}

// Handle Next button click
function moveToNextQuestion() {
    const selectedOption = document.querySelector('input[name="option"]:checked');
    if (selectedOption) {
        const userAnswer = selectedOption.value;
        if (userAnswer === questions[currentQuestionIndex].correctAnswer) {
            score++;
        }
    }

    // Move to the next question
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        loadQuestion(currentQuestionIndex);
        resetTimer();
    } else {
        finishQuiz();
    }
}

// Finish the quiz and display the score
function finishQuiz() {
    clearInterval(timerInterval);
    document.getElementById('question-section').style.display = 'none';
    document.getElementById('score-section').style.display = 'block';
    document.getElementById('finalScore').textContent = `${score} / ${questions.length}`;
}

// Reset the timer for each question
function resetTimer() {
    clearInterval(timerInterval);
    timeLeft = 180; // Reset to 3 minutes
    startTimer();
}

// Start the quiz when the page loads
window.onload = () => {
    loadQuestion(currentQuestionIndex);
    startTimer();
};

// Event listener for "Next Question" button
document.getElementById('nextQuestion').addEventListener('click', moveToNextQuestion);
