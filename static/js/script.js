document.getElementById('darkModeToggle').addEventListener('click', function () {
    // Toggle dark mode on body
    document.body.classList.toggle('dark-mode');

    // Change logos based on dark mode
    const navbarLogo = document.getElementById('navbarLogo');
    const formLogo = document.querySelector('.logo');  // Target the logo above the form
    const button = document.getElementById('darkModeToggle');  // Target the dark mode button
    
    // If dark mode is enabled
    if (document.body.classList.contains('dark-mode')) {
        navbarLogo.src = "{{ url_for('static', filename='images/logowhite.jpeg') }}";  // Dark mode navbar logo
        formLogo.src = "{{ url_for('static', filename='images/logowhite.jpeg') }}";  // Dark mode logo above the form
        button.textContent = "🌕 Light Mode";  // Change button text to Light Mode
        localStorage.setItem('darkMode', 'enabled');
    } else {
        navbarLogo.src = "{{ url_for('static', filename='images/logo.jpeg') }}";  // Light mode navbar logo
        formLogo.src = "{{ url_for('static', filename='images/logo.jpeg') }}";  // Light mode logo above the form
        button.textContent = "🌓 Dark Mode";  // Change button text to Dark Mode
        localStorage.setItem('darkMode', 'disabled');
    }
});


window.addEventListener('load', function () {
    const navbarLogo = document.getElementById('navbarLogo');
    const formLogo = document.querySelector('.logo');
    const button = document.getElementById('darkModeToggle');
    
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        navbarLogo.src = "{{ url_for('static', filename='images/logowhite.jpeg') }}";  
        formLogo.src = "{{ url_for('static', filename='images/logowhite.jpeg') }}";  
        button.textContent = "🌕 Light Mode";  
    }
});

window.addEventListener('load', function() {
  document.body.classList.add('loaded');
});