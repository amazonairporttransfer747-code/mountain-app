<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亞馬遜國家山岳協會｜台灣山岳搜尋系統</title>
    
    <!-- CSS Libraries -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --primary-color: #1b4332;
            --primary-light: #2d6a4f;
            --accent-color: #d8f3dc;
            --highlight-color: #e63946;
            --bg-dark: #081c15;
            --bg-light: #f8f9fa;
            --text-dark: #2b2d42;
            --text-muted: #6c757d;
            --border-color: #e9ecef;
            --sidebar-width: 450px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans TC', sans-serif;
        }

        body {
            display: flex;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            background-color: var(--bg-light);
            color: var(--text-dark);
        }

        /* App Container Layout */
        #app-container {
            display: flex;
            width: 100%;
            height: 100%;
            position: relative;
        }

        /* Sidebar Styling */
        #sidebar {
            width: var(--sidebar-width);
            height: 100%;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            border-right: 1px solid rgba(0,0,0,0.1);
            z-index: 1000;
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }

        /* Header Branding */
        .brand-header {
            background: linear-gradient(135deg, var(--bg-dark), var(--primary-color));
            color: #ffffff;
            padding: 18px 20px;
            border-bottom: 3px solid #52b788;
        }

        .brand-header h1 {
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-header .subtitle {
            font-size: 0.75rem;
            color: #b7e4c7;
            margin-top: 4px;
        }

        /* File Uploader Bar */
        .uploader-box {
            padding: 12px 20px;
            background: #f1f5f9;
            border-bottom: 1px solid var(--border-color);
        }

        .drop-zone {
            border: 2px dashed #cbd5e1;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            background: #ffffff;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.82rem;
            color: var(--text-muted);
        }

        .drop-zone:hover {
            border-color: var(--primary-light);
            background: #f8fafc;
        }

        /* Search Controls Filter Form */
        .search-panel {
            padding: 16px 20px;
            background: #ffffff;
            border-bottom: 1px solid var(--border-color);
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .form-group.full-width {
            grid-column: span 2;
        }

        .form-group label {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--primary-color);
            text-transform: uppercase;
        }

        .form-control {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-control:focus {
            border-color: var(--primary-light);
            box-shadow: 0 0 0 2px rgba(45, 106, 79, 0.15);
        }

        .stats-bar {
            grid-column: span 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 6px;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .result-count {
            font-weight: 700;
            color: var(--highlight-color);
        }

        /* Mountain List Table System */
        .list-container {
            flex: 1;
            overflow-y: auto;
            position: relative;
        }

        .mountain-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            text-align: left;
        }

        .mountain-table th {
            position: sticky;
            top: 0;
            background: #f8fafc;
            color: var(--text-dark);
            padding: 10px 8px;
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            z-index: 10;
            white-space: nowrap;
        }

        .mountain-table td {
            padding: 10px 8px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
            word-break: break-word;
        }

        .mountain-table tr {
            cursor: pointer;
            transition: background 0.15s;
        }

        .mountain-table tr:hover {
            background-color: var(--accent-color);
        }

        .mountain-table tr.selected {
            background-color: #d8f3dc !important;
            font-weight: 600;
        }

        .btn-gpx-search {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: #0284c7;
            color: #ffffff;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
            transition: background 0.2s;
        }

        .btn-gpx-search:hover {
            background: #0369a1;
        }

        /* Map Container */
        #map-wrapper {
            flex: 1;
            height: 100%;
            position: relative;
        }

        #map {
            width: 100%;
            height: 100%;
        }

        /* Zoom-dependent Marker Label Custom UI */
        .leaflet-marker-label {
            background: rgba(8, 28, 21, 0.85);
            color: #ffffff;
            border: 1px solid #52b788;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.72rem;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            pointer-events: none;
        }

        .leaflet-marker-label-detailed {
            line-height: 1.2;
            text-align: center;
        }

        /* Detail Modal Drawer */
        .detail-drawer {
            position: absolute;
            bottom: -100%;
            left: 0;
            width: 100%;
            max-height: 50%;
            background: #ffffff;
            box-shadow: 0 -4px 15px rgba(0,0,0,0.15);
            z-index: 1001;
            transition: bottom 0.3s ease;
            display: flex;
            flex-direction: column;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }

        .detail-drawer.active {
            bottom: 0;
        }

        .drawer-header {
            padding: 12px 20px;
            background: var(--primary-color);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }

        .drawer-content {
            padding: 16px 20px;
            overflow-y: auto;
            font-size: 0.85rem;
        }

        .tag-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 8px;
            margin-top: 10px;
        }

        .tag-item {
            background: #f1f5f9;
            padding: 6px 10px;
            border-radius: 4px;
            border-left: 3px solid var(--primary-light);
            font-size: 0.78rem;
        }

        .tag-key {
            font-weight: 700;
            color: var(--text-dark);
        }

        /* Mobile Layout Modifications */
        @media (max-width: 768px) {
            body {
                flex-direction: column;
            }

            #sidebar {
                width: 100%;
                height: 50vh;
                order: 2;
            }

            #map-wrapper {
                height: 50vh;
                order: 1;
            }

            .search-panel {
                grid-template-columns: 1fr;
            }

            .form-group.full-width {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>

<div id="app-container">
    <!-- Sidebar Controls and List Table -->
    <div id="sidebar">
        <div class="brand-header">
            <h1><i class="fa-solid grand-mountain fa-mountain"></i> 亞馬遜國家山岳協會</h1>
            <div class="subtitle">台灣山岳搜尋系統</div>
        </div>

        <!-- File Parser Trigger -->
        <div class="uploader-box">
            <div class="drop-zone" id="drop-zone">
                <i class="fa-solid fa-file-import"></i> 拖曳或點擊選擇 OSM 檔案 (JSON, GeoJSON, GPX, KML)
                <input type="file" id="file-input" multiple accept=".json,.geojson,.gpx,.kml" style="display: none;">
            </div>
        </div>

        <!-- Cascading Search Panel -->
        <div class="search-panel">
            <div class="form-group">
                <label for="select-county">縣市</label>
                <select id="select-county" class="form-control">
                    <option value="">全部縣市</option>
                </select>
            </div>
            <div class="form-group">
                <label for="select-township">鄉鎮市區</label>
                <select id="select-township" class="form-control">
                    <option value="">全部鄉鎮市區</option>
                </select>
            </div>
            <div class="form-group">
                <label for="select-type">山岳類型</label>
                <select id="select-type" class="form-control">
                    <option value="">全部類型</option>
                </select>
            </div>
            <div class="form-group">
                <label for="input-keyword">山名搜尋</label>
                <input type="text" id="input-keyword" class="form-control" placeholder="例如：玉山...">
            </div>
            <div class="stats-bar">
                <span>符合條件：<span id="result-count" class="result-count">0</span> 筆</span>
                <span id="system-status" style="font-size:0.75rem; color:#059669;"><i class="fa-solid fa-circle-check"></i> 系統就緒</span>
            </div>
        </div>

        <!-- Data List Container -->
        <div class="list-container">
            <table class="mountain-table">
                <thead>
                    <tr>
                        <th>名稱</th>
                        <th>高度 (m)</th>
                        <th>類型</th>
                        <th>縣市</th>
                        <th>鄉鎮市區</th>
                        <th>經度</th>
                        <th>緯度</th>
                        <th>搜尋 GPX</th>
                    </tr>
                </thead>
                <tbody id="mountain-table-body">
                    <!-- Dynamic Rows Rendered Here -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Map Viewport -->
    <div id="map-wrapper">
        <div id="map"></div>

        <!-- Details Modal Overlay Drawer -->
        <div class="detail-drawer" id="detail-drawer">
            <div class="drawer-header">
                <h3 id="drawer-title">山岳名稱</h3>
                <button id="drawer-close" style="background:none; border:none; color:white; cursor:pointer;"><i class="fa-solid fa-xmark fa-lg"></i></button>
            </div>
            <div class="drawer-content" id="drawer-body">
                <!-- Dynamic Content -->
            </div>
        </div>
    </div>
</div>

<!-- JS Libraries -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://unpkg.com/@turf/turf@6.5.0/turf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/togeojson/0.16.0/togeojson.min.js"></script>

<script>
/**
 * 亞馬遜國家山岳協會｜台灣山岳搜尋系統
 * Core Architecture & Application Engine
 */

// Global State Management
const AppState = {
    mountains: [],        // Unified Normalized Mountain Database
    filteredMountains: [],// Active Search Results
    selectedMountainId: null,
    layers: {
        satellite: null,
        osm: null,
        topo: null,
        contours: null,
        gpxOverlay: null,
        markerCluster: null
    },
    map: null,
    markersMap: new Map(), // Map OSM_ID -> Leaflet Marker
    moiBoundaries: null    // Derived MOI spatial polygons for reverse geocoding
};

// ------------------------------------------------------------------
// Module 1: File Parsers & Data Normalizers
// ------------------------------------------------------------------

/**
 * Universal Parser Router
 */
async function parseUploadedFile(file) {
    const fileName = file.name.toLowerCase();
    const textContent = await file.text();

    if (fileName.endsWith('.json') || fileName.endsWith('.geojson')) {
        return parseGeoJSONOrOSMJson(textContent);
    } else if (fileName.endsWith('.gpx')) {
        const xml = new DOMParser().parseFromString(textContent, 'text/xml');
        const geojson = toGeoJSON.gpx(xml);
        return parseGeoJSONOrOSMJson(JSON.stringify(geojson), 'GPX');
    } else if (fileName.endsWith('.kml')) {
        const xml = new DOMParser().parseFromString(textContent, 'text/xml');
        const geojson = toGeoJSON.kml(xml);
        return parseGeoJSONOrOSMJson(JSON.stringify(geojson), 'KML');
    }
    return [];
}

/**
 * OSM JSON & GeoJSON Universal Parser
 */
function parseGeoJSONOrOSMJson(content, sourceType = 'OSM_JSON') {
    let raw = JSON.parse(content);
    let parsedMountains = [];

    // Case A: OSM Overpass API Raw JSON Structure
    if (raw.elements && Array.isArray(raw.elements)) {
        raw.elements.forEach(elem => {
            if (elem.type === 'node' || (elem.type === 'way' && elem.center)) {
                const tags = elem.tags || {};
                if (tags.natural === 'peak' || tags.natural === 'volcano' || tags.mountain === 'yes' || tags.ele) {
                    parsedMountains.push(normalizeMountainData({
                        osm_id: `${elem.type}/${elem.id}`,
                        name: tags.name || tags['name:zh'] || tags['name:en'] || '未命名山岳',
                        ele: parseFloat(tags.ele) || null,
                        type: tags.natural || tags.mountain || 'peak',
                        lon: elem.lon || (elem.center ? elem.center.lon : null),
                        lat: elem.lat || (elem.center ? elem.center.lat : null),
                        tags: tags,
                        geometry: { type: 'Point', coordinates: [elem.lon || elem.center.lon, elem.lat || elem.center.lat] },
                        source: sourceType,
                        counties: extractMultiValueTag(tags, ['county', 'addr:county', 'is_in:county']),
                        townships: extractMultiValueTag(tags, ['township', 'addr:township', 'is_in:township']),
                        raw: elem
                    }));
                }
            }
        });
    }
    // Case B: GeoJSON FeatureCollection
    else if (raw.type === 'FeatureCollection' && Array.isArray(raw.features)) {
        raw.features.forEach((feat, idx) => {
            const props = feat.properties || {};
            const coords = feat.geometry ? getFeatureCenterCoordinates(feat.geometry) : [0, 0];
            
            parsedMountains.push(normalizeMountainData({
                osm_id: props.id || props['@id'] || `geo_${idx}_${Date.now()}`,
                name: props.name || props['name:zh'] || props['name:en'] || '未命名山岳',
                ele: parseFloat(props.ele || props.elevation || props.height) || null,
                type: props.natural || props.mountain || props.type || 'peak',
                lon: coords[0],
                lat: coords[1],
                tags: props,
                geometry: feat.geometry,
                source: sourceType === 'OSM_JSON' ? 'GeoJSON' : sourceType,
                counties: extractMultiValueTag(props, ['county', 'addr:county', 'is_in:county']),
                townships: extractMultiValueTag(props, ['township', 'addr:township', 'is_in:township']),
                raw: feat
            }));
        });
    }

    return parsedMountains;
}

/**
 * Extract multi-value arrays from OSM string tags (e.g., "南投縣;花蓮縣" -> ["南投縣", "花蓮縣"])
 */
function extractMultiValueTag(tags, keys) {
    let results = [];
    keys.forEach(k => {
        if (tags[k]) {
            const splitVals = tags[k].split(/[,;|\/]+/);
            splitVals.forEach(v => {
                const trimmed = v.trim();
                if (trimmed && !results.includes(trimmed)) {
                    results.push(trimmed);
                }
            });
        }
    });
    return results;
}

/**
 * Calculate geometry center
 */
function getFeatureCenterCoordinates(geometry) {
    if (geometry.type === 'Point') {
        return geometry.coordinates;
    } else {
        const centroid = turf.centroid(geometry);
        return centroid.geometry.coordinates;
    }
}

/**
 * Normalizes input to Unified Mountain Data Model
 */
function normalizeMountainData(item) {
    return {
        id: item.osm_id,
        name: item.name,
        ele: item.ele,
        type: item.type,
        counties: item.counties || [],
        townships: item.townships || [],
        derived_counties: [], // GIS Spatial Lookup Derived Metadata
        derived_townships: [],
        lon: item.lon,
        lat: item.lat,
        tags: item.tags || {},
        geometry: item.geometry,
        source: item.source,
        raw: item.raw
    };
}

// ------------------------------------------------------------------
// Module 2: Deduplication & Spatial Administrative Lookup Engine
// ------------------------------------------------------------------

/**
 * Deduplicate data prioritizing OSM ID then spatial proximity + name
 */
function deduplicateMountains(newRecords) {
    const existingMap = new Map(AppState.mountains.map(m => [m.id, m]));

    newRecords.forEach(record => {
        if (existingMap.has(record.id)) {
            // Merge properties without overriding OSM raw data
            const existing = existingMap.get(record.id);
            existing.counties = [...new Set([...existing.counties, ...record.counties])];
            existing.townships = [...new Set([...existing.townships, ...record.townships])];
        } else {
            // Spatial proximity check (threshold: 50 meters with exact name match)
            let isDuplicate = false;
            for (let existing of existingMap.values()) {
                if (existing.name === record.name && existing.name !== '未命名山岳') {
                    const distance = turf.distance(
                        turf.point([existing.lon, existing.lat]),
                        turf.point([record.lon, record.lat]),
                        { units: 'meters' }
                    );
                    if (distance < 50) { // Same peak within 50 meters
                        existing.counties = [...new Set([...existing.counties, ...record.counties])];
                        existing.townships = [...new Set([...existing.townships, ...record.townships])];
                        isDuplicate = true;
                        break;
                    }
                }
            }
            if (!isDuplicate) {
                existingMap.set(record.id, record);
            }
        }
    });

    AppState.mountains = Array.from(existingMap.values());
}

/**
 * MOI GIS Administrative Spatial Reverse Lookup
 * Point-in-polygon verification for boundary peak tags
 */
function runSpatialAdminLookup() {
    if (!AppState.moiBoundaries) return;

    AppState.mountains.forEach(m => {
        const pt = turf.point([m.lon, m.lat]);
        AppState.moiBoundaries.features.forEach(poly => {
            if (turf.booleanPointInPolygon(pt, poly)) {
                const c = poly.properties.COUNTYNAME;
                const t = poly.properties.TOWNNAME;
                if (c && !m.derived_counties.includes(c)) m.derived_counties.push(c);
                if (t && !m.derived_townships.includes(t)) m.derived_townships.push(t);
            }
        });
    });
}

// ------------------------------------------------------------------
// Module 3: Map System (Leaflet & Visual Density Management)
// ------------------------------------------------------------------

function initMap() {
    // Base Layers
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri'
    });
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    });
    const topo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; OpenStreetMap, SRTM | Map style &copy; OpenTopoMap'
    });

    AppState.map = L.map('map', {
        center: [23.97565, 120.973881], // Taiwan Geographic Center
        zoom: 8,
        layers: [satellite]
    });

    // Layer Controls
    const baseMaps = {
        "衛星影像 (優先)": satellite,
        "OpenStreetMap": osm,
        "地形圖": topo
    };

    AppState.layers.markerCluster = L.markerClusterGroup({
        disableClusteringAtZoom: 13,
        spiderfyOnMaxZoom: true
    });
    AppState.map.addLayer(AppState.layers.markerCluster);

    L.control.layers(baseMaps, { "山岳點位": AppState.layers.markerCluster }).addTo(AppState.map);

    // Zoom level listener for dynamic label density rendering
    AppState.map.on('zoomend', updateMarkerLabelsDensity);
}

