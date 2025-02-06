<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "guvi";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$response = array();

// Connect to Redis
try {
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
} catch (Exception $e) {
    $response['success'] = false;
    $response['message'] = "Could not connect to Redis: " . $e->getMessage();
    echo json_encode($response);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Sanitize input
    $email = trim($_POST['email']);
    $password = $_POST['password'];

    // Check if email exists
    $stmt = $conn->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        
        // Verify the password
        if (password_verify($password, $user['password'])) {
            // Generate session ID and store session in Redis
            $sessionId = bin2hex(random_bytes(32));
            
            // Store user data in Redis for 1 hour
            $redis->set($sessionId, json_encode($user), 3600);  // 3600 seconds = 1 hour

            // Successful login response
            $response['success'] = true;
            $response['sessionId'] = $sessionId;
            $response['user'] = array(
                'id' => $user['id'],
                'username' => $user['username'],
                'email' => $user['email']
            );
        } else {
            // Incorrect password
            $response['success'] = false;
            $response['message'] = "Incorrect password.";
        }
    } else {
        // Email not registered
        $response['success'] = false;
        $response['message'] = "Email not registered.";
    }

    $stmt->close();
} else {
    // Invalid request method
    $response['success'] = false;
    $response['message'] = "Invalid request method. Use POST.";
}

$conn->close();
echo json_encode($response);
?>
