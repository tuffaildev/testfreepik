<?php
require_once 'config.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // Validate request method
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        jsonResponse([
            'success' => false,
            'message' => 'Only POST method is allowed'
        ], 405);
    }
    
    // Validate and sanitize input
    if (empty($_POST['url'])) {
        jsonResponse([
            'success' => false,
            'message' => 'URL is required'
        ], 400);
    }
    
    $url = sanitizeInput($_POST['url']);
    
    // Validate URL format and domain
    if (!validateUrl($url)) {
        jsonResponse([
            'success' => false,
            'message' => 'Invalid URL or domain not allowed'
        ], 400);
    }
    
    // Extract URL code
    $urlCode = extractUrlCode($url);
    if (!$urlCode) {
        jsonResponse([
            'success' => false,
            'message' => 'Could not extract URL code from the provided URL'
        ], 400);
    }
    
    // Extract filename
    $filename = extractFilename($url);
    
    // Get database instance
    $db = Database::getInstance();
    
    // Check if URL already exists
    $existingResult = $db->query(
        "SELECT id, status, download FROM downloads WHERE url_code = ? LIMIT 1",
        [$urlCode]
    );
    
    if ($existingResult && $existingResult->num_rows > 0) {
        $existing = $existingResult->fetch_assoc();
        
        if ($existing['download'] == 1) {
            jsonResponse([
                'success' => false,
                'message' => 'This image has already been downloaded'
            ], 409);
        } else {
            jsonResponse([
                'success' => true,
                'message' => 'URL already in queue',
                'url_code' => $urlCode,
                'url' => $url,
                'filename' => $filename,
                'existing' => true
            ]);
        }
    }
    
    // Insert new download record
    $insertData = [
        'url' => $url,
        'url_code' => $urlCode,
        'filename' => $filename,
        'status' => '0',
        'download' => '0',
        'created_at' => date('Y-m-d H:i:s'),
        'updated_at' => date('Y-m-d H:i:s')
    ];
    
    $insertId = $db->insert('downloads', $insertData);
    
    if ($insertId) {
        jsonResponse([
            'success' => true,
            'message' => 'URL added to download queue successfully',
            'url_code' => $urlCode,
            'url' => $url,
            'filename' => $filename,
            'id' => $insertId
        ]);
    } else {
        throw new Exception('Failed to insert download record');
    }
    
} catch (Exception $e) {
    logError('Submit API Error: ' . $e->getMessage(), [
        'url' => $_POST['url'] ?? 'N/A',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'N/A',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'N/A'
    ]);
    
    jsonResponse([
        'success' => false,
        'message' => 'An error occurred while processing your request'
    ], 500);
}
?>