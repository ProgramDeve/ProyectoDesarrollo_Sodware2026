<?php
// buscar.php — Versión robusta que siempre devuelve JSON
error_reporting(E_ALL);
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');

function jsonError($msg, $detalle = null, $http = 200) {
    http_response_code($http);
    echo json_encode(['error' => $msg, 'detalle' => $detalle], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonError('Método no permitido. Usa POST.', null, 405);
}

$termino = isset($_POST['termino']) ? trim($_POST['termino']) : '';
if ($termino === '') {
    jsonError('El término de búsqueda no puede estar vacío.');
}

// ⚠️ ASEGÚRATE DE QUE ESTAS RUTAS SEAN LAS CORRECTAS EN TU PC
$pythonPath = 'C:\Users\JOTA\Downloads\visionprice\.venv\Scripts\python.exe';
$scriptPath = 'C:\Users\JOTA\Downloads\visionprice\test_scraper_manual.py';

if (!file_exists($pythonPath)) {
    jsonError('No se encuentra el Python del venv.', 'Ruta: ' . $pythonPath);
}
if (!file_exists($scriptPath)) {
    jsonError('No se encuentra el script de Python.', 'Ruta: ' . $scriptPath);
}
if (!function_exists('shell_exec')) {
    jsonError('shell_exec está deshabilitado en php.ini.', 'Quita "shell_exec" de disable_functions');
}

putenv('PYTHONIOENCODING=UTF-8');
putenv('PYTHONUTF8=1');

$cmd = escapeshellcmd($pythonPath) . ' ' . escapeshellcmd($scriptPath) . ' ' . escapeshellarg($termino) . ' 2>&1';
$output = shell_exec($cmd);

if ($output === null) {
    jsonError('shell_exec devolvió null.', 'Revisa permisos de Apache y disable_functions');
}

// =========================================================================
// AQUÍ ESTÁ LA MAGIA: Extraemos solo el JSON ignorando textos extra
// =========================================================================
$start = strpos($output, '{');
$end = strrpos($output, '}');

if ($start === false || $end === false || $start > $end) {
    jsonError('Python no devolvió un JSON con formato válido.', $output);
}

$jsonStr = substr($output, $start, $end - $start + 1);
$resultado = json_decode($jsonStr, true);

if ($resultado === null) {
    jsonError('Error al decodificar el JSON extraído.', $jsonStr);
}

// Devolvemos el JSON limpio al index.php
echo json_encode($resultado, JSON_UNESCAPED_UNICODE);