/**
 * Render Leaflet Markers with Cluster and Zoom Density Logic
 */
function renderMapMarkers() {
    AppState.layers.markerCluster.clearLayers();
    AppState.markersMap.clear();

    AppState.filteredMountains.forEach(m => {
        const marker = L.marker([m.lat, m.lon], {
            title: m.name
        });

        // Popup Content
        const displayCounties = getCombinedList(m.counties, m.derived_counties).join('、') || '未標示';
        const displayTownships = getCombinedList(m.townships, m.derived_townships).join('、') || '未標示';

        const popupHTML = `
            <div style="font-size:0.85rem;">
                <h4 style="color:var(--primary-color); margin-bottom:4px;">${m.name}</h4>
                <b>海拔：</b> ${m.ele ? m.ele + ' m' : '未知'}<br>
                <b>類型：</b> ${m.type}<br>
                <b>縣市：</b> ${displayCounties}<br>
                <b>鄉鎮：</b> ${displayTownships}<br>
                <button onclick="openDetailDrawer('${m.id}')" style="margin-top:6px; background:var(--primary-light); color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:0.75rem;">查看完整詳細資訊</button>
            </div>
        `;
        marker.bindPopup(popupHTML);

        // Click Event (Map -> List Sync)
        marker.on('click', () => {
            highlightListRow(m.id);
            AppState.selectedMountainId = m.id;
        });

        AppState.markersMap.set(m.id, marker);
        AppState.layers.markerCluster.addLayer(marker);
    });

    updateMarkerLabelsDensity();
    fitMapBounds();
}

