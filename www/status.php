<?php
// Load DB credentials from environment variables
$host = getenv('MYSQL_HOST');
$user = getenv('MYSQL_USER');
$pass = getenv('MYSQL_PASSWORD');
$db   = getenv('MYSQL_DATABASE');

// Try to connect to the database
$conn = @mysqli_connect($host, $user, $pass, $db);

if ($conn) {
    http_response_code(200);
    header('Content-Type: text/plain');
    echo "OK";
    mysqli_close($conn);
} else {
    http_response_code(503);
    header('Content-Type: text/plain');
	echo "DB ERROR";
}