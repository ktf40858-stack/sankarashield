<?php
/**
 * SankaraShield Security Headers
 * Add this file at the beginning of PHP pages for additional security
 */

// Prevent direct access
if (!defined('SANKARASHIELD_SECURE')) {
    header('HTTP/1.0 403 Forbidden');
    exit('Direct access not permitted');
}

// Security Headers
header('X-Frame-Options: SAMEORIGIN');
header('X-Content-Type-Options: nosniff');
header('X-XSS-Protection: 1; mode=block');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Permissions-Policy: geolocation=(), microphone=(), camera=()');

// Strict Transport Security
header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');

// Content Security Policy
$csp = "default-src 'self'; ";
$csp .= "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; ";
$csp .= "style-src 'self' 'unsafe-inline'; ";
$csp .= "img-src 'self' data: https:; ";
$csp .= "font-src 'self' data:; ";
$csp .= "connect-src 'self'; ";
$csp .= "frame-ancestors 'none';";
header('Content-Security-Policy: ' . $csp);

// Session Security
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');

// Disable PHP version exposure
header_remove('X-Powered-By');

// Anti-CSRF Token Generator
function generateCSRFToken() {
    if (!isset($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

// Validate CSRF Token
function validateCSRFToken($token) {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

// Input Sanitization
function sanitizeInput($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
    return $data;
}

// SQL Injection Prevention (use with prepared statements)
function escapeSQL($connection, $string) {
    return mysqli_real_escape_string($connection, $string);
}

// Rate Limiting
function checkRateLimit($identifier, $maxAttempts = 5, $timeWindow = 300) {
    $cacheFile = sys_get_temp_dir() . '/rate_limit_' . md5($identifier);

    if (file_exists($cacheFile)) {
        $data = json_decode(file_get_contents($cacheFile), true);

        if (time() - $data['first_attempt'] > $timeWindow) {
            // Reset if time window passed
            $data = ['attempts' => 1, 'first_attempt' => time()];
        } else {
            $data['attempts']++;

            if ($data['attempts'] > $maxAttempts) {
                header('HTTP/1.0 429 Too Many Requests');
                exit('Rate limit exceeded. Please try again later.');
            }
        }
    } else {
        $data = ['attempts' => 1, 'first_attempt' => time()];
    }

    file_put_contents($cacheFile, json_encode($data));
    return true;
}

// IP Whitelist/Blacklist Check
function checkIPAccess($ip) {
    // Add your IP whitelist/blacklist logic here
    $blacklist = [
        // '192.168.1.100',
        // Add malicious IPs here
    ];

    if (in_array($ip, $blacklist)) {
        header('HTTP/1.0 403 Forbidden');
        exit('Access denied');
    }

    return true;
}

// File Upload Security
function secureFileUpload($file, $allowedTypes = ['jpg', 'jpeg', 'png', 'gif', 'pdf']) {
    $uploadDir = 'uploads/';
    $fileName = basename($file['name']);
    $fileExtension = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

    // Check file extension
    if (!in_array($fileExtension, $allowedTypes)) {
        return ['success' => false, 'message' => 'Invalid file type'];
    }

    // Check MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);

    $allowedMimes = [
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'png' => 'image/png',
        'gif' => 'image/gif',
        'pdf' => 'application/pdf'
    ];

    if (!isset($allowedMimes[$fileExtension]) || $allowedMimes[$fileExtension] !== $mimeType) {
        return ['success' => false, 'message' => 'File type mismatch'];
    }

    // Check file size (max 10MB)
    if ($file['size'] > 10485760) {
        return ['success' => false, 'message' => 'File too large'];
    }

    // Generate unique filename
    $newFileName = uniqid() . '_' . preg_replace('/[^a-zA-Z0-9._-]/', '', $fileName);
    $targetPath = $uploadDir . $newFileName;

    // Move uploaded file
    if (move_uploaded_file($file['tmp_name'], $targetPath)) {
        return ['success' => true, 'filename' => $newFileName];
    }

    return ['success' => false, 'message' => 'Upload failed'];
}

// Encryption/Decryption functions
function encryptData($data, $key) {
    $cipher = "AES-256-CBC";
    $ivlen = openssl_cipher_iv_length($cipher);
    $iv = openssl_random_pseudo_bytes($ivlen);
    $ciphertext = openssl_encrypt($data, $cipher, $key, 0, $iv);
    return base64_encode($ciphertext . '::' . $iv);
}

function decryptData($data, $key) {
    $cipher = "AES-256-CBC";
    list($encrypted_data, $iv) = explode('::', base64_decode($data), 2);
    return openssl_decrypt($encrypted_data, $cipher, $key, 0, $iv);
}

// Log security events
function logSecurityEvent($event, $details = '') {
    $logFile = 'logs/security.log';
    $timestamp = date('Y-m-d H:i:s');
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
    $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';

    $logEntry = "[{$timestamp}] IP: {$ip} | Event: {$event} | Details: {$details} | UA: {$userAgent}\n";

    file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX);
}

// Initialize security
checkIPAccess($_SERVER['REMOTE_ADDR'] ?? '');
?>