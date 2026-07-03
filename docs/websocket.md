# WebSocket de Sismos

## Objetivo

La API expone un canal WebSocket para recibir actualizaciones de sismos en tiempo real o near real-time sin necesidad de hacer polling HTTP desde el cliente.

Endpoint:

- `ws://localhost:8000/api/v1/stream/earthquakes`

## Mensajes Emitidos

El servidor puede enviar los siguientes eventos:

- `connection_established`: confirma que la conexion fue aceptada
- `initial_snapshot`: envia un lote inicial con los eventos mas recientes
- `earthquake_events`: envia eventos nuevos detectados despues del cursor actual del cliente
- `heartbeat`: mantiene vivo el canal cuando no hubo cambios recientes

## Validacion Rapida

### Requisitos

- stack levantado con `docker compose up -d --build`
- API disponible en `http://localhost:8000`

### 1. Validar health

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' | ConvertTo-Json -Depth 5"
```

### 2. Conectarse desde PowerShell

```powershell
$ws = [System.Net.WebSockets.ClientWebSocket]::new()
$uri = [Uri]'ws://localhost:8000/api/v1/stream/earthquakes'
$ct = [Threading.CancellationToken]::None

$ws.ConnectAsync($uri, $ct).GetAwaiter().GetResult()

$buffer = New-Object byte[] 8192
$segment = [ArraySegment[byte]]::new($buffer)

$msg1 = $ws.ReceiveAsync($segment, $ct).GetAwaiter().GetResult()
[Text.Encoding]::UTF8.GetString($buffer, 0, $msg1.Count)

$msg2 = $ws.ReceiveAsync($segment, $ct).GetAwaiter().GetResult()
[Text.Encoding]::UTF8.GetString($buffer, 0, $msg2.Count)

$ws.Dispose()
```

Resultado esperado:

- primer mensaje con `type = connection_established`
- segundo mensaje con `type = initial_snapshot`

### 3. Provocar actividad en la API

Con la conexion abierta, ejecuta una ingesta manual:

```powershell
powershell -NoProfile -Command "Invoke-RestMethod -Method POST -Uri 'http://localhost:8000/api/v1/operations/ingestions/run' | ConvertTo-Json -Depth 8"
```

Si aparecen sismos nuevos respecto al cursor actual del stream, el cliente debe recibir un evento `earthquake_events`.

## Ejemplo En Navegador

```javascript
const socket = new WebSocket("ws://localhost:8000/api/v1/stream/earthquakes");

socket.onopen = () => console.log("WebSocket conectado");

socket.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};

socket.onerror = (error) => {
  console.error("Error WebSocket:", error);
};

socket.onclose = () => {
  console.log("WebSocket cerrado");
};
```

## Consideraciones

- El stream usa el mismo puerto de la API HTTP.
- No necesita servicios adicionales en `docker-compose.yml`.
- Si actualizas el codigo de la API, reconstruye el servicio `api` para que Docker tome los cambios.

## Troubleshooting

Si no puedes conectar:

```powershell
docker compose ps -a
docker compose logs --tail=200 api
```

Si la API sigue usando una version anterior del codigo:

```powershell
docker compose build api
docker compose up -d api
```
