$(document).ready(function() {
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();
        
        var email = $('#email').val();
        var password = $('#password').val();

        $.ajax({
            url: 'http://localhost/Guvi_intern/php/login.php',
            type: 'POST',
            data: { email: email, password: password },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    localStorage.setItem('sessionId', response.sessionId);
                    localStorage.setItem('user', JSON.stringify(response.user));

                    // Redirect to the prediction page served by FastAPI
                    window.location.href = 'http://localhost:8000/';
                } else {
                    alert('Login failed: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);
                alert('An error occurred during the login process.');
            }
        });
    });
});
