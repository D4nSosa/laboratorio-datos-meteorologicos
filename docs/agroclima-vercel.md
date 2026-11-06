# Arquitectura del conector AgroClima

El Laboratorio de Datos Meteorológicos tiene **un solo frontend público**, alojado en GitHub Pages:

- Frontend: https://d4nsosa.github.io/laboratorio-datos-meteorologicos/explorador-interactivo.html
- Backend: Vercel, exclusivamente para endpoints API. No publica una segunda copia del sitio.

## Estructura

- `docs/`: frontend estático de GitHub Pages.
- `backend/api/agroclima/station.js`: función serverless que consulta AgroClima y devuelve JSON estructurado.
- El proyecto Vercel debe tener **Root Directory = backend**. Así Vercel no sirve los archivos HTML del Laboratorio.

Endpoint:
`https://laboratorio-datos-meteorologicos.vercel.app/api/agroclima/station?id=1609`

## Respuesta

La API devuelve metadatos de la estación, última observación, cantidad de registros y una serie de observaciones normalizadas. Se conserva temporalmente el HTML original para compatibilidad con la interfaz actual mientras se completa la migración del frontend a JSON.

Cada observación incluye hora local, temperatura, humedad, velocidad y dirección del viento, lluvia, presión, punto de rocío y sensación térmica. La hora de consulta (`fetched_at`) no debe confundirse con la hora de medición (`observed_at_local`).

## Validación

- Consultar una estación conocida y comprobar `ok: true`.
- Verificar que `observation_count` sea mayor que cero y que `observations` contenga registros reales.
- Comparar `latest_observation` con la última fila publicada por AgroClima.
- Si cambia el HTML de AgroClima y no se reconoce la tabla, la API devuelve un error explícito; no inventa ni estima mediciones.

La cantidad de fichas del inventario no equivale al número de estaciones con observaciones recientes.
