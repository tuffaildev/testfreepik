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
    
    // Validate URL code format
    if (!ctype_digit($urlCode)) {
        jsonResponse([
            'success' => false,
            'message' => 'Invalid URL code format'
        ], 400);
    }
    
    // Get database instance
    $db = Database::getInstance();
    
    // Get download record
    $result = $db->query(
        "SELECT id, filename, file_path, download FROM downloads WHERE url_code = ? AND download = 1 LIMIT 1",
        [$urlCode]
    );
    
    if (!$result || $result->num_rows === 0) {
        jsonResponse([
            'success' => false,
            'message' => 'Download not ready or not found'
        ], 404);
    }
    
    $download = $result->fetch_assoc();
    
    // Determine file path
    $filePath = null;
    if (!empty($download['file_path']) && file_exists($download['file_path'])) {
        $filePath = $download['file_path'];
    } else {
        // Try to find file in downloads directory
        $possibleExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
        foreach ($possibleExtensions as $ext) {
            $testPath = UPLOAD_DIR . $download['filename'] . '.' . $ext;
            if (file_exists($testPath)) {
                $filePath = $testPath;
                break;
            }
        }
    }
    
    if (!$filePath || !file_exists($filePath)) {
        jsonResponse([
            'success' => false,
            'message' => 'File not found on server'
        ], 404);
    }
    
    // Validate file size
    $fileSize = filesize($filePath);
    if ($fileSize === false || $fileSize > MAX_FILE_SIZE) {
        jsonResponse([
            'success' => false,
            'message' => 'File is too large or corrupted'
        ], 413);
    }
    
    // Get file info
    $fileInfo = pathinfo($filePath);
    $fileName = $download['filename'] . '.' . ($fileInfo['extension'] ?? 'jpg');
    $mimeType = mime_content_type($filePath) ?: 'application/octet-stream';
    
    // Update download count
    $db->update(
        'downloads',
        [
            'download_count' => 'download_count + 1',
            'last_downloaded' => date('Y-m-d H:i:s')
        ],
        'url_code = ?',
        [$urlCode]
    );
    
    // Set headers for file download
    header('Content-Type: ' . $mimeType);
    header('Content-Disposition: attachment; filename="' . $fileName . '"');
    header('Content-Length: ' . $fileSize);
    header('Cache-Control: no-cache, must-revalidate');
    header('Expires: 0');
    header('Pragma: public');
    
    // Clear any previous output
    if (ob_get_level()) {
        ob_end_clean();
    }
    
    // Output file
    $handle = fopen($filePath, 'rb');
    if ($handle === false) {
        jsonResponse([
            'success' => false,
            'message' => 'Could not open file for reading'
        ], 500);
    }
    
    while (!feof($handle)) {
        echo fread($handle, 8192);
        flush();
    }
    
    fclose($handle);
    exit;
    
} catch (Exception $e) {
    logError('Download API Error: ' . $e->getMessage(), [
        'url_code' => $_GET['url_code'] ?? 'N/A',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'N/A',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'N/A'
    ]);
    
    // Clear any output buffers
    if (ob_get_level()) {
        ob_end_clean();
    }
    
    jsonResponse([
        'success' => false,
        'message' => 'An error occurred while downloading the file'
    ], 500);
}
?>