/**
 * Adjust Label density dynamically depending on map Zoom level
 */
function updateMarkerLabelsDensity() {
    const currentZoom = AppState.map.getZoom();

    AppState.markersMap.forEach((marker, id) => {
        const m = AppState.mountains.find(item => item.id === id);
        if (!m) return;

        marker.unbindTooltip();

        if (currentZoom >= 15) {
            // Near Distance: Full Details
            const displayCounties = getCombinedList(m.counties, m.derived_counties).join('、');
            const displayTownships = getCombinedList(m.townships, m.derived_townships).join('、');
            marker.bindTooltip(`
                <div class="leaflet-marker-label leaflet-marker-label-detailed">
                    <b>${m.name}</b><br>
                    ${m.ele ? m.ele + 'm' : ''}<br>
                    <span style="font-size:0.65rem; color:#a7f3d0;">${displayCounties} ${displayTownships}</span>
                </div>
            `, { permanent: true, direction: 'top', className: 'custom-tooltip' });
        } else if (currentZoom >= 12) {
            // Mid Distance: Name + Altitude
            marker.bindTooltip(`
                <div class="leaflet-marker-label">
                    ${m.name} ${m.ele ? '(' + m.ele + 'm)' : ''}
                </div>
            `, { permanent: true, direction: 'top', className: 'custom-tooltip' });
        }
        // Far Distance (zoom < 12): Show Markers/Clusters only
    });
}

