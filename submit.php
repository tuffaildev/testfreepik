<?php
require 'db.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['url'])) {
    $url = $conn->real_escape_string($_POST['url']);
    // Extract the URL code from the URL
    preg_match('/_(\d+)\.htm/', $url, $matches);
    if (isset($matches[1])) {
        $url_code = $matches[1];
    } else {
        echo json_encode(['error' => 'Invalid URL format.']);
        exit;
    }
    // Extract filename from URL
    preg_match('/\/([^\/?#]+\.htm)/', $url, $file_matches);
    $filename = isset($file_matches[1]) ? $conn->real_escape_string($file_matches[1]) : null;
//like filename i get grass-silhouette_521407.htm I need grass-silhouette remove _521407.htm
    if ($filename) {
        $filename = preg_replace('/_\d+\.htm$/', '', $filename); // Remove the _number.htm part
    }

    $status = '0';
    $download = 0;

    $sql = "INSERT INTO downloads (url, url_code, status, download, filename) VALUES ('$url', '$url_code', '$status', $download, '$filename')";
    if ($conn->query($sql) === TRUE) {
        echo json_encode(['url_code' => $url_code]);
    } else {
        echo json_encode(['error' => $conn->error]);
    }
    exit;
}
echo json_encode(['error' => 'Invalid request.']);
?>