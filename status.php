<?php
require 'db.php';

header('Content-Type: application/json');

if (isset($_GET['url_code'])) {
    $url_code = $conn->real_escape_string($_GET['url_code']);
    $sql = "SELECT download FROM downloads WHERE url_code = '$url_code' LIMIT 1";
    $result = $conn->query($sql);

    if ($row = $result->fetch_assoc()) {
        echo json_encode(['download' => (int)$row['download']]);
    } else {
        echo json_encode(['download' => 0]);
    }
    exit;
}
echo json_encode(['error' => 'Missing url_code']);
?>