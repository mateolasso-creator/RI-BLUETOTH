<?php
/**
 * API REST del servidor - P-C3 (Versión Bluetooth Token)
 */
header('Content-Type: application/json; charset=utf-8');
date_default_timezone_set('America/Lima');

$db = new mysqli('db', 'root', 'rootpassword', 'rfid_access');

$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

// --- 1. GET /check?token={TOKEN} ---
if ($method === 'GET' && strpos($request_uri, '/check') !== false) {
    $token = $_GET['token'] ?? '';
    
    $stmt = $db->prepare("SELECT name FROM users WHERE token = ? AND status = 'ACTIVE'");
    $stmt->bind_param('s', $token);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        echo json_encode([
            "autorizado" => true,
            "nombre" => $row['name']
        ]);
    } else {
        echo json_encode([
            "autorizado" => false,
            "nombre" => "Desconocido"
        ]);
    }
    exit;
}

// --- 2. POST /log ---
if ($method === 'POST' && strpos($request_uri, '/log') !== false) {
    $body = json_decode(file_get_contents('php://input'), true);
    
    // Body esperado: {"token","timestamp","resultado"}
    $token = $body['token'] ?? 'N/A';
    $resultado = $body['resultado'] ?? 'UNKNOWN';
    
    $stmt = $db->prepare("INSERT INTO logs (token, access_status) VALUES (?, ?)");
    $stmt->bind_param('ss', $token, $resultado);
    $stmt->execute();
    
    echo json_encode(["status" => "registrado"]);
    exit;
}

// --- 3. GET /usuarios y POST /usuarios ---
if (strpos($request_uri, '/usuarios') !== false) {
    if ($method === 'GET') {
        $res = $db->query("SELECT name, token FROM users");
        echo json_encode($res->fetch_all(MYSQLI_ASSOC));
    } elseif ($method === 'POST') {
        $body = json_decode(file_get_contents('php://input'), true);
        $stmt = $db->prepare("INSERT INTO users (token, name) VALUES (?, ?)");
        $stmt->bind_param('ss', $body['token'], $body['name']);
        $stmt->execute();
        echo json_encode(["status" => "usuario_creado"]);
    }
    exit;
}
?>