/**
 * Auto-Fit map view bounds to match filtered mountains
 */
function fitMapBounds() {
    if (AppState.filteredMountains.length === 0) return;

    if (AppState.filteredMountains.length === 1) {
        const target = AppState.filteredMountains[0];
        AppState.map.flyTo([target.lat, target.lon], 14, { duration: 1.2 });
    } else {
        const bounds = L.latLngBounds(AppState.filteredMountains.map(m => [m.lat, m.lon]));
        AppState.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
    }
}

// ------------------------------------------------------------------
// Module 4: Cascading Search & UI Binding Engine
// ------------------------------------------------------------------

function initSearchFilters() {
    // Collect all dynamic values across datasets
    populateDropdowns();

    // Event Listeners
    document.getElementById('select-county').addEventListener('change', () => {
        updateTownshipDropdown();
        executeSearch();
    });
    document.getElementById('select-township').addEventListener('change', executeSearch);
    document.getElementById('select-type').addEventListener('change', executeSearch);
    document.getElementById('input-keyword').addEventListener('input', executeSearch);
}

function populateDropdowns() {
    const countiesSet = new Set();
    const typesSet = new Set();

    AppState.mountains.forEach(m => {
        getCombinedList(m.counties, m.derived_counties).forEach(c => countiesSet.add(c));
        if (m.type) typesSet.add(m.type);
    });

    // Fill County Select
    const countySelect = document.getElementById('select-county');
    countySelect.innerHTML = '<option value="">全部縣市</option>';
    Array.from(countiesSet).sort().forEach(c => {
        countySelect.innerHTML += `<option value="${c}">${c}</option>`;
    });

    // Fill Type Select
    const typeSelect = document.getElementById('select-type');
    typeSelect.innerHTML = '<option value="">全部類型</option>';
    Array.from(typesSet).sort().forEach(t => {
        typeSelect.innerHTML += `<option value="${t}">${t}</option>`;
    });

    updateTownshipDropdown();
}

