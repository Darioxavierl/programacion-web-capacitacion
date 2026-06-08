# Aplicación Web: Simulador de Cobertura Radioeléctrica

## 1. Identificación del proyecto

**Nombre del proyecto:** Simulador Web de Cobertura Radioeléctrica  
**Área de aplicación:** Telecomunicaciones  
**Tipo de sistema:** Aplicación web con frontend, backend y base de datos  
**Autor:** Dario Portilla  
**Tecnologías principales:** React, JavaScript, Python, FastAPI, PostgreSQL, Docker, OpenStreetMap

## 2. Descripción general de la aplicación

La aplicación web propuesta permite realizar una simulación básica de cobertura radioeléctrica sobre un mapa interactivo. El usuario puede iniciar sesión, ubicar una antena sobre un mapa de OpenStreetMap, ingresar parámetros técnicos y calcular una zona aproximada de cobertura dentro de un radio definido.

La versión inicial implementa el modelo **FSPL (Free Space Path Loss)**. Este modelo permite estimar la pérdida de propagación en espacio libre a partir de la frecuencia y la distancia. En esta primera entrega no se consideran altura de antena, relieve, obstáculos, edificios, vegetación ni pérdidas adicionales. La finalidad es presentar un prototipo funcional y coherente con el levantamiento de requerimientos y el diseño de base de datos realizados en las unidades anteriores.

## 3. Relación con la UF1: levantamiento de requerimientos

En la UF1 se definió como desarrollo de software una plataforma para apoyar el análisis de cobertura radioeléctrica. A partir de las historias de usuario, se identificaron funciones como crear proyectos, ubicar antenas, configurar parámetros técnicos, ejecutar simulaciones, visualizar resultados y guardar información.

La aplicación implementada responde a esos requerimientos mediante:

- Inicio de sesión de usuarios.
- Registro de usuarios.
- Ubicación de antena en mapa.
- Formulario de configuración técnica.
- Cálculo de cobertura usando FSPL.
- Visualización del resultado sobre el mapa.
- Almacenamiento de datos en base de datos.

## 4. Relación con la UF2: diseño de base de datos

La base de datos fue diseñada con un modelo relacional. Las tablas principales corresponden a las entidades identificadas en la tarea anterior:

| Entidad | Función |
|---|---|
| usuarios | Almacena los usuarios del sistema. |
| proyectos | Guarda los proyectos de simulación creados por cada usuario. |
| modelos_propagacion | Registra los modelos de propagación disponibles. |
| antenas | Guarda la ubicación y parámetros técnicos de las antenas. |
| simulaciones | Registra cada ejecución de simulación. |
| resultados | Guarda los valores obtenidos por cada simulación. |
| exportaciones | Tabla prevista para registrar archivos exportados. |

## 5. Arquitectura de la aplicación

El sistema se plantea bajo una arquitectura de tres capas:

### 5.1 Capa de presentación

Corresponde al frontend desarrollado con **React + JavaScript**. Esta capa se ejecuta en el navegador del usuario y permite interactuar con el sistema mediante formularios, botones, mapa y paneles de resultados.

Componentes principales:

- Pantalla de login.
- Pantalla de registro.
- Panel lateral de configuración.
- Mapa interactivo con OpenStreetMap.
- Visualización GeoJSON de cobertura.

### 5.2 Capa de aplicación o lógica de negocio

Corresponde al backend desarrollado con **Python + FastAPI**. Esta capa recibe las peticiones HTTP del frontend, valida datos, autentica usuarios, calcula la cobertura y se comunica con la base de datos.

Componentes principales:

- API REST.
- Autenticación con JWT.
- Validación de datos con Pydantic.
- Cálculo FSPL.
- Conexión a PostgreSQL con SQLAlchemy.

### 5.3 Capa de datos

Corresponde a la base de datos **PostgreSQL**. Su función es almacenar de forma persistente la información de usuarios, proyectos, antenas, simulaciones y resultados.

## 6. Funcionalidades del sistema

### 6.1 Login

El sistema incluye autenticación mediante correo y contraseña. Al iniciar sesión correctamente, el backend entrega un token JWT que el frontend utiliza para consultar los servicios protegidos.

Usuario demo:

- Correo: `admin@cobertura.local`
- Contraseña: `admin123`

### 6.2 Registro de usuario

El usuario puede crear una cuenta con nombre, correo y contraseña. La contraseña se almacena cifrada mediante bcrypt.

### 6.3 Mapa interactivo

El mapa se basa en OpenStreetMap y Leaflet. El usuario puede hacer clic en el mapa para ubicar la antena. La latitud y longitud seleccionadas se muestran en el panel de configuración.

### 6.4 Formulario técnico de antena

El formulario permite ingresar:

- Nombre del proyecto.
- Nombre de antena.
- Frecuencia en MHz.
- Potencia de transmisión en dBm.
- Ganancia de antena en dBi.
- Radio de simulación en km.
- Resolución en metros.
- Umbral de cobertura en dBm.

### 6.5 Cálculo de cobertura FSPL

El backend calcula la pérdida en espacio libre mediante:

```text
FSPL(dB) = 32.44 + 20 log10(d_km) + 20 log10(f_MHz)
```

Después estima la potencia recibida:

```text
Prx(dBm) = Ptx(dBm) + Gtx(dBi) - FSPL(dB)
```

