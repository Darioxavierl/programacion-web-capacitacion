# Simulador Web de Cobertura Radioeléctrica

Aplicación web desarrollada como proyecto final de la Unidad Formativa 3, basada en el levantamiento de requerimientos de la UF1 y el diseño de base de datos de la UF2.

## Descripción general

El sistema permite a un usuario autenticado ubicar una antena sobre un mapa de OpenStreetMap y calcular una cobertura radioeléctrica inicial dentro de un radio definido. En esta primera versión se utiliza únicamente el modelo **FSPL (Free Space Path Loss)**, sin considerar altura de antena, relieve, obstáculos, clutter urbano ni pérdidas adicionales.

La aplicación está organizada en tres capas:

1. **Frontend:** interfaz web en React + JavaScript con mapa interactivo.
2. **Backend:** API REST en Python con FastAPI para autenticación, lógica de negocio y cálculo FSPL.
3. **Base de datos:** PostgreSQL para almacenar usuarios, proyectos, antenas, simulaciones, modelos y resultados.

## Funcionalidades implementadas

- Login con token JWT.
- Registro de usuarios.
- Usuario demo creado automáticamente.
- Mapa interactivo con OpenStreetMap.
- Selección de ubicación de antena mediante clic en el mapa.
- Formulario de parámetros técnicos: frecuencia, potencia, ganancia, radio, resolución y umbral.
- Cálculo de pérdida por espacio libre FSPL.
- Estimación de potencia recibida en dBm.
- Visualización de cobertura mediante anillos GeoJSON sobre el mapa.
- Persistencia de proyectos, antenas, simulaciones y resultados en PostgreSQL.
- Despliegue con Docker Compose.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Frontend | React, Vite, JavaScript, React Leaflet |
| Mapa | OpenStreetMap + Leaflet |
| Backend | Python, FastAPI, SQLAlchemy |
| Base de datos | PostgreSQL |
| Autenticación | JWT + passlib/bcrypt |
| Contenedores | Docker y Docker Compose |

## Ejecución

Desde la raíz del proyecto:

```bash
docker compose up --build
```

Servicios:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Usuario demo:

- Correo: `admin@cobertura.local`
- Contraseña: `admin123`

## Estructura del proyecto

```text
radio_coverage_web_app/
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── coverage.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── Dockerfile
│   ├── index.html
│   └── package.json
├── docs/
│   └── APLICACION_WEB_COBERTURA_RADIOELECTRICA.md
├── docker-compose.yml
└── README.md
```

## Modelo FSPL utilizado

El backend calcula la pérdida por espacio libre con:

```text
FSPL(dB) = 32.44 + 20 log10(d_km) + 20 log10(f_MHz)
```

Luego estima la potencia recibida:

```text
Prx(dBm) = Ptx(dBm) + Gtx(dBi) - FSPL(dB)
```

## Alcance y limitaciones

Esta versión es funcional como prototipo académico. No debe utilizarse como herramienta definitiva de ingeniería de red porque no considera:

- Altura de antena.
- Perfil del terreno.
- Pérdidas por obstáculos.
- Patrón real de radiación.
- Clutter urbano.
- Modelos empíricos como Okumura-Hata, COST-231 o 3GPP TR 38.901.

## Mejoras futuras

- Incorporar modelos Okumura-Hata, COST-231 y 3GPP.
- Cargar DEM o datos de terreno.
- Exportar resultados en CSV, KML y PNG.

---

## Guía de inicio rápido (Windows)

### Requisitos

| Requisito | Versión mínima | Descarga |
|---|---|---|
| **Docker Desktop** | 4.x | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| **Windows** | 10 64-bit (build 19041) o Windows 11 | — |
| **WSL2** | habilitado automáticamente por Docker Desktop | — |

> Docker Desktop instala Docker Engine y Docker Compose v2 juntos. No se necesita nada más.

### Pasos

**1. Clonar o descomprimir el proyecto** en una carpeta local, por ejemplo `D:\Proyectos\capacitacion`.

**2. Abrir PowerShell o la terminal integrada de VS Code** y navegar a la raíz del proyecto (donde está `docker-compose.yml`):

```powershell
cd D:\Proyectos\capacitacion
```

**3. Construir las imágenes y levantar los servicios** (primera vez):

```powershell
docker compose up --build
```

Docker descargará las imágenes base, instalará dependencias y arrancará los tres servicios. Espera a ver en los logs:

```
cobertura_backend   | INFO:     Application startup complete.
cobertura_frontend  |   VITE ready in ...
```

**4. Abrir la aplicación** en el navegador:

- **App web:** <http://localhost:5173>
- **API (Swagger):** <http://localhost:8000/docs>

**5. Iniciar sesión** con el usuario demo:

```
Correo:    admin@cobertura.local
Contraseña: admin123
```

### Comandos habituales

```powershell
# Iniciar sin reconstruir (después de la primera vez)
docker compose up

# Iniciar en segundo plano
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Ver logs solo del backend
docker compose logs -f backend

# Detener los servicios
docker compose down

# Detener y borrar la base de datos (volumen)
docker compose down -v
```

### Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Error: port is already allocated` | El puerto 5173, 8000 o 5432 está en uso | Cerrar la aplicación que usa ese puerto, o cambiar el puerto en `docker-compose.yml` |
| Backend no arranca, error `bcrypt` | Conflicto de versión de `bcrypt` | Verificar que `requirements.txt` incluya `bcrypt==3.2.2` y reconstruir con `--build` |
| `Cannot connect to the Docker daemon` | Docker Desktop no está ejecutándose | Abrir Docker Desktop desde el menú Inicio y esperar a que el icono de la bandeja aparezca en verde |
- Añadir gestión completa de proyectos.
- Añadir roles diferenciados de administrador, técnico y estudiante.
- Mejorar visualización como mapa de calor real.
