# Estado de descargas y dataset meteorológico — 29/10/2026

Proyecto: Laboratorio de Datos Meteorológicos y Territoriales  
Responsable: DAN SOSA

## Resumen

Se descargaron mediante acceso a archivos públicos de GitHub y se copiaron al repositorio dos grupos de materiales:

1. **Corrientes:** snapshot de los archivos mensuales, diarios, catálogo de fuentes, metadatos y tabla de estaciones del portal del Departamento de Economía Agraria del Ministerio de Producción de Corrientes. Se generaron además CSV normalizados para facilitar búsquedas y análisis.
2. **INTA-SIGA, cobertura nacional:** catálogo de 182 estaciones y manifiesto de un consolidado de observaciones que un proyecto externo declara contener 1.177.258 registros. Se archivaron el catálogo JSON, una versión CSV para filtrar estaciones, el manifiesto y un análisis de cobertura. El archivo de observaciones de 151 MB no se pudo recuperar: el repositorio original lo guarda en Git LFS y el conector de GitHub disponible devolvió solo el puntero de Git LFS.

**No se afirma que ya tengamos un dataset nacional de observaciones descargado.** Tenemos un catálogo nacional de estaciones y metadatos que identifican un consolidado nacional existente, pero sus observaciones siguen pendientes de obtener.

## Archivos guardados en este repositorio

### Corrientes

Directorio: `datos/fuentes-externas/corrientes/`

- `rainfall-daily.json`: copia del archivo diario original.
- `rainfall-daily.csv`: versión CSV derivada.
- `rainfall.json`: copia del archivo mensual original.
- `rainfall-monthly.csv`: versión expandida a filas año-departamento-mes.
- `stations.json`: tabla original de estaciones y registros meteorológicos mensuales.
- `source-catalog.json`: catálogo de fuentes publicado por el portal.
- `metadata.json`: metadatos originales.
- `qa-summary.json`: métricas de cobertura y controles básicos.
- `README.md`: procedencia y advertencias.

Fuente original: https://github.com/deaeconomiactes/Precipitaciones-Lluvias

### INTA-SIGA, catálogo nacional

Directorio: `datos/fuentes-externas/inta-siga/`

- `estaciones.json`: catálogo original de 182 estaciones.
- `estaciones.csv`: tabla derivada filtrable con identificador, nombre, provincia, localidad, coordenadas, tipo y fechas reportadas.
- `manifest.json`: manifiesto original del consolidado de observaciones.
- `catalog-analysis.json`: análisis por provincia, estaciones correntinas y estado de recuperación.
- `README.md`: procedencia, advertencias y explicación de por qué falta el CSV de observaciones.

Proyecto fuente: https://github.com/marianof2000/precipitaciones-argentina-inta  
Paquete original de INTA-SIGA: https://github.com/AgRoMeteorologiaINTA/siga

## Análisis de la base diaria provincial

El archivo diario recuperado contiene 5.186 filas y 25 departamentos. Las fechas registradas van del 2023-01-01 al 2026-10-25.

| Año | Filas | Media de valores por registro (mm) | Mínimo (mm) | Máximo (mm) |
|---|---:|---:|---:|---:|
| 2023 | 1.654 | 20,424 | 0,1 | 300 |
| 2024 | 1.505 | 23,595 | 0,8 | 202 |
| 2025 | 1.471 | 24,817 | 0,5 | 243 |
| 2026, parcial | 556 | 19,442 | 1 | 152,5 |

Estas medias **no son promedios anuales de precipitación**. Son la media aritmética de los valores de las filas disponibles y no tienen en cuenta el número desigual de registros por localidad/fecha, por lo que no deben usarse para comparar la lluvia anual entre años. Los totales anuales requieren reconstruir por sitio y año la cobertura y el conjunto de observaciones.

Controles básicos ejecutados: 0 filas con fecha inválida, precipitación negativa/no numérica o coordenadas ausentes, según el esquema esperado. Esto es solo una validación estructural; no valida el origen, la calidad instrumental ni la continuidad de cada registro.

**Hallazgo crítico para Virasoro:** el archivo diario no contiene filas cuyo campo `department` sea Virasoro. El catálogo provincial menciona Virasoro como estación, pero eso no significa que esta tabla diaria contenga observaciones para esa estación. No se debe completar la serie con valores de Santo Tomé o de otra localidad.

El archivo mensual contiene 817 filas por departamento y año, con años declarados 1993–2026 y 25 departamentos. Es una serie departamental y debe mantenerse separada de las mediciones puntuales de estaciones y de ERA5.

## Análisis del catálogo nacional INTA-SIGA

El catálogo externo declara 182 estaciones en 24 valores de provincia/etiqueta, incluyendo siete estaciones con provincia sin asignar. El manifiesto de la fuente declara:

