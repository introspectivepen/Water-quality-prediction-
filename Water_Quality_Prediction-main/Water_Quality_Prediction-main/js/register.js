// register.js
$(document).ready(function() {
    $('#registerForm').on('submit', function(event) {
        event.preventDefault();
        var username = $('#username').val();
        var email = $('#email').val();
        var password = $('#password').val();
        var confirmPassword = $('#confirm-password').val();

        if (password !== confirmPassword) {
            alert('Passwords do not match.');
            return;
        }

        $.ajax({
            url: 'http://localhost/Guvi_intern/php/register.php',
            type: 'POST',
            data: {
                username: username,
                email: email,
                password: password
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    alert('Registration successful. You can now log in.');
                    window.location.href = 'login.html';
                } else {
                    alert('Registration failed: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
                alert('An error occurred during the registration process. Please try again.');
            }
        });
    });
});
