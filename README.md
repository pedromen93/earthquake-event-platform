# Earthquake Event Platform

Plataforma para procesar eventos sismicos consumidos desde la API publica de USGS, persistirlos en MongoDB, exponer consultas mediante FastAPI y generar reportes horarios con Airflow.

## Alcance

La solucion incluye:

- API REST con `FastAPI`
- persistencia en `MongoDB`
- ingesta periodica desacoplada como worker independiente
- metricas horarias near real-time
- reportes horarios consolidados
- orquestacion horaria con `Airflow`
- ejecucion completa mediante `Docker Compose`

## Arquitectura

- enfoque inspirado en `Clean Architecture`
- separacion entre `presentation`, `application`, `domain`, `infrastructure`, `workers` y `airflow`
- casos de uso desacoplados de FastAPI, MongoDB y Airflow
- repositorios sin reglas de negocio
- servicios de dominio para agregacion y consolidacion

Documento y diagrama:

- [architecture.md](file:///c:/PEDRO/PruebaTecnica/docs/architecture.md)
- [websocket.md](file:///c:/PEDRO/PruebaTecnica/docs/websocket.md)

## Propuesta 8.4

La implementacion actual cubre la capa transaccional y operativa end-to-end. Para el punto `8.4` del enunciado, la solucion queda preparada para evolucionar hacia una arquitectura de datos orientada a analitica avanzada y Machine Learning sin modificar el dominio actual.

### Estado actual

- `MongoDB` funciona como capa transaccional u operacional para eventos, metricas y reportes
- `FastAPI` expone consulta operacional y el stream WebSocket de sismos
- `ingestion-worker` procesa eventos near real-time
- `Airflow` ya existe como punto de orquestacion para procesos analiticos futuros
- `hourly_metrics` y `hourly_reports` funcionan como primeros agregados historicos

### Arquitectura objetivo propuesta

- **Capa transaccional**: `MongoDB` sigue almacenando eventos, metricas y reportes operativos
- **Capa de extraccion**: `Airflow` orquesta jobs incrementales para exportar datos desde la capa transaccional
- **Data lake / raw zone**: almacenamiento de eventos historicos en archivos `Parquet` particionados por fecha y hora
- **Curated zone / feature layer**: datasets limpios y agregados para entrenamiento de modelos y analitica historica
- **Serving analitico**: capa optimizada para dashboards y consultas historicas, separada de la base operacional
- **Tiempo real**: el WebSocket actual alimenta dashboards operativos near real-time y puede convivir con una capa futura de mensajeria

### Cobertura esperada del punto 8.4

- **Dashboards historicos para tendencias**:
  - hoy: base parcial con `hourly_metrics` y `hourly_reports`
  - futuro: consumo desde una capa analitica o datasets `Parquet`
- **Dashboards en tiempo real**:
  - hoy: base funcional con `WS /api/v1/stream/earthquakes`
  - futuro: UI conectada al stream para visualizacion continua
- **Datasets analiticos para Machine Learning**:
  - futuro: jobs en `Airflow` para generar datasets curados y versionados
- **Procesamiento de Parquet near real-time**:
  - futuro: exportaciones incrementales a particiones por `year/month/day/hour`
- **Separacion transaccional y analitica**:
  - hoy: definida arquitectonicamente
  - futuro: materializada con una capa analitica separada
- **Almacenamiento historico de gran volumen**:
  - futuro: conservacion de historico en almacenamiento barato y particionado

### Decision de alcance

Esta propuesta se documenta como evolucion futura deliberada. El objetivo de la implementacion actual fue cerrar primero la capa operacional con calidad de produccion, dejando preparada la extension hacia analitica y ML.

## Endpoints

### Minimos requeridos

- `GET /api/v1/earthquakes`
- `GET /api/v1/metrics`
- `GET /api/v1/reports`

### Operativos

- `POST /api/v1/operations/ingestions/run`
- `GET /api/v1/health`
- `WS /api/v1/stream/earthquakes`

## Requisitos Previos

Para la forma recomendada de ejecucion necesitas:

- `Docker Desktop` funcionando
- `Docker Compose` disponible

Para desarrollo local sin Docker completo:

- `Python 3.12`
- `pip`
- al menos `MongoDB` levantado, idealmente usando el mismo `docker compose`

## Inicio Rapido Con Docker

Esta es la forma recomendada para levantar toda la solucion de inicio a fin.

### 1. Preparar variables de entorno

Desde la raiz del proyecto:

```powershell
copy .env.example .env
```

El archivo `.env` es necesario porque:

- centraliza la configuracion sin hardcodear valores en el codigo
- permite cambiar puertos, conexion a MongoDB, fuente externa y credenciales de Airflow sin editar Python
- lo consume tanto la aplicacion como `docker compose`

Si no necesitas cambios, puedes usar los valores por defecto del archivo `.env.example`.

Variables minimas que conviene revisar antes de levantar el stack:

- `APP_PORT`: puerto publicado para la API y el WebSocket
- `MONGODB_URI`: cadena de conexion que usaran la API y el worker
- `INGESTION_INTERVAL_SECONDS`: cada cuantos segundos corre la ingesta automatica
- `AIRFLOW_WEBSERVER_PORT`: puerto publicado para la interfaz web de Airflow
- `AIRFLOW_ADMIN_USERNAME` y `AIRFLOW_ADMIN_PASSWORD`: credenciales iniciales de acceso a Airflow

### 2. Construir e iniciar todos los servicios

```powershell
docker compose up -d --build
```

Servicios incluidos:

- `mongodb`
- `api`
- `ingestion-worker`
- `airflow-postgres`
- `airflow-init`
- `airflow-webserver`
- `airflow-scheduler`

### 3. Verificar el estado de los contenedores

```powershell
docker compose ps -a
```

Estado esperado:

- `earthquake-api` en `Up (healthy)`
- `earthquake-mongodb` en `Up (healthy)`
- `earthquake-ingestion-worker` en `Up`
- `earthquake-airflow-webserver` en `Up`
- `earthquake-airflow-scheduler` en `Up`
- `earthquake-airflow-init` en `Exited (0)` y eso es correcto

### 4. Validar la API

Health check:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' | ConvertTo-Json -Depth 5"
```

Swagger:

- [http://localhost:8000/docs](http://localhost:8000/docs)

Respuesta esperada del health:

```json
{
  "status": "ok",
  "service": "Earthquake Event Platform",
  "environment": "local"
}
```

### 5. Forzar una ingesta manual

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Method POST -Uri 'http://localhost:8000/api/v1/operations/ingestions/run' | ConvertTo-Json -Depth 8"
```

Esto dispara un ciclo manual de ingesta desde USGS y actualiza los datos persistidos.

### 6. Consultar los endpoints principales

Sismos:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/earthquakes?page=1&page_size=5' | ConvertTo-Json -Depth 8"
```

Metricas:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/metrics?page=1&page_size=5' | ConvertTo-Json -Depth 8"
```

Reportes:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/reports?page=1&page_size=5' | ConvertTo-Json -Depth 8"
```

Nota:

- `earthquakes` debe devolver eventos si la ingesta ya corrió correctamente
- `metrics` debe devolver ventanas agregadas cuando existan eventos procesados
- `reports` puede salir vacio si todavia no se ha generado ningun reporte horario

### 6.1 Conectarse al stream WebSocket en tiempo real

La API expone un canal WebSocket para recibir eventos sismicos nuevos o recien detectados:

- `ws://localhost:8000/api/v1/stream/earthquakes`

Puedes conectarte con cualquier cliente WebSocket. El servidor envia:

- un evento `connection_established`
- un `initial_snapshot` con los eventos mas recientes
- eventos `earthquake_events` cuando aparezcan nuevos sismos
- eventos `heartbeat` para mantener vivo el canal

Guia dedicada:

- [websocket.md](file:///c:/PEDRO/PruebaTecnica/docs/websocket.md)

Ejemplo con JavaScript en navegador:

```javascript
const socket = new WebSocket("ws://localhost:8000/api/v1/stream/earthquakes");

socket.onmessage = (event) => {
  const payload = JSON.parse(event.data);
  console.log(payload);
};
```

### 7. Validar Airflow

Accesos:

- Airflow UI: [http://localhost:8080](http://localhost:8080)
- Airflow health: [http://localhost:8080/health](http://localhost:8080/health)

Credenciales por defecto:

- usuario: `admin`
- password: `admin`

Dentro de Airflow debe aparecer el DAG:

- `earthquake_hourly_reports`

### 8. Ejecutar manualmente el DAG de reportes

Si quieres generar un reporte horario sin esperar la programacion:

```powershell
docker compose exec airflow-webserver airflow dags test earthquake_hourly_reports 2026-07-02T21:00:00+00:00
```

Luego vuelve a consultar:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/reports?page=1&page_size=5' | ConvertTo-Json -Depth 8"
```

## Flujo De Validacion Recomendado

Si quieres demostrar que todo el sistema funciona, este es el recorrido sugerido:

1. Levantar el stack con `docker compose up -d --build`
2. Verificar `docker compose ps -a`
3. Validar `GET /api/v1/health`
4. Ejecutar `POST /api/v1/operations/ingestions/run`
5. Consultar `GET /api/v1/earthquakes`
6. Consultar `GET /api/v1/metrics`
7. Conectarse al `WS /api/v1/stream/earthquakes`
8. Entrar a Airflow y validar el DAG
9. Ejecutar el DAG de reportes o el runner de reportes
10. Consultar `GET /api/v1/reports`

## Desarrollo Local

Si quieres trabajar sin levantar todo el stack, puedes ejecutar solo lo necesario.

### 1. Levantar MongoDB con Docker

```powershell
docker compose up -d mongodb
```

### 2. Preparar entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
```

### 3. Ajustar el `.env` para desarrollo local

Si ejecutas la API desde tu maquina y MongoDB en Docker, normalmente necesitaras cambiar:

```env
MONGODB_URI=mongodb://localhost:27017
```

### 4. Levantar la API en local

```powershell
.\.venv\Scripts\uvicorn app.main:app --reload
```

### 5. Ejecutar el worker de ingesta

Un ciclo:

```powershell
.\.venv\Scripts\python -m app.workers.ingestion.main --once
```

Modo periodico:

```powershell
.\.venv\Scripts\python -m app.workers.ingestion.main
```

### 6. Generar reportes en local

Ultimo reporte horario cerrado:

```powershell
.\.venv\Scripts\python -m app.workers.reporting.main
```

Hora especifica:

```powershell
.\.venv\Scripts\python -m app.workers.reporting.main --report-date 2026-06-17T10:00:00+00:00
```

## Variables De Entorno

Las variables por defecto estan en `.env.example`. Debes copiar ese archivo a `.env` antes de levantar la solucion:

```powershell
copy .env.example .env
```

### Variables requeridas para un arranque normal

Estas variables deben existir en `.env` para que la solucion quede predecible y facil de mover entre entornos. Si copias `.env.example`, ya quedan definidas.

| Variable | Ejemplo | Uso |
| --- | --- | --- |
| `APP_NAME` | `Earthquake Event Platform` | Nombre visible del servicio en respuestas y logs. |
| `APP_ENV` | `local` | Identifica el entorno actual, util para logs y comportamiento por entorno. |
| `APP_DEBUG` | `true` | Activa o desactiva detalles utiles para desarrollo local. |
| `APP_HOST` | `0.0.0.0` | Host de escucha de la API dentro del contenedor o entorno local. |
| `APP_PORT` | `8000` | Puerto publicado para la API HTTP y el WebSocket. |
| `API_V1_PREFIX` | `/api/v1` | Prefijo comun de los endpoints REST y del stream. |
| `LOG_LEVEL` | `INFO` | Nivel de verbosidad del logging. |
| `LOG_JSON` | `true` | Define si los logs salen en formato estructurado JSON. |
| `MONGODB_URI` | `mongodb://mongodb:27017` | Conexion principal usada por la API, workers y procesos de reportes. |
| `MONGODB_DATABASE` | `earthquake_platform` | Base de datos de trabajo de la aplicacion. |
| `MONGODB_EARTHQUAKES_COLLECTION` | `earthquakes` | Coleccion donde se guardan los eventos sismicos. |
| `MONGODB_HOURLY_METRICS_COLLECTION` | `hourly_metrics` | Coleccion de agregados horarios calculados por la aplicacion. |
| `MONGODB_HOURLY_REPORTS_COLLECTION` | `hourly_reports` | Coleccion de reportes horarios consolidados. |
| `USGS_BASE_URL` | `https://earthquake.usgs.gov` | URL base de la fuente publica de eventos sismicos. |
| `USGS_SUMMARY_PATH` | `/earthquakes/feed/v1.0/summary/all_hour.geojson` | Feed especifico que se consulta en cada ciclo de ingesta. |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Timeout HTTP para llamadas salientes a USGS. |
| `INGESTION_INTERVAL_SECONDS` | `180` | Intervalo del worker automatico; define cada cuanto intenta traer nuevos eventos. |
| `MONGODB_PORT` | `27017` | Puerto publicado del contenedor MongoDB hacia la maquina host. |
| `AIRFLOW_WEBSERVER_PORT` | `8080` | Puerto publicado para la UI y health de Airflow. |
| `AIRFLOW_UID` | `50000` | UID usado por los contenedores de Airflow para permisos y escritura de logs. |
| `AIRFLOW_POSTGRES_USER` | `airflow` | Usuario de la base interna que usa Airflow. |
| `AIRFLOW_POSTGRES_PASSWORD` | `airflow` | Password de la base interna de Airflow. |
| `AIRFLOW_POSTGRES_DB` | `airflow` | Nombre de la base interna de Airflow. |
| `AIRFLOW_ADMIN_USERNAME` | `admin` | Usuario inicial para entrar a la UI de Airflow. |
| `AIRFLOW_ADMIN_PASSWORD` | `admin` | Password inicial para entrar a la UI de Airflow. |

### Ajustes mas comunes segun el escenario

- **Docker Compose completo**:
  - puedes dejar los valores por defecto de `.env.example`
  - `MONGODB_URI` debe seguir apuntando a `mongodb://mongodb:27017`
- **API local y MongoDB en Docker**:
  - cambia `MONGODB_URI` a `mongodb://localhost:27017`
- **Quiero que la ingesta corra mas rapido para pruebas**:
  - baja `INGESTION_INTERVAL_SECONDS`, por ejemplo a `60`
- **Quiero cambiar puertos porque tengo conflictos locales**:
  - ajusta `APP_PORT`, `MONGODB_PORT` y `AIRFLOW_WEBSERVER_PORT`

### Variable opcional del compose

- `APP_ENV_FILE`:
  - no hace falta definirla en el `.env` comun
  - solo sirve si quieres que `docker compose` cargue otro archivo distinto, por ejemplo `.env.dev` o `.env.prod`

## Postman

Coleccion lista para importar:

- [Earthquake API.postman_collection.json](file:///c:/PEDRO/PruebaTecnica/docs/postman/Earthquake%20API.postman_collection.json)

Uso sugerido:

1. Importar la coleccion
2. Definir `baseUrl = http://localhost:8000`
3. Ejecutar `Get Health`
4. Ejecutar `Run Ingestion`
5. Ejecutar `Get Earthquakes`
6. Ejecutar `Get Metrics`
7. Ejecutar `Get Reports`

Nota:

- La coleccion cubre endpoints HTTP.
- La validacion del WebSocket se documenta en [websocket.md](file:///c:/PEDRO/PruebaTecnica/docs/websocket.md).

## Pruebas

Pruebas agregadas:

- unitarias para agregacion de metricas
- unitarias para consolidacion de reportes
- unitarias para la ingesta y deduplicacion
- smoke test del endpoint de sismos

Ejecutar:

```powershell
.\.venv\Scripts\python -m pytest tests -q
```

## Troubleshooting

### El endpoint `health` no responde

- verifica `docker compose ps -a`
- revisa logs de la API:

```powershell
docker compose logs --tail=200 api
```

### `reports` sale vacio

- primero confirma que ya existan eventos y metricas
- ejecuta manualmente el DAG o el runner de reportes

### El WebSocket no conecta

- verifica que `earthquake-api` este en `Up (healthy)`
- recuerda que el stream usa el mismo puerto `8000` de la API
- reconstruye la API si agregaste o cambiaste el endpoint:

```powershell
docker compose build api
docker compose up -d api
```

### Airflow sigue usando codigo viejo

Si cambias codigo Python compartido por `airflow-webserver` y `airflow-scheduler`, reconstruye:

```powershell
docker compose build airflow-init airflow-webserver airflow-scheduler
docker compose up -d airflow-init airflow-webserver airflow-scheduler
```

### Ver logs por servicio

```powershell
docker compose logs --tail=200 api
docker compose logs --tail=200 ingestion-worker
docker compose logs --tail=200 airflow-webserver
docker compose logs --tail=200 airflow-scheduler
docker compose logs --tail=200 mongodb
```

## Detener La Solucion

Detener contenedores:

```powershell
docker compose down
```

Detener y eliminar volumenes:

```powershell
docker compose down -v
```

## Estructura Relevante

```text
app/
├─ application/
├─ domain/
├─ infrastructure/
├─ presentation/
├─ workers/
airflow/
├─ dags/
deploy/
├─ docker/
docs/
├─ architecture.md
├─ postman/
tests/
docker-compose.yml
```
