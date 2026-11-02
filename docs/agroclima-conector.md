# Conector de observaciones AgroClima

## Arquitectura

El sitio del Laboratorio se publica como contenido estático en GitHub Pages. Por eso no puede actuar como servidor proxy ni leer directamente el HTML de AgroClima cuando el proveedor no habilita CORS.

El Worker de `infra/agroclima-proxy/worker.js` es un intermediario de solo lectura. Acepta únicamente un ID numérico, consulta dos rutas públicas fijas de AgroClima y devuelve el HTML junto con la URL de origen y la hora de consulta. No acepta URLs arbitrarias, credenciales ni parámetros para otros hosts.

La interfaz convierte las tablas HTML devueltas en tablas de texto usando `textContent`; no inserta el HTML remoto en el DOM. Si no reconoce una tabla meteorológica, informa que no pudo extraerla y no inventa valores.

## Despliegue requerido

1. Iniciar sesión en Cloudflare desde una terminal con Wrangler (`npx wrangler login`).
2. Desde la raíz del repositorio, publicar el Worker con `npx wrangler deploy infra/agroclima-proxy/worker.js --name lnm-agroclima-proxy`.
3. Si preferís el Dashboard, crear un Worker nuevo y pegar el contenido de `infra/agroclima-proxy/worker.js`.
4. Copiar su URL pública y agregar la ruta `/api/agroclima/station`.
5. Pegar esa URL en `docs/assets/js/agroclima-config.js`, en `window.LNM_AGROCLIMA_PROXY_URL`.
6. Publicar el cambio en GitHub Pages.

No se incluye una URL ficticia ni se considera activo el conector hasta desplegar el Worker y verificar una respuesta real.

## Cobertura del catálogo

La interfaz permite seleccionar cualquier ficha del inventario local por ID, no solo la estación de ejemplo 1609. Los marcadores se dibujan únicamente cuando existen coordenadas numéricas; las estaciones sin coordenadas no se descartan y se pueden consultar desde el selector. La cobertura efectiva de la red pública debe reconciliarse con el mapa de AgroClima antes de afirmar que las 119 estaciones visibles allí están incluidas en el inventario local.

## Prueba

Abrir en el navegador:

`https://<worker>.<subdominio>.workers.dev/api/agroclima/station?id=1609`

La respuesta esperada es JSON con `ok: true`, `station_id`, `source_url`, `fetched_at` y `html`. Un error 502 indica que AgroClima no entregó una ficha accesible al Worker.

El mapa carga el inventario local de estaciones al iniciar. Las estaciones con coordenadas aparecen como marcadores al activar la capa AgroClima; todas las fichas del inventario también quedan disponibles en el selector, incluidas las que todavía no tienen coordenadas. Seleccionar una estación en el mapa o en el selector consulta su ficha por ID. La ficha del Laboratorio debe mostrar las tablas meteorológicas que la página publique, junto con la hora de consulta. El horario de consulta no debe confundirse con la hora de medición, que debe aparecer en los registros de origen.

## Límites

- La extracción depende de la estructura HTML que AgroClima publique. Si cambia, el parser de tablas puede necesitar ajustes.
- No se ha confirmado una API JSON oficial de AgroClima.
- El inventario local actual contiene 192 fichas detectadas en el rango de IDs 1400–1700; 187 tienen coordenadas y 5 quedan accesibles solo desde el selector. Esto no debe confundirse con el mapa público actual de AgroClima, que informa 119 estaciones: el inventario local no está todavía sincronizado ni reconciliado automáticamente con ese recuento.
- El inventario de estaciones no equivale a observaciones; el conector consulta la página al seleccionar una estación. No se hacen consultas masivas ni polling de toda la red.
- No hay streaming continuo. La consulta ocurre bajo demanda y el usuario puede actualizar manualmente.
- Las condiciones de acceso, frecuencia permitida y términos del proveedor deben respetarse. El Worker no automatiza polling.
- Las coordenadas de estaciones marcadas como pares no etiquetados siguen requiriendo validación independiente.