function updateTownshipDropdown() {
    const selectedCounty = document.getElementById('select-county').value;
    const townshipSelect = document.getElementById('select-township');
    townshipSelect.innerHTML = '<option value="">全部鄉鎮市區</option>';

    const townshipsSet = new Set();

    AppState.mountains.forEach(m => {
        const mCounties = getCombinedList(m.counties, m.derived_counties);
        if (!selectedCounty || mCounties.includes(selectedCounty)) {
            getCombinedList(m.townships, m.derived_townships).forEach(t => townshipsSet.add(t));
        }
    });

    Array.from(townshipsSet).sort().forEach(t => {
        townshipSelect.innerHTML += `<option value="${t}">${t}</option>`;
    });
}

/**
 * Filter Execution Logic (Intersection of all rules)
 */
function executeSearch() {
    const countyVal = document.getElementById('select-county').value;
    const townshipVal = document.getElementById('select-township').value;
    const typeVal = document.getElementById('select-type').value;
    const keywordVal = document.getElementById('input-keyword').value.trim().toLowerCase();

    AppState.filteredMountains = AppState.mountains.filter(m => {
        const allCounties = getCombinedList(m.counties, m.derived_counties);
        const allTownships = getCombinedList(m.townships, m.derived_townships);

        // County Condition (Multi-value inclusive check)
        if (countyVal && !allCounties.includes(countyVal)) return false;

        // Township Condition (Multi-value inclusive check)
        if (townshipVal && !allTownships.includes(townshipVal)) return false;

        // Type Condition
        if (typeVal && m.type !== typeVal) return false;

        // Keyword Fuzzy Search Condition
        if (keywordVal && !m.name.toLowerCase().includes(keywordVal)) return false;

        return true;
    });

    // Update UI Counter
    document.getElementById('result-count').textContent = AppState.filteredMountains.length;

    // Render Table & Map
    renderTable();
    renderMapMarkers();
}

