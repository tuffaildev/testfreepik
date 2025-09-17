<?php
require_once 'config.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // Get database instance
    $db = Database::getInstance();
    
    // Get statistics
    $totalResult = $db->query("SELECT COUNT(*) as total FROM downloads");
    $total = $totalResult->fetch_assoc()['total'];
    
    $completedResult = $db->query("SELECT COUNT(*) as completed FROM downloads WHERE download = 1");
    $completed = $completedResult->fetch_assoc()['completed'];
    
    $pendingResult = $db->query("SELECT COUNT(*) as pending FROM downloads WHERE download = 0");
    $pending = $pendingResult->fetch_assoc()['pending'];
    
    $processingResult = $db->query("SELECT COUNT(*) as processing FROM downloads WHERE status = 1 AND download = 0");
    $processing = $processingResult->fetch_assoc()['processing'];
    
    // Get recent downloads
    $recentResult = $db->query(
        "SELECT url, filename, status, download, created_at 
         FROM downloads 
         ORDER BY created_at DESC 
         LIMIT 10"
    );
    
    $recent = [];
    while ($row = $recentResult->fetch_assoc()) {
        $recent[] = [
            'filename' => $row['filename'],
            'status' => $row['status'] == 1 && $row['download'] == 1 ? 'completed' : 
                       ($row['status'] == 1 ? 'processing' : 'pending'),
            'created_at' => $row['created_at']
        ];
    }
    
    jsonResponse([
        'success' => true,
        'data' => [
            'total' => (int)$total,
            'completed' => (int)$completed,
            'pending' => (int)$pending,
            'processing' => (int)$processing,
            'recent' => $recent
        ]
    ]);
    
} catch (Exception $e) {
    logError('Stats API Error: ' . $e->getMessage());
    
    jsonResponse([
        'success' => false,
        'message' => 'An error occurred while fetching statistics'
    ], 500);
}
?>