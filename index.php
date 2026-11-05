<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionPrice — Comparador de Precios</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.5;
            padding: 2rem 1rem;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        
        /* Header */
        header { text-align: center; margin-bottom: 2.5rem; }
        h1 { color: #0f172a; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px; }
        h1 span { color: #2563eb; }
        .subtitle { color: #64748b; font-size: 1rem; margin-top: 0.5rem; }

        /* Tabs */
        .tabs {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .tab-btn {
            padding: 0.75rem 1.5rem;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            color: #64748b;
            transition: all 0.2s;
            font-family: inherit;
        }
        .tab-btn:hover { border-color: #cbd5e1; }
        .tab-btn.active {
            color: #2563eb;
            border-color: #2563eb;
            background: #eff6ff;
        }
        .tab-panel { display: none; animation: fadeIn 0.3s; }
        .tab-panel.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* Buscador */
        .search-box { display: flex; gap: 0.5rem; margin-bottom: 2rem; max-width: 700px; margin-left: auto; margin-right: auto; }
        .search-box input {
            flex: 1;
            padding: 1rem 1.2rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.2s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .search-box input:focus { outline: none; border-color: #2563eb; }
        .search-box button {
            padding: 0 2rem;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            font-family: inherit;
        }
        .search-box button:hover { background: #1d4ed8; }
        .search-box button:disabled { background: #94a3b8; cursor: wait; }

        /* Recomendación */
        #recommendationCard {
            display: none;
            background: linear-gradient(135deg, #eff6ff, #e0e7ff);
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            text-align: center;
        }
        .rec-title {
            color: #1e40af;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        .rec-body { color: #334155; font-size: 1rem; }
        .rec-price { font-size: 1.5rem; font-weight: 800; color: #1e40af; }
        .rec-savings { color: #16a34a; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem; display: inline-block; background: #dcfce7; padding: 0.2rem 0.6rem; border-radius: 99px; }

        /* Tabla */
        #results { display: none; }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .results-header h2 { font-size: 1.2rem; color: #0f172a; }
        .results-count { color: #64748b; font-size: 0.9rem; }
        
        .table-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th {
            background: #f8fafc;
            color: #475569;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        td { padding: 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.95rem; vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #f8fafc; }

        /* Tienda Tags */
        .tienda-tag {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .tag-coolbox { background: #fee2e2; color: #b91c1c; }
        .tag-plaza-vea { background: #dcfce7; color: #15803d; }
        .tag-ripley { background: #fce7f3; color: #be185d; }
        .tag-oechsle { background: #fef08a; color: #854d0e; }
        .tag-hiraoka { background: #e0e7ff; color: #3730a3; }

        /* Precio y Enlaces */
        .precio { font-weight: 700; color: #0f172a; font-size: 1.1rem; white-space: nowrap; }
        .precio-minimo { color: #16a34a; }
        .btn-link {
            display: inline-block;
            padding: 0.4rem 1rem;
            background: #f1f5f9;
            color: #2563eb;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-link:hover { background: #2563eb; color: white; }

        /* Estados */
        #loading { display: none; text-align: center; padding: 3rem; color: #64748b; font-weight: 500; }
        #error { display: none; background: #fef2f2; color: #b91c1c; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #fecaca; }
        
        /* Imagen / Cámara */
        .upload-zone {
            border: 3px dashed #cbd5e1; border-radius: 12px; padding: 3rem 1.5rem; text-align: center;
            background: white; transition: all 0.2s; cursor: pointer; margin-bottom: 1.5rem; max-width: 600px; margin-left: auto; margin-right: auto;
        }
        .upload-zone:hover, .upload-zone.dragover { border-color: #2563eb; background: #eff6ff; }
        .upload-zone .icon { font-size: 3rem; margin-bottom: 1rem; }
        .upload-zone .title { font-size: 1.1rem; color: #1e293b; font-weight: 600; margin-bottom: 0.3rem; }
        .upload-zone .hint { color: #94a3b8; font-size: 0.9rem; }
        
        .actions-row { display: flex; gap: 1rem; justify-content: center; margin-bottom: 2rem; }
        .btn-secondary {
            padding: 0.75rem 1.5rem; background: white; color: #2563eb; border: 2px solid #2563eb;
            border-radius: 8px; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: all 0.2s; font-family: inherit;
        }
        .btn-secondary:hover { background: #2563eb; color: white; }
        
        .preview-wrap { display: none; text-align: center; margin-bottom: 1.5rem; }
        .preview-wrap img { max-width: 100%; max-height: 300px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .btn-detect {
            display: none; padding: 1rem 2rem; background: #10b981; color: white; border: none; border-radius: 8px;
            font-size: 1.05rem; font-weight: 700; cursor: pointer; margin-top: 1rem; font-family: inherit; transition: background 0.2s;
        }
        .btn-detect:hover { background: #059669; }

        #cameraWrap { display: none; text-align: center; margin-bottom: 1.5rem; }
        #cameraPreview { width: 100%; max-width: 500px; border-radius: 12px; background: #000; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .camera-controls { margin-top: 1rem; display: flex; gap: 1rem; justify-content: center; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Vision<span>Price</span></h1>
        <p class="subtitle">Comparador inteligente de precios en Perú. Encuentra la mejor oferta al instante.</p>
    </header>

    <div class="tabs">
        <button class="tab-btn active" data-tab="tab-texto">Búsqueda por Texto</button>
        <button class="tab-btn" data-tab="tab-imagen">Escanear Imagen / Cámara</button>
    </div>

    <!-- PANEL: TEXTO -->
    <div id="tab-texto" class="tab-panel active">
        <form class="search-box" id="searchForm">
            <input type="text" id="termino" placeholder="Ej: Laptop Lenovo, iPhone 15, Audífonos Sony..." required autofocus>
            <button type="submit" id="btnBuscar">Comparar Precios</button>
        </form>
    </div>

    <!-- PANEL: IMAGEN -->
    <div id="tab-imagen" class="tab-panel">
        <div class="upload-zone" id="uploadZone">
            <div class="icon">📸</div>
            <div class="title">Arrastra una foto del producto aquí</div>
            <div class="hint">o haz clic para buscar en tus archivos (JPG, PNG)</div>
        </div>
        <input type="file" id="fileInput" accept="image/*" style="display:none">

        <div class="actions-row">
            <button class="btn-secondary" id="btnSeleccionar">Subir Imagen</button>
            <button class="btn-secondary" id="btnAbrirCamara">Usar Cámara Web</button>
        </div>

        <div class="preview-wrap" id="previewWrap">
            <img id="previewImg" alt="Vista previa">
            <div class="preview-caption" id="previewCaption" style="margin-top: 0.5rem; color: #64748b; font-size: 0.9rem;"></div>
            <button class="btn-detect" id="btnDetectar">Detectar Producto (YOLO)</button>
        </div>

        <div id="cameraWrap">
            <video id="cameraPreview" autoplay playsinline></video>
            <div class="camera-controls">
                <button class="btn-secondary" id="btnCapturar">Capturar Foto</button>
                <button class="btn-secondary" id="btnCerrarCamara">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- ESTADOS -->
    <div id="loading">⏳ Analizando ofertas en 6 tiendas. Por favor espera...</div>
    <div id="error"></div>

    <!-- RESULTADOS Y RECOMENDACIÓN -->
    <div id="recommendationCard"></div>

    <div id="results">
        <div class="results-header">
            <h2>Ofertas encontradas para: <span id="terminoMostrado" style="color:#2563eb;"></span></h2>
            <span class="results-count"><strong id="totalResultados">0</strong> resultados</span>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Tienda</th>
                        <th>Producto</th>
                        <th>Precio</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody id="tablaResultados"></tbody>
            </table>
        </div>
    </div>
</div>

<script>
// ============================================================
// TABS Y UI
// ============================================================
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
        if (btn.dataset.tab !== 'tab-imagen') { cerrarCamara(); }
    });
});

const searchForm = document.getElementById('searchForm');
const btnBuscar = document.getElementById('btnBuscar');
const loading = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const resultsDiv = document.getElementById('results');
const recCard = document.getElementById('recommendationCard');

// ============================================================
// LÓGICA DE BÚSQUEDA
// ============================================================
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const termino = document.getElementById('termino').value.trim();
    if (!termino) return;

    loading.style.display = 'block';
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
    recCard.style.display = 'none';
    btnBuscar.disabled = true;

    try {
        const formData = new FormData();
        formData.append('termino', termino);

        const response = await fetch('buscar.php', { method: 'POST', body: formData });
        const textResponse = await response.text();
        
        let data;
        try {
            data = JSON.parse(textResponse);
        } catch (err) {
            throw new Error("Error en el servidor:\n" + textResponse.substring(0, 300));
        }

        if (data.error) { throw new Error(data.error + (data.detalle ? ':\n' + data.detalle : '')); }

        if (!data.exito || data.total === 0) {
            errorDiv.textContent = 'No se encontraron ofertas para "' + termino + '". Intenta con otro término.';
            errorDiv.style.display = 'block';
            return;
        }

        renderResultadosYRecomendacion(data, termino);
    } catch (err) {
        errorDiv.textContent = '❌ ' + err.message;
        errorDiv.style.display = 'block';
    } finally {
        loading.style.display = 'none';
        btnBuscar.disabled = false;
    }
});

// ============================================================
// RENDERIZADO PROFESIONAL Y RECOMENDACIÓN
// ============================================================
function renderResultadosYRecomendacion(data, terminoBuscado) {
    document.getElementById('terminoMostrado').textContent = data.termino;
    document.getElementById('totalResultados').textContent = data.total;

    const coloresTiendas = {
        'coolbox': 'tag-coolbox',
        'plaza vea': 'tag-plaza-vea',
        'ripley': 'tag-ripley',
        'oechsle': 'tag-oechsle',
        'hiraoka': 'tag-hiraoka'
    };

    const tbody = document.getElementById('tablaResultados');
    tbody.innerHTML = '';
    
    // Precio mínimo general
    const precioMinimo = data.resultados[0].precio;

    data.resultados.forEach((item) => {
        const tr = document.createElement('tr');
        const precioFormateado = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(item.precio);
        const esMinimo = item.precio === precioMinimo;
        
        const tagClass = coloresTiendas[item.tienda.toLowerCase()] || 'tag-plaza-vea';

        tr.innerHTML = `
            <td><span class="tienda-tag ${tagClass}">${escapeHtml(item.tienda)}</span></td>
            <td style="font-weight: 500;">${escapeHtml(item.titulo)}</td>
            <td class="precio ${esMinimo ? 'precio-minimo' : ''}">
                ${precioFormateado} ${esMinimo ? '🏆' : ''}
            </td>
            <td>
                ${item.url ? `<a class="btn-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener">Ver Oferta</a>` : '<span style="color:#94a3b8; font-size:0.85rem;">Sin enlace</span>'}
            </td>
        `;
        tbody.appendChild(tr);
    });

    resultsDiv.style.display = 'block';

    // --- LÓGICA DE RECOMENDACIÓN INTELIGENTE (POR CLÚSTER/MEDIANA) ---
    const mejorOpcion = data.resultados[0];
    
    // Obtenemos todos los precios y calculamos la mediana
    const precios = data.resultados.map(r => r.precio).sort((a, b) => a - b);
    const mediana = precios[Math.floor(precios.length / 2)];
    
    // Calculamos el ahorro respecto a la mediana (el precio "normal" del mercado)
    // Esto evita que una laptop gamer de 7000 soles arruine el cálculo de ahorro.
    let precioReferencia = mediana;
    
    // Si solo hay 1 o 2 resultados, usamos el máximo
    if (precios.length <= 2) {
        precioReferencia = precios[precios.length - 1];
    }

    const ahorro = precioReferencia - mejorOpcion.precio;
    
    let recomendacionHTML = `
        <div class="rec-title">✨ Recomendación de Compra Inteligente</div>
        <div class="rec-body">
            La mejor oferta para <strong>"${escapeHtml(terminoBuscado)}"</strong> está en <strong>${escapeHtml(mejorOpcion.tienda)}</strong> por 
            <span class="rec-price">${new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(mejorOpcion.precio)}</span>.
    `;

    if (ahorro > 0) {
        const porcentajeAhorro = Math.round((ahorro / precioReferencia) * 100);
        recomendacionHTML += `
            <br>
            <span class="rec-savings">Ahorras aproximadamente ${new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(ahorro)} (${porcentajeAhorro}%) frente al precio promedio del mercado.</span>
        `;
    }
    
    recomendacionHTML += `</div>`;
    recCard.innerHTML = recomendacionHTML;
    recCard.style.display = 'block';
}

// ============================================================
// UTILIDADES DE IMAGEN Y CÁMARA
// ============================================================
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const btnSeleccionar = document.getElementById('btnSeleccionar');
const btnAbrirCamara = document.getElementById('btnAbrirCamara');
const previewWrap = document.getElementById('previewWrap');
const previewImg = document.getElementById('previewImg');
const previewCaption = document.getElementById('previewCaption');
const btnDetectar = document.getElementById('btnDetectar');
const cameraWrap = document.getElementById('cameraWrap');
const cameraPreview = document.getElementById('cameraPreview');
const btnCapturar = document.getElementById('btnCapturar');
const btnCerrarCamara = document.getElementById('btnCerrarCamara');

let streamCamara = null;
let imagenSeleccionada = null;

uploadZone.addEventListener('click', () => fileInput.click());
btnSeleccionar.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault(); uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) manejarImagen(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) manejarImagen(e.target.files[0]);
});

function manejarImagen(file) {
    if (!file.type.startsWith('image/')) { alert('El archivo debe ser una imagen.'); return; }
    imagenSeleccionada = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewWrap.style.display = 'block';
        btnDetectar.style.display = 'inline-block';
        previewCaption.textContent = `Archivo listo: ${file.name}`;
        errorDiv.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

btnDetectar.addEventListener('click', () => {
    alert('🚀 ¡Muy pronto! En la siguiente fase, YOLO analizará esta imagen, detectará el producto y buscará sus precios automáticamente. Por ahora, usa la pestaña de "Búsqueda por Texto".');
});

btnAbrirCamara.addEventListener('click', async () => {
    try {
        streamCamara = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
        cameraPreview.srcObject = streamCamara;
        cameraWrap.style.display = 'block';
        previewWrap.style.display = 'none';
        btnAbrirCamara.disabled = true;
    } catch (err) {
        alert('No se pudo abrir la cámara: ' + err.message + '\nVerifica que estés en localhost y des permisos.');
    }
});

btnCerrarCamara.addEventListener('click', cerrarCamara);
function cerrarCamara() {
    if (streamCamara) { streamCamara.getTracks().forEach(t => t.stop()); streamCamara = null; }
    cameraPreview.srcObject = null;
    cameraWrap.style.display = 'none';
    btnAbrirCamara.disabled = false;
}

btnCapturar.addEventListener('click', () => {
    if (!streamCamara) return;
    const canvas = document.createElement('canvas');
    canvas.width = cameraPreview.videoWidth;
    canvas.height = cameraPreview.videoHeight;
    canvas.getContext('2d').drawImage(cameraPreview, 0, 0);
    canvas.toBlob((blob) => {
        const file = new File([blob], 'captura-camara.jpg', { type: 'image/jpeg' });
        manejarImagen(file);
        cerrarCamara();
    }, 'image/jpeg', 0.9);
});

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
</script>
</body>
</html>
