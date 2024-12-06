

function updateDateTime() {
    const dateTime = new Date().toLocaleString();
    document.getElementById("dateTime").textContent = dateTime;
}
setInterval(updateDateTime, 1000);

function initializeQuizToggle() {
  const quizToggle = document.getElementById('quizToggle');
  const quizCourses = document.getElementById('quizCourses');
  
  quizToggle.addEventListener('click', () => {
    const isVisible = quizCourses.classList.contains('visible');
    
    if (isVisible) {
      quizCourses.classList.remove('visible');
      quizCourses.classList.add('hidden');
      quizToggle.textContent = '+';
    } else {
      quizCourses.classList.remove('hidden');
      quizCourses.classList.add('visible');
      quizToggle.textContent = '−';
    }
  });
}

function initializeAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, {
    threshold: 0.1
  });
  
  document.querySelectorAll('.animate-on-scroll').forEach((element) => {
    observer.observe(element);
  });
}