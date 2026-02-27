import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Download, FileText, Settings, Layers,
  ZoomIn, ZoomOut, RotateCcw, Maximize2,
  CheckCircle, AlertCircle, AlertTriangle,
  ChevronDown, ChevronUp, Info, LogOut,
  Plus, Trash2, Circle
} from 'lucide-react';
import DrawingCanvas from './components/DrawingCanvas';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import { useAuth } from './contexts/AuthContext';

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
  const { user, loading: authLoading, logout } = useAuth();
  const [authMode, setAuthMode] = useState('login');

  if (authLoading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-logo">
            <div className="app-logo-icon">DV</div>
            <p>Yukleniyor...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    if (authMode === 'register') {
      return <RegisterPage onSwitchToLogin={() => setAuthMode('login')} />;
    }
    return <LoginPage onSwitchToRegister={() => setAuthMode('register')} />;
  }

  return <ConfiguratorApp user={user} logout={logout} />;
}

function ConfiguratorApp({ user, logout }) {
  // State
  const [boxModels, setBoxModels] = useState(DEFAULT_BOX_MODELS);
  const [selectedBoxId, setSelectedBoxId] = useState('ejb51');
  const [config, setConfig] = useState({
    terminals: 24,
    holesTop: 3,
    holesBottom: 3,
    holesLeft: 0,
    holesRight: 0,
    holeSizeTop: 'M20',
    holeSizeBottom: 'M20',
    holeSizeLeft: 'M20',
    holeSizeRight: 'M20',
  });
  const [holeSizes, setHoleSizes] = useState({});
  const [validation, setValidation] = useState({ is_valid: true, errors: [], warnings: [] });
  const [zoom, setZoom] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('connecting');
  const [userList, setUserList] = useState([]);
  const [controllerId, setControllerId] = useState(null);
  const [coverElements, setCoverElements] = useState([]);
  const [coverCatalog, setCoverCatalog] = useState([]);
  const [orders, setOrders] = useState([]);
  const [showOrders, setShowOrders] = useState(false);

  const selectedBox = boxModels.find(b => b.id === selectedBoxId) || boxModels[0];

  const token = localStorage.getItem('token');

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

  // Load hole sizes from API
  useEffect(() => {
    fetch(`${API_BASE}/hole-sizes`)
      .then((res) => res.ok ? res.json() : {})
      .then((data) => setHoleSizes(data))
      .catch(() => setHoleSizes({ M20: { diameter: 20 }, M25: { diameter: 25 }, M32: { diameter: 32 } }));
  }, []);

  // Load cover element catalog
  useEffect(() => {
    fetch(`${API_BASE}/cover-elements`)
      .then((res) => res.ok ? res.json() : [])
      .then((data) => setCoverCatalog(data))
      .catch(() => {});
  }, []);

  // Load user list for controller selection
  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/auth/users`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.ok ? res.json() : [])
      .then((data) => setUserList(data))
      .catch(() => {});
  }, [token]);

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

  const controllerName = userList.find(u => u.id === controllerId)?.full_name || null;

  const buildConfigPayload = () => ({
    box_id: selectedBoxId,
    terminals: config.terminals,
    holes_top: config.holesTop,
    holes_bottom: config.holesBottom,
    holes_left: config.holesLeft,
    holes_right: config.holesRight,
    holes_top_spec: { count: config.holesTop, size: config.holeSizeTop },
    holes_bottom_spec: { count: config.holesBottom, size: config.holeSizeBottom },
    holes_left_spec: { count: config.holesLeft, size: config.holeSizeLeft },
    holes_right_spec: { count: config.holesRight, size: config.holeSizeRight },
    prepared_by: user.full_name,
    controlled_by: controllerName,
    controller_id: controllerId,
  });

  // Download handlers
  const downloadPDF = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildConfigPayload())
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
        body: JSON.stringify(buildConfigPayload())
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
        body: JSON.stringify(buildConfigPayload())
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

  const addCoverElement = (elementId) => {
    const elem = coverCatalog.find(e => e.id === elementId);
    if (!elem) return;
    setCoverElements(prev => [...prev, {
      element_id: elementId,
      x: (selectedBox.mounting_plate_x || selectedBox.internal_width) / 2,
      y: (selectedBox.mounting_plate_y || selectedBox.internal_length) / 2,
      label: '',
    }]);
  };

  const removeCoverElement = (index) => {
    setCoverElements(prev => prev.filter((_, i) => i !== index));
  };

  const updateCoverElement = (index, field, value) => {
    setCoverElements(prev => prev.map((el, i) =>
      i === index ? { ...el, [field]: field === 'x' || field === 'y' ? parseFloat(value) || 0 : value } : el
    ));
  };

  // Order management
  const loadOrders = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/orders`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setOrders(data.orders || []);
      }
    } catch (e) { /* ignore */ }
  }, [token]);

  const saveOrder = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          box_id: selectedBoxId,
          terminals: config.terminals,
          holes_top: config.holesTop,
          holes_bottom: config.holesBottom,
          holes_left: config.holesLeft,
          holes_right: config.holesRight,
        }),
      });
      if (res.ok) {
        await loadOrders();
        alert('Siparis kaydedildi');
      }
    } catch (e) {
      alert('Siparis kaydedilemedi');
    }
  };

  const loadOrderConfig = (order) => {
    setSelectedBoxId(order.box_id);
    setConfig({
      terminals: order.terminals,
      holesTop: order.holes_top,
      holesBottom: order.holes_bottom,
      holesLeft: order.holes_left,
      holesRight: order.holes_right,
      holeSizeTop: 'M20',
      holeSizeBottom: 'M20',
      holeSizeLeft: 'M20',
      holeSizeRight: 'M20',
    });
    setShowOrders(false);
  };

  const downloadLabel = async () => {
    try {
      const res = await fetch(`${API_BASE}/generate/label`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ box_id: selectedBoxId }),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `LABEL-${selectedBoxId.toUpperCase()}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      alert('Etiket olusturulamadi');
    }
  };

  const totalHoles = config.holesTop + config.holesBottom + config.holesLeft + config.holesRight;

  // BOM data
  const bomItems = [
    { name: `${selectedBox.name} Enclosure`, code: `P+F-${selectedBox.id.toUpperCase()}`, qty: 1 },
    { name: 'NS 35 DIN Rail', code: 'NS35-DIN', qty: selectedBox.rail_count },
    { name: 'UT 2,5 Terminal Block', code: 'PHX-UT2.5', qty: config.terminals },
    { name: 'M20 Cable Gland', code: 'M20-GL', qty: totalHoles },
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

  // Save Config Handler
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
          <span className="toolbar-user">{user.full_name}</span>
          <button className="toolbar-btn" onClick={logout} title="Cikis Yap">
            <LogOut size={16} />
          </button>
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
          <button
            className="toolbar-btn"
            onClick={downloadLabel}
            disabled={!validation.is_valid}
          >
            <FileText size={16} />
            Etiket
          </button>
          <div style={{borderLeft:'1px solid #555',height:24,margin:'0 4px'}} />
          <button
            className="toolbar-btn"
            onClick={saveOrder}
            disabled={!validation.is_valid}
          >
            <Plus size={16} />
            Kaydet
          </button>
          <button
            className="toolbar-btn"
            onClick={() => { loadOrders(); setShowOrders(!showOrders); }}
          >
            <Info size={16} />
            Gecmis
          </button>
        </div>
      </header>

      {/* Orders Panel */}
      {showOrders && (
        <div style={{
          position:'absolute', top:52, right:12, zIndex:50,
          background:'#1e293b', border:'1px solid #334155',
          borderRadius:8, padding:12, width:360, maxHeight:400, overflowY:'auto',
          boxShadow:'0 4px 12px rgba(0,0,0,0.3)'
        }}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
            <span style={{fontWeight:600,color:'#e2e8f0'}}>Gecmis Siparisler</span>
            <button onClick={() => setShowOrders(false)} style={{background:'none',border:'none',color:'#94a3b8',cursor:'pointer'}}>X</button>
          </div>
          {orders.length === 0 ? (
            <p style={{color:'#94a3b8',fontSize:13}}>Henuz siparis yok.</p>
          ) : (
            orders.map((o) => (
              <div key={o.id} onClick={() => loadOrderConfig(o)}
                style={{
                  padding:8, marginBottom:6, background:'#0f172a', borderRadius:6,
                  cursor:'pointer', border:'1px solid #334155',
                }}>
                <div style={{fontWeight:500,color:'#e2e8f0',fontSize:13}}>{o.drawing_number}</div>
                <div style={{color:'#94a3b8',fontSize:11}}>
                  {o.box_id.toUpperCase()} | {o.terminals}T | {o.holes_top+o.holes_bottom+o.holes_left+o.holes_right}H | {o.created_at.split('T')[0]}
                </div>
              </div>
            ))
          )}
        </div>
      )}

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

          {/* Cable Entries */}
          <div className="config-section">
            <div className="config-section-title">
              <Layers size={12} />
              Cable Entries
            </div>
            <div className="holes-grid">
              {[
                { field: 'holesTop', sizeField: 'holeSizeTop', label: 'Top', max: selectedBox.max_holes_long },
                { field: 'holesBottom', sizeField: 'holeSizeBottom', label: 'Bottom', max: selectedBox.max_holes_long },
                { field: 'holesLeft', sizeField: 'holeSizeLeft', label: 'Left', max: selectedBox.max_holes_short },
                { field: 'holesRight', sizeField: 'holeSizeRight', label: 'Right', max: selectedBox.max_holes_short },
              ].map(({ field, sizeField, label, max }) => (
                <div key={field} className="hole-input-wrapper">
                  <div className="form-label">
                    <span>{label}</span>
                    <span className="form-label-value">max {max}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <input
                      type="number"
                      className="form-input"
                      style={{ flex: 1 }}
                      value={config[field]}
                      onChange={(e) => handleInputChange(field, e.target.value)}
                      min="0"
                      max={max}
                    />
                    <select
                      className="form-select"
                      style={{ width: '72px', fontSize: '11px', padding: '4px' }}
                      value={config[sizeField]}
                      onChange={(e) => setConfig(prev => ({ ...prev, [sizeField]: e.target.value }))}
                    >
                      {Object.keys(holeSizes).length > 0
                        ? Object.keys(holeSizes).map(size => (
                            <option key={size} value={size}>{size}</option>
                          ))
                        : ['M20', 'M25', 'M32', 'M40', 'M50'].map(size => (
                            <option key={size} value={size}>{size}</option>
                          ))
                      }
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Controller Selection */}
          <div className="config-section">
            <div className="config-section-title">
              <Info size={12} />
              Kontrol Eden
            </div>
            <div className="form-group">
              <select
                className="form-select"
                value={controllerId || ''}
                onChange={(e) => setControllerId(e.target.value ? parseInt(e.target.value) : null)}
              >
                <option value="">Secilmedi</option>
                {userList.filter(u => u.id !== user.id).map(u => (
                  <option key={u.id} value={u.id}>{u.full_name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Cover Elements */}
          <div className="config-section">
            <div className="config-section-title">
              <Circle size={12} />
              Kapak Elemanlari
            </div>
            <div className="form-group">
              <div style={{ display: 'flex', gap: '4px' }}>
                <select
                  className="form-select"
                  style={{ flex: 1 }}
                  id="cover-element-select"
                  defaultValue=""
                >
                  <option value="" disabled>Eleman sec...</option>
                  {coverCatalog.map(elem => (
                    <option key={elem.id} value={elem.id}>{elem.name}</option>
                  ))}
                </select>
                <button
                  className="number-btn"
                  style={{ padding: '4px 8px' }}
                  onClick={() => {
                    const sel = document.getElementById('cover-element-select');
                    if (sel.value) {
                      addCoverElement(sel.value);
                      sel.value = '';
                    }
                  }}
                >
                  <Plus size={14} />
                </button>
              </div>
            </div>
            {coverElements.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '8px' }}>
                {coverElements.map((ce, i) => {
                  const elem = coverCatalog.find(e => e.id === ce.element_id);
                  return (
                    <div key={i} style={{ padding: '6px', background: '#f8f9fa', borderRadius: '4px', fontSize: '11px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 500 }}>{elem?.name || ce.element_id}</span>
                        <button
                          className="number-btn"
                          style={{ padding: '2px 4px', color: '#ef4444' }}
                          onClick={() => removeCoverElement(i)}
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                      <div style={{ display: 'flex', gap: '4px' }}>
                        <div style={{ flex: 1 }}>
                          <span style={{ fontSize: '10px', color: '#64748b' }}>X (mm)</span>
                          <input
                            type="number"
                            className="form-input"
                            style={{ fontSize: '11px', padding: '2px 4px' }}
                            value={ce.x}
                            onChange={(e) => updateCoverElement(i, 'x', e.target.value)}
                          />
                        </div>
                        <div style={{ flex: 1 }}>
                          <span style={{ fontSize: '10px', color: '#64748b' }}>Y (mm)</span>
                          <input
                            type="number"
                            className="form-input"
                            style={{ fontSize: '11px', padding: '2px 4px' }}
                            value={ce.y}
                            onChange={(e) => updateCoverElement(i, 'y', e.target.value)}
                          />
                        </div>
                        <div style={{ flex: 1 }}>
                          <span style={{ fontSize: '10px', color: '#64748b' }}>Etiket</span>
                          <input
                            type="text"
                            className="form-input"
                            style={{ fontSize: '11px', padding: '2px 4px' }}
                            value={ce.label}
                            placeholder="S1"
                            onChange={(e) => updateCoverElement(i, 'label', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
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
                  <tr key={i}>
                    <td>{item.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '10px' }}>{item.code}</td>
                    <td>{item.qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
                <div className="drawing-info-label">Hazirlayan</div>
                <div className="drawing-info-value">{user.full_name}</div>
              </div>
              <div className="drawing-info-item">
                <div className="drawing-info-label">Kontrol Eden</div>
                <div className="drawing-info-value">{controllerName || '-'}</div>
              </div>
              <div className="drawing-info-item">
                <div className="drawing-info-label">Sheets</div>
                <div className="drawing-info-value">4</div>
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
    </div>
  );
}

export default App;
