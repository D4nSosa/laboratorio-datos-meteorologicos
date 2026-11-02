# Despliegue Vercel del conector AgroClima

El frontend del Laboratorio está en `docs/`. Para publicar el sitio y la función API en el mismo proyecto Vercel:

1. Crear un proyecto Vercel conectado al repositorio `D4nSosa/laboratorio-datos-meteorologicos`.
2. Configurar **Root Directory** como `docs`.
3. Usar el branch `main` como Production Branch.
4. No configurar un comando de build; el sitio es HTML/CSS/JS estático y la función está en `docs/api/agroclima/station.js`.
5. El endpoint resultante será `https://<dominio-del-proyecto>/api/agroclima/station?id=1609`.
6. Actualizar `docs/assets/js/agroclima-config.js` con la URL absoluta del endpoint para que el frontend alojado en GitHub Pages también pueda consultarlo. La función incluye CORS para ese uso.

La función consulta exclusivamente las rutas públicas de AgroClima `/public/estacion.php` y `/3/public/estacion.php`; no acepta URLs arbitrarias. Es una consulta bajo demanda, no un proceso de polling.

## Validación antes de anunciar disponibilidad

- Confirmar que el deployment de Vercel está en estado READY.
- Consultar el endpoint con un ID conocido y comprobar `ok: true`, `station_id`, `source_url`, `fetched_at` y `html`.
- Confirmar que el HTML contiene tablas de observaciones meteorológicas que el parser del frontend pueda reconocer.
- Comparar la hora de consulta (`fetched_at`) con las marcas de tiempo de medición que publique AgroClima.

La cantidad de fichas del inventario (192) no equivale al número de estaciones con observaciones recientes. El total efectivo solo se podrá informar después de consultar las fichas y clasificar su recencia.