/**
 * Utility: Combine raw tags and spatial derived arrays
 */
function getCombinedList(rawArr, derivedArr) {
    return [...new Set([...(rawArr || []), ...(derivedArr || [])])];
}

// ------------------------------------------------------------------
// Module 5: Interactive Table & Bi-Directional Map-List Sync
// ------------------------------------------------------------------

function renderTable() {
    const tbody = document.getElementById('mountain-table-body');
    tbody.innerHTML = '';

    if (AppState.filteredMountains.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:var(--text-muted);">無符合條件之山岳資料</td></tr>';
        return;
    }

    AppState.filteredMountains.forEach(m => {
        const tr = document.createElement('tr');
        tr.id = `row-${m.id}`;
        if (m.id === AppState.selectedMountainId) {
            tr.classList.add('selected');
        }

        const countiesStr = getCombinedList(m.counties, m.derived_counties).join('、') || '-';
        const townshipsStr = getCombinedList(m.townships, m.derived_townships).join('、') || '-';
        const gpxSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(m.name + ' GPX')}`;

        tr.innerHTML = `
            <td><b>${m.name}</b></td>
            <td>${m.ele ? m.ele : '-'}</td>
            <td><span style="background:#e2e8f0; padding:2px 6px; border-radius:4px; font-size:0.72rem;">${m.type}</span></td>
            <td>${countiesStr}</td>
            <td>${townshipsStr}</td>
            <td>${m.lon.toFixed(4)}</td>
            <td>${m.lat.toFixed(4)}</td>
            <td>
                <a href="${gpxSearchUrl}" target="_blank" class="btn-gpx-search" onclick="event.stopPropagation();">
                    <i class="fa-solid fa-magnifying-glass"></i> 搜尋 GPX
                </a>
            </td>
        `;

        // Click Event (List -> Map Sync)
        tr.addEventListener('click', () => {
            selectMountainFromList(m);
        });

        tbody.appendChild(tr);
    });
}

/**
 * List -> Map Sync Execution
 */
function selectMountainFromList(mountain) {
    AppState.selectedMountainId = mountain.id;

    // Highlight row
    document.querySelectorAll('.mountain-table tr').forEach(r => r.classList.remove('selected'));
    const targetRow = document.getElementById(`row-${mountain.id}`);
    if (targetRow) targetRow.classList.add('selected');

    // Pan Map & Open Popup
    AppState.map.flyTo([mountain.lat, mountain.lon], 15, { duration: 1.0 });

    const marker = AppState.markersMap.get(mountain.id);
    if (marker) {
        AppState.layers.markerCluster.zoomToShowLayer(marker, () => {
            marker.openPopup();
        });
    }
}

/**
 * Map -> List Highlight Execution
 */
function highlightListRow(mountainId) {
    document.querySelectorAll('.mountain-table tr').forEach(r => r.classList.remove('selected'));
    const targetRow = document.getElementById(`row-${mountainId}`);
    if (targetRow) {
        targetRow.classList.add('selected');
        targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// ------------------------------------------------------------------
// Module 6: Detail Drawer Modal & Tag Inspector
// ------------------------------------------------------------------

function openDetailDrawer(mountainId) {
    const m = AppState.mountains.find(item => item.id === mountainId);
    if (!m) return;

    document.getElementById('drawer-title').textContent = `${m.name} ${m.ele ? '(' + m.ele + ' m)' : ''}`;

    const drawerBody = document.getElementById('drawer-body');
    const countiesStr = getCombinedList(m.counties, m.derived_counties).join('、') || '無資料';
    const townshipsStr = getCombinedList(m.townships, m.derived_townships).join('、') || '無資料';

    let tagsGrid = '';
    Object.entries(m.tags).forEach(([k, v]) => {
        tagsGrid += `
            <div class="tag-item">
                <span class="tag-key">${k}</span>: <span>${v}</span>
            </div>
        `;
    });

    drawerBody.innerHTML = `
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:12px;">
            <div><b>OSM ID：</b> ${m.id}</div>
            <div><b>資料來源：</b> ${m.source}</div>
            <div><b>行政縣市：</b> ${countiesStr}</div>
            <div><b>鄉鎮市區：</b> ${townshipsStr}</div>
            <div><b>WGS84 座標：</b> ${m.lon.toFixed(6)}, ${m.lat.toFixed(6)}</div>
            <div><b>山岳類型：</b> ${m.type}</div>
        </div>
        <h4 style="margin-top:10px; color:var(--primary-color);">原始 OSM 標籤 (Tags Inspector)</h4>
        <div class="tag-grid">
            ${tagsGrid || '<div style="color:var(--text-muted)">無額外標籤資料</div>'}
        </div>
    `;

    document.getElementById('detail-drawer').classList.add('active');
}

document.getElementById('drawer-close').addEventListener('click', () => {
    document.getElementById('detail-drawer').classList.remove('active');
});

// ------------------------------------------------------------------
// Module 7: Application Initialization & File Upload Listeners
// ------------------------------------------------------------------

function initUploader() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary-color)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#cbd5e1';
    });

    dropZone.addEventListener('drop', async (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#cbd5e1';
        if (e.dataTransfer.files.length > 0) {
            await handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            await handleFiles(e.target.files);
        }
    });
}

async function handleFiles(files) {
    document.getElementById('system-status').innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 解析資料中...`;
    
    let allNewMountains = [];
    for (let i = 0; i < files.length; i++) {
        const parsed = await parseUploadedFile(files[i]);
        allNewMountains = allNewMountains.concat(parsed);
    }

    // Deduplicate & Merge
    deduplicateMountains(allNewMountains);

    // Spatial Reverse Lookup (if boundaries exist)
    runSpatialAdminLookup();

    // Re-initialize Filter dropdown options and refresh Search
    populateDropdowns();
    executeSearch();

    document.getElementById('system-status').innerHTML = `<i class="fa-solid fa-circle-check"></i> 載入 ${AppState.mountains.length} 筆資料`;
}

// System Bootstrapping
window.addEventListener('DOMContentLoaded', () => {
    initMap();
    initSearchFilters();
    initUploader();
});
</script>
</body>
</html>
