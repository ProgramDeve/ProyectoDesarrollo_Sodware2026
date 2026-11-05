<?php
// buscar.php — Versión para Docker (se comunica con el microservicio de Python vía HTTP)
error_reporting(E_ALL);
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');

function jsonError($msg, $detalle = null, $http = 200) {
    http_response_code($http);
    echo json_encode(['error' => $msg, 'detalle' => $detalle], JSON_UNESCAPED_UNICODE);
    exit;
}

// 1. Validar que sea una petición POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonError('Método no permitido. Usa POST.', null, 405);
}

$termino = isset($_POST['termino']) ? trim($_POST['termino']) : '';
if ($termino === '') {
    jsonError('El término de búsqueda no puede estar vacío.');
}

// 2. Validar que la extensión cURL esté disponible en PHP
if (!function_exists('curl_init')) {
    jsonError('La extensión cURL de PHP no está habilitada.');
}

// 3. Configurar la URL de la API de Python en Docker
// IMPORTANTE: 'python-api' es el nombre del servicio que definiremos en docker-compose.yml.
// Docker se encarga de traducir ese nombre a la IP interna del contenedor.
$pythonApiUrl = 'http://python-api:5000/buscar';

$payload = json_encode(['termino' => $termino]);

// 4. Hacer la petición HTTP al contenedor de Python
$ch = curl_init($pythonApiUrl);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30); // El scraping de 5 tiendas puede tardar unos segundos

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

// 5. Manejo de errores de red
if ($response === false) {
    jsonError('Error de conexión con el backend de Python.', $curlError);
}

if ($httpCode !== 200) {
    jsonError('El backend de Python devolvió un error HTTP.', "Código: $httpCode. Respuesta: $response");
}

// 6. Decodificar la respuesta JSON que viene de Python
$resultado = json_decode($response, true);

if ($resultado === null) {
    jsonError('El backend de Python no devolvió un JSON válido.', $response);
}

// 7. Devolver el JSON limpio al frontend (index.php)
echo json_encode($resultado, JSON_UNESCAPED_UNICODE);