// Legal Pages JavaScript - Theme Toggle Only

document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    setupThemeToggle();
});

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.className = savedTheme === 'light' ? 'light-mode' : '';
}

function setupThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isLightMode = document.body.classList.contains('light-mode');
            
            if (isLightMode) {
                document.body.classList.remove('light-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}