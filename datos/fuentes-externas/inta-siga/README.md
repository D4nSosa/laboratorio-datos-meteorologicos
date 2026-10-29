# Catálogo nacional de estaciones SIGA-INTA (referencia externa)

Recuperado el 2026-10-29 desde el proyecto público [Precipitaciones Argentina](https://github.com/marianof2000/precipitaciones-argentina-inta), que declara consolidar observaciones de precipitación de estaciones argentinas a partir de SIGA-INTA.

## Archivos archivados aquí

- `estaciones.json`: catálogo original de 182 estaciones y metadatos.
- `estaciones.csv`: versión tabular derivada del catálogo para filtrar y buscar estaciones.
- `manifest.json`: manifiesto original de los datos de observaciones, copiado del repositorio fuente.
- `catalog-analysis.json`: resumen de cobertura provincial, estaciones de Corrientes y limitaciones de la recuperación.

## Lo que declara el manifiesto de la fuente

- 182 estaciones.
- 1.177.258 registros.
- 38 columnas, entre ellas `precipitacion_pluviometrica`, `precipitacion_cronologica` y `precipitacion_maxima_30minutos`.
- Tamaño del CSV de observaciones: 151.209.900 bytes.
- SHA-256 declarado por la fuente: `b55fa017707eab7552c220b92185387d52dfd598f26f23a3be1aa59f0c0323dc`.
- Manifiesto generado: 2026-08-20.

## Importante: no se archivó el CSV de observaciones

En el repositorio original, `datos/estaciones.csv` es un puntero Git LFS de 134 bytes; el contenido real es un objeto LFS de aproximadamente 151 MB. La herramienta de acceso disponible en esta sesión solo devolvió el puntero, no el objeto binario. Por lo tanto, el manifiesto y catálogo fueron recuperados, pero **las 1.177.258 observaciones no se han descargado ni validado localmente ni se han copiado a este repositorio**.

El catálogo sí sirve para buscar estaciones por provincia y proximidad, pero no para analizar precipitaciones. El manifiesto y el resumen se conservan como metadatos de terceros, con enlaces al origen; no se les aplica la licencia MIT del repositorio de investigación.

## Hallazgo para la investigación de Virasoro

El catálogo tiene estaciones en Corrientes y Misiones. Las estaciones SIGA más cercanas que figuran en el catálogo están aproximadamente a 70–80 km de Gobernador Virasoro, incluyendo Villa Miguel Lanús/Cerro Azul e Ituzaingó. Esto no reemplaza registros de Virasoro ni demuestra que las series sean completas. Ver `catalog-analysis.json`.

Fuente original: https://github.com/marianof2000/precipitaciones-argentina-inta
