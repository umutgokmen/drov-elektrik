import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Download, FileText, Settings, Layers,
  ZoomIn, ZoomOut, RotateCcw, Maximize2,
  CheckCircle, AlertCircle, AlertTriangle,
  ChevronDown, ChevronUp, Info, Clock, Save
} from 'lucide-react';
import DrawingCanvas from './components/DrawingCanvas';
import OrderHistory from './components/OrderHistory';

// API Base URL
const API_BASE = 'http://localhost:8000/api/v1';

// Box models (loaded 서버에서)
const DEFAULT_BOX_MODELS = [
  { id: 'ejb21', name: 'EJB 21', internal_width: 179, internal_length: 169, internal_depth: 160, rail_count: 1, max_terminals: 30, max_holes_long: 10, max_holes_short: 8 },
  { id: 'ejb31', name: 'EJB 31', internal_width: 258, internal_length: 249, internal_depth: 294, rail_count: 2, max_terminals: 52, max_holes_long: 28, max_holes_short: 20 },
  { id: 'ejb51', name: 'EJB 51', internal_width: 388, internal_length: 390, internal_depth: 370, rail_count: 2, max_terminals: 80, max_holes_long: 44, max_holes_short: 24 },
  { id: 'ejb61', name: 'EJB 61', internal_width: 470, internal_length: 500, internal_depth: 360, rail_count: 3, max_terminals: 92, max_holes_long: 72, max_holes_short: 48 },
  { id: 'ejb71', name: 'EJB 71', internal_width: 530, internal_length: 600, internal_depth: 410, rail_count: 3, max_terminals: 110, max_holes_long: 90, max_holes_short: 59 },
  { id: 'ejb91', name: 'EJB 91', internal_width: 650, internal_length: 700, internal_depth: 510, rail_count: 3, max_terminals: 140, max_holes_long: 112, max_holes_short: 70 },
];

