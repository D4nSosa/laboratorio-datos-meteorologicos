# Inventario de estaciones AgroClima

La exploración se ejecuta mediante GitHub Actions con `scripts/descubrir_estaciones_agroclima.py`.

## Qué hace

1. Inspecciona el HTML público del mapa y los JavaScript enlazados para registrar referencias y posibles IDs.
2. Explora un rango acotado de IDs (por defecto 1400–1700), además de IDs semilla documentados.
3. Comprueba las páginas públicas conocidas de cada ID.
4. Extrae nombres desde metadatos HTML, encabezados y etiquetas explícitas; coordenadas desde campos etiquetados o estructuras de mapas; y fechas únicamente cuando aparecen junto a una etiqueta explícita de observación/actualización.
5. Genera `datos/agroclima/estaciones.json` y `estaciones.csv`, y publica ambos como commit en la rama y artefacto de Actions.

## Calidad y revisión

Cada registro conserva `name_source`, `coordinate_source` y `metadata_quality`. Los valores no detectados se dejan como `null`; no se sustituyen por nombres inventados ni por textos genéricos. Las coordenadas detectadas como pares sin etiqueta quedan marcadas `unlabelled_pair` y requieren revisión manual.

`page_validated` significa que la página pública contiene evidencia meteorológica. No demuestra que el sensor esté activo, que los datos sean recientes ni que exista una serie histórica descargable. `metadata_quality=complete` sólo indica que se obtuvo nombre y coordenadas; tampoco certifica operatividad.

## Ejecución

En GitHub: Actions → Descubrir estaciones AgroClima → Run workflow. El rango inicial por defecto es 1400–1700, con máximo de 1501 IDs por ejecución. También se ejecuta semanalmente.

## Límites

- El rango de IDs no garantiza un catálogo completo.
- El mapa puede depender de un catálogo/API dinámico que no esté expuesto en el HTML inicial.
- Los endpoints candidatos se registran para inspección, pero no se invocan endpoints privados o no documentados automáticamente.
- El proceso no descarga ni integra observaciones meteorológicas en el Laboratorio; sólo construye un inventario auditable.

## IDs semilla

1490, 1528, 1578, 1584, 1609 y 1620.