- 1.177.258 registros.
- 38 columnas, entre ellas tres variables de precipitación.
- CSV de observaciones de 151.209.900 bytes.
- SHA-256 declarado: `b55fa017707eab7552c220b92185387d52dfd598f26f23a3be1aa59f0c0323dc`.
- Generación del manifiesto: 2026-08-20.

Esas cifras son **declaraciones del manifiesto del proyecto fuente**, no una auditoría independiente de los registros: no fue posible obtener el objeto CSV para verificar hash, número de filas o calidad.

El catálogo incluye 13 estaciones con provincia Corrientes y siete con provincia Misiones. Entre las estaciones del catálogo más cercanas a Gobernador Virasoro aparecen Villa Miguel Lanús/Cerro Azul, Misiones (aproximadamente 70–73 km según coordenadas publicadas), e Ituzaingó, Corrientes (aproximadamente 79 km). Son referencias para investigar, no sustitutos de una estación local.

## Fuentes consultadas y qué falta

### SMN

- Portal de descarga: https://www.smn.gob.ar/descarga-de-datos
- Dataset horario de Datos Argentina: https://datos.gob.ar/dataset/smn-datos-meteorologicos-horarios
- Catálogo de estaciones en Datos Argentina: https://datos.gob.ar/dataset/smn-listado-estaciones-meteorologicas-smn

El archivo horario documentado contiene temperatura, presión, humedad y viento, pero no precipitación entre los campos enumerados. No lo usamos como fuente de lluvia. La descarga específica de series de precipitación del SMN todavía debe identificarse y obtenerse.

### INA / DSIyAH

- Documentación de API: https://www.argentina.gob.ar/ina/recursos/aplicacionweb-datos-hidrologicos
- Catálogo de estaciones: https://alerta.ina.gov.ar/pub/gui/estaciones
- Catálogo de datos/series: https://alerta.ina.gov.ar/pub/gui/datos

La API documenta estaciones, variables y series de la Cuenca del Plata, incluidas variables de precipitación. No se descargó todavía una exportación masiva de estaciones/series desde la API.

### SNIH

- Portal: https://snih.hidricosargentina.gob.ar/
- Información institucional: https://www.argentina.gob.ar/node/439689

El portal informa que ofrece datos históricos consolidados y registros en tiempo útil no validados. No se exportó todavía un inventario completo ni una descarga nacional de series.

### INTA-SIGA

El paquete abierto permite listar estaciones y descargar sus observaciones con funciones como `siga_estaciones()` y `siga_descargar()`. El catálogo nacional se archivó desde un proyecto externo que declara usar SIGA, pero no pudimos recuperar su archivo CSV de 151 MB. Queda pendiente descargar directamente desde SIGA o desde el objeto Git LFS original.

### ICAA

- Acceso a estaciones: https://icaa.gov.ar/instructivo-acceso-estacion-icaa/
- Históricos publicados: https://icaa.gov.ar/registro-de-datos-meteorologicos/

El ICAA informó que la consulta enviada fue derivada al área técnica. El inventario provincial y las series históricas que no estén publicadas siguen pendientes de respuesta.

## Próximos pasos prioritarios

1. Obtener de forma directa el CSV consolidado de SIGA-INTA (151 MB) y verificar su SHA-256, número de filas, columnas y cobertura.
2. Descargar el catálogo de estaciones y las series con variable precipitación de INA/DSIyAH, filtrando por unidad, frecuencia y estación.
3. Obtener del SMN el producto que efectivamente incluya precipitación histórica por estación, no solo el dataset horario de temperatura/presión/viento/humedad.
4. Consultar el SNIH por series pluviométricas y metadatos, distinguiendo registros históricos validados de telemetría cruda.
5. Auditar los datos diarios provinciales por localidad y fecha, y determinar si hay una serie útil para Virasoro.
6. Crear un catálogo maestro sin mezclar observaciones, agregaciones departamentales y reanálisis.

## Reglas para no contaminar el dataset

- Un dato ausente no es cero.
- Un acumulado departamental no equivale a una medición de estación.
- Una coordenada de un registro no demuestra por sí sola que sea una estación oficial.
- Las fechas inicial/final de una estación no garantizan cobertura diaria continua.
- No combinar fuentes con unidades, periodos o métodos incompatibles sin una tabla de correspondencias.
- Conservar fuente, fecha de recuperación, identificador original, licencia/condiciones y hash de cada archivo.
- El MIT del repositorio se aplica al código original, no a los datos de terceros; cada fuente conserva sus condiciones.

## Fuentes citadas

- INTA-SIGA: https://github.com/AgRoMeteorologiaINTA/siga
- Proyecto externo de consolidación SIGA: https://github.com/marianof2000/precipitaciones-argentina-inta
- Portal de Corrientes: https://deaeconomiactes.github.io/Precipitaciones-Lluvias/
- INA/DSIyAH: https://alerta.ina.gov.ar/pub/gui/apibase
- SNIH: https://snih.hidricosargentina.gob.ar/
- SMN: https://www.smn.gob.ar/descarga-de-datos
