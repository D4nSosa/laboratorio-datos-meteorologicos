# Catálogo nacional de estaciones SIGA-INTA (referencia externa)

Recuperado el 2026-10-29 desde el proyecto público [Precipitaciones Argentina](https://github.com/marianof2000/precipitaciones-argentina-inta), que declara consolidar observaciones de precipitación de estaciones argentinas a partir de SIGA-INTA.

## Archivos archivados aquí

- `estaciones.json`: catálogo original de 182 estaciones y metadatos.
- `estaciones.csv`: versión tabular derivada del catálogo para filtrar y buscar estaciones.
- `manifest.json`: manifiesto original de los datos de observaciones, copiado del repositorio fuente.
- `catalog-analysis.json`: resumen de cobertura provincial y estaciones de Corrientes.
- `estaciones-observaciones.csv.gz`: consolidado nacional real de observaciones, descargado y comprimido desde Git LFS (35.814.553 bytes).
- `observaciones-metadata.json`: resultado de validación de hash, filas, columnas y estructura.
- `OBSERVACIONES.md`: descripción del archivo de observaciones y advertencias de uso.

## Lo que declara el manifiesto de la fuente

- 182 estaciones.
- 1.177.258 registros.
- 38 columnas, entre ellas `precipitacion_pluviometrica`, `precipitacion_cronologica` y `precipitacion_maxima_30minutos`.
- Tamaño del CSV de observaciones: 151.209.900 bytes.
- SHA-256 declarado por la fuente: `b55fa017707eab7552c220b92185387d52dfd598f26f23a3be1aa59f0c0323dc`.
- Manifiesto generado: 2026-08-20.

## Descarga y validación del consolidado

El archivo real se descargó mediante GitHub Actions desde el repositorio de origen, se verificó y se incorporó a este repositorio como `estaciones-observaciones.csv.gz`. El CSV original pesa 151.209.900 bytes; comprimido pesa 35.814.553 bytes.

La ejecución verificó el SHA-256 del CSV original contra el manifiesto de origen (`b55fa017707eab7552c220b92185387d52dfd598f26f23a3be1aa59f0c0323dc`), contó 1.177.258 filas de datos y 38 columnas, y revisó que cada fila mantuviera el número correcto de campos. El resultado de esa validación está en `observaciones-metadata.json`.

La validación confirma integridad y estructura, no calidad instrumental ni continuidad temporal de cada estación. El archivo procede de un consolidado comunitario que declara usar datos SIGA-INTA; se mantiene la referencia al proyecto original y no se le aplica automáticamente la licencia MIT de este laboratorio.

## Hallazgo para la investigación de Virasoro

El catálogo tiene estaciones en Corrientes y Misiones. Las estaciones SIGA más cercanas que figuran en el catálogo están aproximadamente a 70–80 km de Gobernador Virasoro, incluyendo Villa Miguel Lanús/Cerro Azul e Ituzaingó. Esto no reemplaza registros de Virasoro ni demuestra que las series sean completas. Ver `catalog-analysis.json`.

Fuente original: https://github.com/marianof2000/precipitaciones-argentina-inta
