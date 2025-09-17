<?php
require_once 'config.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // Validate request method
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        jsonResponse([
            'success' => false,
            'message' => 'Only GET method is allowed'
        ], 405);
    }
    
    // Validate input
    if (empty($_GET['url_code'])) {
        jsonResponse([
            'success' => false,
            'message' => 'URL code is required'
        ], 400);
    }
    
    $urlCode = sanitizeInput($_GET['url_code']);
    
    // Validate URL code format (should be numeric)
    if (!ctype_digit($urlCode)) {
        jsonResponse([
            'success' => false,
            'message' => 'Invalid URL code format'
        ], 400);
    }
    
    // Get database instance
    $db = Database::getInstance();
    
    // Get download status
    $result = $db->query(
        "SELECT id, url, filename, status, download, created_at, updated_at FROM downloads WHERE url_code = ? LIMIT 1",
        [$urlCode]
    );
    
    if (!$result || $result->num_rows === 0) {
        jsonResponse([
            'success' => false,
            'message' => 'Download record not found'
        ], 404);
    }
    
    $download = $result->fetch_assoc();
    
    // Update last checked timestamp
    $db->update(
        'downloads',
        ['last_checked' => date('Y-m-d H:i:s')],
        'url_code = ?',
        [$urlCode]
    );
    
    // Determine status message
    $statusMessage = 'Unknown';
    if ($download['status'] == 0 && $download['download'] == 0) {
        $statusMessage = 'Queued for processing';
    } elseif ($download['status'] == 1 && $download['download'] == 0) {
        $statusMessage = 'Processing download';
    } elseif ($download['download'] == 1) {
        $statusMessage = 'Download completed';
    }
    
    jsonResponse([
        'success' => true,
        'message' => $statusMessage,
        'data' => [
            'id' => (int)$download['id'],
            'url' => $download['url'],
            'filename' => $download['filename'],
            'status' => (int)$download['status'],
            'download' => (int)$download['download'],
            'status_message' => $statusMessage,
            'created_at' => $download['created_at'],
            'updated_at' => $download['updated_at']
        ]
    ]);
    
} catch (Exception $e) {
    logError('Status API Error: ' . $e->getMessage(), [
        'url_code' => $_GET['url_code'] ?? 'N/A',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'N/A',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'N/A'
    ]);
    
    jsonResponse([
        'success' => false,
        'message' => 'An error occurred while checking status'
    ], 500);
}
?>