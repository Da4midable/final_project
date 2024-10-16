document.getElementById("quizToggle").addEventListener("click", function() {
    const topics = document.getElementById("quizCourses");
    topics.style.display = topics.style.display === "block" ? "none" : "block";
});

function updateDateTime() {
    const dateTime = new Date().toLocaleString();
    document.getElementById("dateTime").textContent = dateTime;
}
setInterval(updateDateTime, 1000);

const accountCreationDate = new Date("2024-01-01T12:00:00");
function updateMemberSince() {
    const now = new Date();
    const diff = now - accountCreationDate;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    document.getElementById("memberSince").textContent = `${days} days, ${hours % 24} hours, ${minutes % 60} minutes, and ${seconds % 60} seconds ago`;
}
setInterval(updateMemberSince, 1000);
