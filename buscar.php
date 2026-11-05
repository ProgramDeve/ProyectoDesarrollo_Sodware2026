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


// =========================================================================
// LÓGICA DE RUTAS DINÁMICAS
// =========================================================================
// Buscamos la carpeta del proyecto donde está el .venv. 
// Probamos varias rutas comunes para que funcione sin importar quién lo clone.
$rutasPosibles = [
    dirname(__DIR__, 3), // Si el proyecto está en C:\Users\gusta\ProyectoDesarrollo_Sodware2026\ProyectoDesarrollo_Sodware2026
    dirname(__DIR__, 2), // Si está un nivel más arriba
    dirname(__DIR__),    // Si está en la misma carpeta que XAMPP
    'C:\Users\gusta\ProyectoDesarrollo_Sodware2026\ProyectoDesarrollo_Sodware2026' // Ruta exacta por si acaso
];


$rutaProyectoReal = '';
foreach ($rutasPosibles as $ruta) {
    if (file_exists($ruta . '\.venv\Scripts\python.exe')) {
        $rutaProyectoReal = $ruta;
        break;
    }
}


if ($rutaProyectoReal === '') {
    jsonError('No se pudo encontrar la carpeta del proyecto. Asegúrate de haber creado el .venv con "py -3.11 -m venv .venv"');
}


$pythonPath = $rutaProyectoReal . '\.venv\Scripts\python.exe';
$scriptPath = $rutaProyectoReal . '\test_scraper_manual.py';


// =========================================================================
// VALIDACIONES Y EJECUCIÓN
// =========================================================================
if (!file_exists($pythonPath)) {
    jsonError('No se encuentra el ejecutable de Python en la ruta.', 'Ruta: ' . $pythonPath);
}
if (!file_exists($scriptPath)) {
    jsonError('No se encuentra el script test_scraper_manual.py.', 'Ruta: ' . $scriptPath);
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
// EXTRACCIÓN DEL JSON
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