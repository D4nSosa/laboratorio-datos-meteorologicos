# Fuentes externas y archivos de investigación

Esta carpeta conserva conjuntos de datos meteorológicos e hidrológicos con procedencia, unidades, cobertura y controles separados. **No forma parte todavía de la interfaz pública**: primero se archivan y validan los datos; la integración visual se hace después.

## Estructura

| Ruta | Contenido | Uso |
|---|---|---|
| `radiosondeos/igra/` | Archivos originales IGRA 2.2, inventario oficial y catálogos derivados | Perfiles atmosféricos verticales y cobertura de estaciones |
| `precipitacion/chirps-v3/` | CHIRPS v3 Final, recorte nacional y agregados mensuales derivados | Precipitación espacial de largo plazo |
| `hidrologia/ina-dsiyah/` | Catálogos de estaciones, redes, variables, unidades y series de DSIyAH | Cuenca del Plata; no representa por sí sola todo el país |
| `hidrologia/snih/` | Inventario SNIH, asociaciones de parámetros, series nivométricas y telemetría | Redes integradas al SNIH; cobertura y variables según estación |
| `manifiestos/` | Manifiestos JSON con fechas, URL, versiones, conteos, errores y SHA-256 | Auditoría y reproducción |

## Contrato de datos para la interfaz

- Geometrías de estaciones: GeoJSON en EPSG:4326; coordenadas como `[longitud, latitud]`.
- Tablas: CSV o CSV comprimido con gzip; conservar nombres de campos, unidades y fecha/hora UTC o local explícita.
- Grillas: NetCDF con coordenadas `time`, `latitude`, `longitude`; no asumir que el navegador puede leer NetCDF sin una biblioteca específica o una capa de servicio.
- Los perfiles IGRA originales son ZIP con archivos de texto por identificador de estación.
- Las observaciones históricas validadas y la telemetría cruda no validada se mantienen en rutas y variables separadas.
- No interpolar huecos ni reemplazar valores faltantes por cero.
- No fusionar estaciones por cercanía geográfica. Los posibles traslados/duplicados se marcan para revisión y se conservan sus identificadores originales.

## Fuentes y notas de interpretación

### IGRA 2.2 — NOAA/NCEI
Inventario y perfiles originales: https://www.ncei.noaa.gov/pub/data/igra/ y https://www.ncei.noaa.gov/pub/data/igra/data/data-por/

Los archivos de perfil se distribuyen por identificador. Dos IDs cercanos pueden reflejar cambios de emplazamiento, series distintas o sitios separados; no se deduplican automáticamente. El inventario de estaciones es una tabla de disponibilidad, no un perfil atmosférico.

### CHIRPS v3 Final — UCSB CHC
Fuente y producto procesado de acceso público: https://dynamical.org/catalog/ucsb-chc-chirps-analysis-final/

Los NetCDF nacionales anuales se derivan del producto diario Final: tasa media diaria `kg m-2 s-1` multiplicada por 86.400 segundos y sumada por mes. Unidades de salida: `mm month-1`. **No etiquetar estos archivos como el producto mensual nativo de CHIRPS**. Licencia CC BY 4.0; citar UCSB CHC/CHIRPS v3 y dynamical.org como procesador/archivo.

### INA — DSIyAH
API pública: https://alerta.ina.gob.ar/pub/gui/

Los catálogos pertenecen al Sistema de Información Hidrológica de la Cuenca del Plata. La API permite solicitar observaciones por `seriesId` o por estación/variable y rango temporal. No generalizar su cobertura a la totalidad de Argentina.

### SNIH — Sistema Nacional de Información Hídrica
Portal: https://snih.hidricosargentina.gob.ar/  
Términos: https://snih.hidricosargentina.gob.ar/Terminos.aspx

El portal distingue datos históricos consolidados y datos a tiempo útil sin validar. Mantener esa diferencia en cualquier visualización. Citar a la Subsecretaría de Recursos Hídricos y/o a la red que corresponda, junto con la fecha de actualización.

### GPM IMERG
Producto de referencia: NASA GPM IMERG V07B, resolución aproximada 0,1° y 30 minutos. Los productos Final y Late no son intercambiables: Final tiene ajuste gauge y mayor latencia; Late es de menor latencia y distinta calidad. La descarga masiva del producto NASA Final requiere autenticación Earthdata. No se marca como descargado mientras no existan archivos verificados.

## Integración sugerida

1. Leer el manifiesto y el catálogo de estaciones para construir las capas del mapa.
2. Mostrar la fuente, variable, unidad, período y estado de validación junto a cada serie.
3. Usar CHIRPS como grilla de precipitación y las estaciones como observaciones independientes; no presentarlas como si fueran la misma medición.
4. Para NetCDF, decidir entre lectura en un servicio de datos o conversión a GeoTIFF/COG o teselas antes de cargar grillas completas en el navegador.
5. Incorporar filtros por período, variable, fuente y calidad; no cargar todos los perfiles/series al abrir la página.

Los estados reales de cada descarga están en los manifiestos, no se infieren de la mera existencia de esta documentación.