Con estos valores se genera un conjunto de anillos de cobertura que se muestran en el mapa.

### 6.6 Visualización de resultados

El resultado se presenta mediante polígonos GeoJSON sobre el mapa. Cada anillo representa un nivel aproximado de potencia recibida. Además, el panel lateral muestra:

- Potencia promedio estimada.
- Potencia mínima estimada.
- Porcentaje aproximado de cobertura.
- Tiempo de ejecución.
- Observación técnica del modelo.

### 6.7 Persistencia en base de datos

Cada simulación guarda información en las tablas de proyectos, antenas, simulaciones y resultados. Esto permite mantener un registro histórico de las pruebas realizadas.

## 7. Base de datos implementada

### 7.1 Tabla usuarios

Campos principales:

- `usuario_id` como llave primaria.
- `nombre`.
- `correo`.
- `hashed_password`.
- `rol`.
- `estado`.
- `fecha_registro`.

### 7.2 Tabla proyectos

Campos principales:

- `proyecto_id` como llave primaria.
- `usuario_id` como llave foránea.
- `nombre_proyecto`.
- `descripcion`.
- `ciudad`.
- `fecha_creacion`.
- `estado`.

### 7.3 Tabla modelos_propagacion

Campos principales:

- `modelo_id` como llave primaria.
- `nombre_modelo`.
- `tipo_entorno`.
- `freq_min_mhz`.
- `freq_max_mhz`.
- `descripcion`.

### 7.4 Tabla antenas

Campos principales:

- `antena_id` como llave primaria.
- `proyecto_id` como llave foránea.
- `nombre_antena`.
- `latitud`.
- `longitud`.
- `frecuencia_mhz`.
- `potencia_dbm`.
- `ganancia_dbi`.
- `altura_m`.
- `azimut_grados`.
- `tecnologia`.

En esta versión, `altura_m` y `azimut_grados` quedan preparados para versiones futuras, pero no intervienen en el cálculo FSPL.

### 7.5 Tabla simulaciones

Campos principales:

- `simulacion_id` como llave primaria.
- `proyecto_id` como llave foránea.
- `modelo_id` como llave foránea.
- `nombre_simulacion`.
- `radio_km`.
- `resolucion_m`.
- `threshold_dbm`.
- `fecha_ejecucion`.
- `estado`.

### 7.6 Tabla resultados

Campos principales:

- `resultado_id` como llave primaria.
- `simulacion_id` como llave foránea.
- `antena_id` como llave foránea.
- `rsrp_promedio_dbm`.
- `rsrp_min_dbm`.
- `cobertura_porcentaje`.
- `tiempo_ejecucion_s`.
- `observacion`.

### 7.7 Tabla exportaciones

Campos principales:

- `exportacion_id` como llave primaria.
- `simulacion_id` como llave foránea.
- `formato`.
- `nombre_archivo`.
- `fecha_exportacion`.
- `disponible`.

## 8. Relaciones entre tablas

| Relación | Tipo | Descripción |
|---|---|---|
| usuarios → proyectos | 1 a muchos | Un usuario puede crear varios proyectos. |
| proyectos → antenas | 1 a muchos | Un proyecto puede tener varias antenas. |
| proyectos → simulaciones | 1 a muchos | Un proyecto puede tener varias simulaciones. |
| modelos_propagacion → simulaciones | 1 a muchos | Un modelo puede ser utilizado por varias simulaciones. |
| simulaciones → resultados | 1 a muchos | Una simulación puede generar varios resultados. |
| antenas → resultados | 1 a muchos | Una antena puede estar asociada a varios resultados. |
| simulaciones → exportaciones | 1 a muchos | Una simulación puede tener varios archivos exportados. |

## 9. Seguridad considerada

La seguridad básica del sistema se implementa mediante:

- Autenticación por correo y contraseña.
- Cifrado de contraseña con bcrypt.
- Tokens JWT para proteger endpoints.
- Validación de datos de entrada.
- Separación de permisos inicial por rol de usuario.
- Variables de entorno para credenciales y clave secreta.

## 10. Dockerización

La aplicación se entrega dockerizada mediante `docker-compose.yml`. Se levantan tres servicios:

| Servicio | Descripción | Puerto |
|---|---|---|
| frontend | Interfaz React | 5173 |
| backend | API FastAPI | 8000 |
| db | Base de datos PostgreSQL | 5432 |

Para ejecutar:

```bash
docker compose up --build
```

## 11. Alcance actual

La versión entregada cumple con el objetivo académico de elaborar una aplicación web funcional con frontend, backend, login, base de datos y cálculo técnico básico.

El cálculo FSPL se considera una primera aproximación. No se debe interpretar como una simulación profesional completa de cobertura, ya que no incluye factores reales como terreno, edificaciones, difracción, reflexión, pérdidas por clutter, altura de antenas ni modelos empíricos más avanzados.

## 12. Mejoras futuras

- Agregar modelos Okumura-Hata, COST-231 Hata y 3GPP TR 38.901.
- Incorporar datos de elevación del terreno.
- Exportar mapas en PNG, KML y CSV.
- Crear administración completa de usuarios.
- Añadir gestión de múltiples antenas por proyecto.
- Implementar comparación de escenarios.
- Mejorar el mapa de cobertura con interpolación tipo heatmap.
