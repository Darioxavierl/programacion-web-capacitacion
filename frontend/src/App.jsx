import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, GeoJSON, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { apiFetch, clearToken, getToken, login, register } from './api.js';

const antennaIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function MapClickHandler({ onPick }) {
  useMapEvents({
    click(event) {
      onPick(event.latlng.lat, event.latlng.lng);
    },
  });
  return null;
}

function LoginView({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ nombre: 'Dario Portilla', correo: 'admin@cobertura.local', password: 'admin123' });
  const [error, setError] = useState('');
  const update = (key, value) => setForm((old) => ({ ...old, [key]: value }));

  async function submit(event) {
    event.preventDefault();
    setError('');
    try {
      if (mode === 'register') {
        await register({ nombre: form.nombre, correo: form.correo, password: form.password, rol: 'Tecnico' });
      }
      await login(form.correo, form.password);
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <h1>Simulador Web de Cobertura Radioeléctrica</h1>
        <p>Ingrese con el usuario demo o registre una cuenta para guardar proyectos y simulaciones.</p>
        <form onSubmit={submit}>
          {mode === 'register' && (
            <label>Nombre completo
              <input value={form.nombre} onChange={(e) => update('nombre', e.target.value)} />
            </label>
          )}
          <label>Correo
            <input type="email" value={form.correo} onChange={(e) => update('correo', e.target.value)} />
          </label>
          <label>Contraseña
            <input type="password" value={form.password} onChange={(e) => update('password', e.target.value)} />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit">{mode === 'login' ? 'Iniciar sesión' : 'Registrar e ingresar'}</button>
          <button type="button" className="link-button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            {mode === 'login' ? 'Crear una cuenta nueva' : 'Volver al login'}
          </button>
        </form>
        <small>Usuario demo: admin@cobertura.local / admin123</small>
      </section>
    </main>
  );
}

function Dashboard({ onLogout }) {
  const defaultPosition = [-2.90055, -79.00453];
  const [user, setUser] = useState(null);
  const [position, setPosition] = useState(defaultPosition);
  const [coverage, setCoverage] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    nombre_proyecto: 'Cobertura Campus Central',
    ciudad: 'Cuenca',
    nombre_antena: 'Nodo FSPL Demo',
    frecuencia_mhz: 3500,
    potencia_dbm: 43,
    ganancia_dbi: 15,
    radio_km: 3,
    resolucion_m: 250,
    threshold_dbm: -100,
    tecnologia: '5G NR',
  });

  useEffect(() => {
    apiFetch('/api/users/me').then(setUser).catch(() => null);
  }, []);

  const update = (key, value) => setForm((old) => ({ ...old, [key]: value }));

  const geoJsonStyle = (feature) => {
    const c = feature.properties.coverage_class;
    const palette = {
      excelente: '#1565c0',
      buena: '#00acc1',
      limite: '#f9a825',
      fuera_de_cobertura: '#c62828',
    };
    return {
      color: palette[c] || '#5c6bc0',
      weight: 1,
      fillColor: palette[c] || '#5c6bc0',
      fillOpacity: 0.35,
    };
  };

  async function calculate(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...form,
        latitud: position[0],
        longitud: position[1],
        frecuencia_mhz: Number(form.frecuencia_mhz),
        potencia_dbm: Number(form.potencia_dbm),
        ganancia_dbi: Number(form.ganancia_dbi),
        radio_km: Number(form.radio_km),
        resolucion_m: Number(form.resolucion_m),
        threshold_dbm: Number(form.threshold_dbm),
      };
      const data = await apiFetch('/api/coverage/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      setCoverage(data.geojson);
      setSummary(data.resumen);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearToken();
    onLogout();
  }

  const geoJsonKey = useMemo(() => JSON.stringify(coverage || {}).length + String(Date.now()), [coverage]);

  return (
    <main className="app-layout">
      <aside className="sidebar">
        <header>
          <h1>Cobertura Radioeléctrica</h1>
          <p>Modelo inicial: FSPL sin altura ni relieve.</p>
          {user && <small>Sesión: {user.nombre} ({user.rol})</small>}
        </header>

        <form className="coverage-form" onSubmit={calculate}>
          <label>Proyecto
            <input value={form.nombre_proyecto} onChange={(e) => update('nombre_proyecto', e.target.value)} />
          </label>
          <label>Nombre de antena
            <input value={form.nombre_antena} onChange={(e) => update('nombre_antena', e.target.value)} />
          </label>
          <div className="grid-2">
            <label>Frecuencia (MHz)
              <input type="number" value={form.frecuencia_mhz} onChange={(e) => update('frecuencia_mhz', e.target.value)} />
            </label>
            <label>Potencia (dBm)
              <input type="number" value={form.potencia_dbm} onChange={(e) => update('potencia_dbm', e.target.value)} />
            </label>
          </div>
          <div className="grid-2">
            <label>Ganancia (dBi)
              <input type="number" value={form.ganancia_dbi} onChange={(e) => update('ganancia_dbi', e.target.value)} />
            </label>
            <label>Radio (km)
              <input type="number" min="0.1" step="0.1" value={form.radio_km} onChange={(e) => update('radio_km', e.target.value)} />
            </label>
          </div>
          <div className="grid-2">
            <label>Resolución (m)
              <input type="number" value={form.resolucion_m} onChange={(e) => update('resolucion_m', e.target.value)} />
            </label>
            <label>Umbral (dBm)
              <input type="number" value={form.threshold_dbm} onChange={(e) => update('threshold_dbm', e.target.value)} />
            </label>
          </div>
          <p className="coords">Antena: {position[0].toFixed(6)}, {position[1].toFixed(6)}</p>
          <button disabled={loading}>{loading ? 'Calculando...' : 'Calcular cobertura FSPL'}</button>
          {error && <p className="error">{error}</p>}
        </form>

        {summary && (
          <section className="summary">
            <h2>Resultado</h2>
            <p><strong>RSRP promedio:</strong> {summary.rsrp_promedio_dbm} dBm</p>
            <p><strong>RSRP mínimo:</strong> {summary.rsrp_min_dbm} dBm</p>
            <p><strong>Cobertura:</strong> {summary.cobertura_porcentaje}%</p>
            <p><strong>Tiempo:</strong> {summary.tiempo_ejecucion_s}s</p>
            <small>{summary.nota}</small>
          </section>
        )}

        <button className="logout" onClick={logout}>Cerrar sesión</button>
      </aside>

      <section className="map-panel">
        <MapContainer center={position} zoom={13} className="map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapClickHandler onPick={(lat, lng) => setPosition([lat, lng])} />
          <Marker position={position} icon={antennaIcon} />
          {coverage && <GeoJSON key={geoJsonKey} data={coverage} style={geoJsonStyle} />}
        </MapContainer>
        <div className="map-help">Haz clic en el mapa para ubicar la antena.</div>
        <div className="map-legend">
          <span className="legend-item"><i style={{ background: '#1565c0' }} />Excelente</span>
          <span className="legend-item"><i style={{ background: '#00acc1' }} />Buena</span>
          <span className="legend-item"><i style={{ background: '#f9a825' }} />Límite</span>
          <span className="legend-item"><i style={{ background: '#c62828' }} />Sin cobertura</span>
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  return authenticated ? <Dashboard onLogout={() => setAuthenticated(false)} /> : <LoginView onLogin={() => setAuthenticated(true)} />;
}