function App() {
  // State
  const [boxModels, setBoxModels] = useState(DEFAULT_BOX_MODELS);
  const [selectedBoxId, setSelectedBoxId] = useState('ejb51');
  const [config, setConfig] = useState({
    terminals: 24,
    holesTop: 3,
    holesBottom: 3,
    holesLeft: 0,
    holesRight: 0
  });
  const [validation, setValidation] = useState({ is_valid: true, errors: [], warnings: [] });
  const [zoom, setZoom] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('connecting');

  // Order history state
  const [orders, setOrders] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const selectedBox = boxModels.find(b => b.id === selectedBoxId) || boxModels[0];

  // Load box models from API
  useEffect(() => {
    const loadBoxModels = async () => {
      try {
        const response = await fetch(`${API_BASE}/boxes`);
        if (response.ok) {
          const data = await response.json();
          setBoxModels(data.map(box => ({
            id: box.id,
            name: box.name,
            internal_width: box.internal_width,
            internal_length: box.internal_length,
            internal_depth: box.internal_depth,
            rail_count: box.rail_count,
            max_terminals: box.max_terminals,
            max_holes_long: box.max_holes_long,
            max_holes_short: box.max_holes_short
          })));
          setApiStatus('connected');
        }
      } catch (error) {
        console.warn('API not available, using fallback data');
        setApiStatus('offline');
      }
    };
    loadBoxModels();
  }, []);

  // Validate configuration via API
  useEffect(() => {
    const validateConfig = async () => {
      if (apiStatus !== 'connected') {
        // Local validation fallback
        const errors = [];
        if (config.terminals > selectedBox.max_terminals) {
          errors.push({ field: 'terminals', message: `Max ${selectedBox.max_terminals} terminals` });
        }
        setValidation({ is_valid: errors.length === 0, errors, warnings: [] });
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            box_id: selectedBoxId,
            terminals: config.terminals,
            holes_top: config.holesTop,
            holes_bottom: config.holesBottom,
            holes_left: config.holesLeft,
            holes_right: config.holesRight
          })
        });
        if (response.ok) {
          const data = await response.json();
          setValidation(data);
        }
      } catch (error) {
        console.warn('Validation API error', error);
      }
    };

    const debounce = setTimeout(validateConfig, 300);
    return () => clearTimeout(debounce);
  }, [selectedBoxId, config, selectedBox, apiStatus]);

  // Download handlers
  const downloadPDF = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight
        })
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `DRV-${selectedBoxId.toUpperCase()}-001.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('PDF download error', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadDXF = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate/dxf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight
        })
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `DRV-${selectedBoxId.toUpperCase()}-001.dxf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('DXF download error', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadSTEP = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate/step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight
        })
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `DRV-${selectedBoxId.toUpperCase()}-001.step`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('STEP download error', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Input handlers
  const handleInputChange = (field, value) => {
    let numValue = parseInt(value) || 0;
    if (numValue < 0) numValue = 0;

    // Clamp to max values
    if (field === 'terminals') numValue = Math.min(numValue, selectedBox.max_terminals);
    if (field === 'holesTop' || field === 'holesBottom') numValue = Math.min(numValue, selectedBox.max_holes_long);
    if (field === 'holesLeft' || field === 'holesRight') numValue = Math.min(numValue, selectedBox.max_holes_short);

    setConfig(prev => ({ ...prev, [field]: numValue }));
  };

  const totalHoles = config.holesTop + config.holesBottom + config.holesLeft + config.holesRight;

  // BOM data
  const bomItems = [
    { name: `${selectedBox.name} Enclosure`, code: `P+F-${selectedBox.id.toUpperCase()}`, qty: 1, isSaltMalzeme: false },
    { name: 'NS 35 DIN Rail', code: 'NS35-DIN', qty: selectedBox.rail_count, isSaltMalzeme: false },
    { name: 'UT 2,5 Terminal Block', code: 'PHX-UT2.5', qty: config.terminals, isSaltMalzeme: false },
    { name: 'M20 Cable Gland', code: 'M20-GL', qty: totalHoles, isSaltMalzeme: false },
    { name: 'EJB Cover', code: 'EJB-COVER', qty: 1, isSaltMalzeme: true },
    { name: 'CLIPFIX 35/5 End Clamp', code: 'pnl_302203_CLIPFIX-35-5', qty: 2, isSaltMalzeme: true },
    { name: 'Drain Valve M20x1.5', code: 'Drain_Valve_M20x1.5mm', qty: 1, isSaltMalzeme: true },
  ].filter(item => item.qty > 0);

  // Preview State
  const [previewMode, setPreviewMode] = useState('2d'); // '2d' or '3d'
  const [previewSvg, setPreviewSvg] = useState(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // 3D Preview Fetch Logic
  const fetch3DModel = useCallback(async () => {
    setIsPreviewLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight
        })
      });
      if (response.ok) {
        const svgText = await response.text();
        setPreviewSvg(svgText);
        setPreviewMode('3d');
      }
    } catch (error) {
      console.error('Preview error', error);
    } finally {
      setIsPreviewLoading(false);
    }
  }, [selectedBoxId, config]);

  const toggle3DPreview = () => {
    if (previewMode === '3d') {
      setPreviewMode('2d');
    } else {
      fetch3DModel();
    }
  };

  // Fullscreen Handler
  const toggleFullScreen = () => {
    const elem = document.querySelector('.preview-canvas-container');
    if (!document.fullscreenElement) {
      elem.requestFullscreen().catch(err => {
        console.error(`Error enabling full-screen mode: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  };

  // Save Config Handler (JSON download - kept for offline use)
  const saveConfig = () => {
    const data = {
      box_id: selectedBoxId,
      config: config,
      date: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `config-${selectedBoxId}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Save Order to backend
  const saveOrderToHistory = async () => {
    if (apiStatus !== 'connected') return;
    try {
      await fetch(`${API_BASE}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight,
        }),
      });
      await loadOrders();
    } catch (error) {
      console.error('Save order error', error);
    }
  };

  // Load orders from backend
  const loadOrders = async () => {
    if (apiStatus !== 'connected') return;
    try {
      const response = await fetch(`${API_BASE}/orders`);
      if (response.ok) {
        setOrders(await response.json());
      }
    } catch (error) {
      console.warn('Could not load orders', error);
    }
  };

  // Load an order into the configurator
  const loadOrderConfig = (order) => {
    setSelectedBoxId(order.box_id);
    setConfig({
      terminals: order.terminals,
      holesTop: order.holes_top,
      holesBottom: order.holes_bottom,
      holesLeft: order.holes_left,
      holesRight: order.holes_right,
    });
    setShowHistory(false);
  };

  // Auto-refresh 3D preview if active and config changes? No, too slow. Manual refresh.
  // But if mode is 3d and config changes, maybe revert to 2d or show stale warning?
  // Let's keep it simple: switch to 2d on config change.
  // Auto-refresh 3D preview on config change
  useEffect(() => {
    if (previewMode === '3d') {
      const debounce = setTimeout(() => {
        fetch3DModel();
      }, 800); // 800ms debounce for smoother experience
      return () => clearTimeout(debounce);
    }
  }, [config, selectedBoxId, previewMode]); // eslint-disable-line react-hooks/exhaustive-deps

  // Load order history once connected
  useEffect(() => {
    if (apiStatus === 'connected') {
      loadOrders();
    }
  }, [apiStatus]); // eslint-disable-line react-hooks/exhaustive-deps

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveConfig();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        if (validation.is_valid && !isLoading) {
          downloadPDF();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedBoxId, config, validation, isLoading]);


  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <div className="app-logo-icon">DV</div>
          <div>
            <div className="app-logo-text">DROV Engineering</div>
            <div className="app-logo-subtitle">Configurator v2.1</div>
          </div>
        </div>

        <div className="toolbar-actions">
          <button
            className="toolbar-btn"
            onClick={saveConfig}
            title="Save Configuration (Ctrl+S)"
          >
            <FileText size={16} />
            Save
          </button>
          <button
            className="toolbar-btn"
            onClick={saveOrderToHistory}
            disabled={apiStatus !== 'connected' || !validation.is_valid}
            title="Save order to history"
          >
            <Save size={16} />
            Save Order
          </button>
          <button
            className="toolbar-btn"
            onClick={() => { loadOrders(); setShowHistory(true); }}
            disabled={apiStatus !== 'connected'}
            title="View order history"
          >
            <Clock size={16} />
            History
          </button>
          <button
            className="toolbar-btn"
            onClick={downloadDXF}
            disabled={!validation.is_valid || isLoading}
          >
            <Layers size={16} />
            DXF
          </button>
          <button
            className="toolbar-btn"
            onClick={downloadSTEP}
            disabled={!validation.is_valid || isLoading}
          >
            <Box size={16} />
            STEP
          </button>
          <button
            className="toolbar-btn primary"
            onClick={downloadPDF}
            disabled={!validation.is_valid || isLoading}
          >
            {isLoading ? (
              <div className="loading-spinner" />
            ) : (
              <>
                <Download size={16} />
                PDF
              </>
            )}
          </button>
        </div>
      </header>

      {/* Left Panel - Configuration */}
      <div className="panel">
        <div className="panel-header">
          <span>Configuration</span>
          <Settings size={14} />
        </div>
        <div className="panel-content">
          {/* Box Model Selection */}
          <div className="config-section">
            <div className="config-section-title">
              <Box size={12} />
              Enclosure Model
            </div>
            <div className="form-group">
              <select
                className="form-select"
                value={selectedBoxId}
                onChange={(e) => setSelectedBoxId(e.target.value)}
              >
                {boxModels.map(box => (
                  <option key={box.id} value={box.id}>{box.name}</option>
                ))}
              </select>
            </div>
            <div className="box-specs">
              <div className="box-spec-item">
                <span className="box-spec-label">Dimensions</span>
                <span className="box-spec-value">{selectedBox.internal_width}×{selectedBox.internal_length}×{selectedBox.internal_depth}</span>
              </div>
              <div className="box-spec-item">
                <span className="box-spec-label">DIN Rails</span>
                <span className="box-spec-value">{selectedBox.rail_count}</span>
              </div>
              <div className="box-spec-item">
                <span className="box-spec-label">Max Terminals</span>
                <span className="box-spec-value">{selectedBox.max_terminals}</span>
              </div>
            </div>
          </div>

          {/* Terminal Count */}
          <div className="config-section">
            <div className="config-section-title">
              <Settings size={12} />
              Terminal Blocks
            </div>
            <div className="form-group">
              <div className="form-label">
                <span>UT 2,5 Count</span>
                <span className="form-label-value">{config.terminals} / {selectedBox.max_terminals}</span>
              </div>
              <input
                type="range"
                className="form-slider"
                min="0"
                max={selectedBox.max_terminals}
                value={config.terminals}
                onChange={(e) => handleInputChange('terminals', e.target.value)}
              />
              <div className="number-input-group" style={{ marginTop: '8px' }}>
                <input
                  type="number"
                  className="form-input"
                  value={config.terminals}
                  onChange={(e) => handleInputChange('terminals', e.target.value)}
                  min="0"
                  max={selectedBox.max_terminals}
                />
                <button className="number-btn" onClick={() => handleInputChange('terminals', config.terminals - 1)}>
                  <ChevronDown size={14} />
                </button>
                <button className="number-btn" onClick={() => handleInputChange('terminals', config.terminals + 1)}>
                  <ChevronUp size={14} />
                </button>
              </div>
            </div>
          </div>

          {/* M20 Holes */}
          <div className="config-section">
            <div className="config-section-title">
              <Layers size={12} />
              M20 Cable Entries
            </div>
            <div className="holes-grid">
              {[
                { field: 'holesTop', label: 'Top', max: selectedBox.max_holes_long },
                { field: 'holesBottom', label: 'Bottom', max: selectedBox.max_holes_long },
                { field: 'holesLeft', label: 'Left', max: selectedBox.max_holes_short },
                { field: 'holesRight', label: 'Right', max: selectedBox.max_holes_short },
              ].map(({ field, label, max }) => (
                <div key={field} className="hole-input-wrapper">
                  <div className="form-label">
                    <span>{label}</span>
                    <span className="form-label-value">max {max}</span>
                  </div>
                  <input
                    type="number"
                    className="form-input"
                    value={config[field]}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    min="0"
                    max={max}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Center Panel - Preview */}
      <div className="preview-panel">
        <div className="preview-toolbar">
          <div className="preview-controls">
            <button className="preview-btn" onClick={() => setZoom(z => Math.max(25, z - 25))}>
              <ZoomOut size={16} />
            </button>
            <span className="zoom-display">{zoom}%</span>
            <button className="preview-btn" onClick={() => setZoom(z => Math.min(200, z + 25))}>
              <ZoomIn size={16} />
            </button>
            <button className="preview-btn" onClick={() => setZoom(100)}>
              <RotateCcw size={16} />
            </button>
          </div>

          <div className="preview-controls" style={{ borderLeft: '1px solid #ddd', paddingLeft: '8px', marginLeft: '8px' }}>
            <button
              className={`preview-btn ${previewMode === '3d' ? 'active' : ''}`}
              onClick={toggle3DPreview}
              title="Toggle High-Fidelity 3D View"
            >
              {isPreviewLoading ? <div className="loading-spinner" style={{ width: 16, height: 16, border: '2px solid #ccc', borderTopColor: '#333' }} /> : <Box size={16} color={previewMode === '3d' ? '#ffffff' : '#64748b'} />}
              <span style={{ marginLeft: 6, fontSize: 12, fontWeight: 500, color: previewMode === '3d' ? '#ffffff' : '#64748b' }}>3D View</span>
            </button>
          </div>

          <div className="preview-controls" style={{ marginLeft: 'auto' }}>
            <button className="preview-btn" onClick={toggleFullScreen} title="Toggle Fullscreen">
              <Maximize2 size={16} />
            </button>
          </div>
        </div>
        <div className="preview-canvas-container">
          <div
            className="preview-canvas"
            style={previewMode === '3d' ? { width: '100%', height: '100%', overflow: 'hidden' } : { transform: `scale(${zoom / 100})`, transformOrigin: 'center center' }}
          >
            {previewMode === '3d' && previewSvg ? (
              <div dangerouslySetInnerHTML={{ __html: previewSvg }} style={{ width: '100%', height: '100%' }} />
            ) : (
              <DrawingCanvas
                box={{
                  id: selectedBox.id,
                  name: selectedBox.name,
                  internalWidth: selectedBox.internal_width,
                  internalLength: selectedBox.internal_length,
                  internalDepth: selectedBox.internal_depth,
                  railCount: selectedBox.rail_count,
                  maxTerminals: selectedBox.max_terminals
                }}
                config={config}
              />
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Details */}
      <div className="panel">
        <div className="panel-header">
          <span>Details</span>
          <Info size={14} />
        </div>
        <div className="panel-content">
          {/* Validation Status */}
          <div className="details-section">
            <div className="details-section-title">Validation</div>
            <div className={`validation-status ${validation.is_valid ? 'valid' : 'invalid'}`}>
              <div className="validation-icon">
                {validation.is_valid ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
              </div>
              <span>{validation.is_valid ? 'Configuration Valid' : 'Invalid Configuration'}</span>
            </div>
            {validation.errors?.map((err, i) => (
              <div key={i} className="validation-status invalid" style={{ marginTop: '8px' }}>
                <AlertCircle size={14} />
                <span style={{ fontSize: '11px' }}>{err.message}</span>
              </div>
            ))}
            {validation.warnings?.map((warn, i) => (
              <div key={i} className="validation-status warning" style={{ marginTop: '8px' }}>
                <AlertTriangle size={14} />
                <span style={{ fontSize: '11px' }}>{warn.message}</span>
              </div>
            ))}
          </div>

          {/* BOM */}
          <div className="details-section">
            <div className="details-section-title">Bill of Materials</div>
            <table className="bom-table">
              <thead>
                <tr>
                  <th>Part</th>
                  <th>Code</th>
                  <th>Qty</th>
                </tr>
              </thead>
              <tbody>
                {bomItems.map((item, i) => (
                  <tr key={i} style={item.isSaltMalzeme ? { opacity: 0.75, fontStyle: 'italic' } : {}}>
                    <td>{item.name}{item.isSaltMalzeme && <span title="Standard salt malzeme item" style={{ marginLeft: 4, fontSize: 9, color: '#8b5cf6' }}>*</span>}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '10px' }}>{item.code}</td>
                    <td>{item.qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ fontSize: '9px', color: '#94a3b8', marginTop: '4px' }}>* Standard salt malzeme (always included)</div>
          </div>

          {/* Drawing Info */}
          <div className="details-section">
            <div className="details-section-title">Drawing Information</div>
            <div className="drawing-info">
              <div className="drawing-info-item">
                <div className="drawing-info-label">Drawing No.</div>
                <div className="drawing-info-value">DRV-{selectedBox.id.toUpperCase()}-001</div>
              </div>
              <div className="drawing-info-item">
                <div className="drawing-info-label">Scale</div>
                <div className="drawing-info-value">1:2</div>
              </div>
              <div className="drawing-info-item">
                <div className="drawing-info-label">Sheet</div>
                <div className="drawing-info-value">1/1</div>
              </div>
              <div className="drawing-info-item">
                <div className="drawing-info-label">Date</div>
                <div className="drawing-info-value">{new Date().toLocaleDateString('tr-TR')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <footer className="app-statusbar">
        <div className="status-item">
          <div className={`status-indicator ${apiStatus === 'connected' ? '' : apiStatus === 'offline' ? 'error' : 'warning'}`}></div>
          <span>API: {apiStatus === 'connected' ? 'Connected' : apiStatus === 'offline' ? 'Offline Mode' : 'Connecting...'}</span>
        </div>
        <div className="status-item">
          <span>
            <span className="kbd">Ctrl</span> + <span className="kbd">S</span> Save
          </span>
          <span style={{ marginLeft: '16px' }}>
            <span className="kbd">Ctrl</span> + <span className="kbd">P</span> Export PDF
          </span>
        </div>
        <div className="status-item">
          <span>Units: mm</span>
        </div>
      </footer>

      {/* Order History Modal */}
      {showHistory && (
        <OrderHistory
          orders={orders}
          boxModels={boxModels}
          onLoad={loadOrderConfig}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
}

export default App;
