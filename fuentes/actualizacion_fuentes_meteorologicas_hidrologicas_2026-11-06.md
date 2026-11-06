# Actualización de fuentes meteorológicas e hidrológicas — 6 de noviembre de 2026

**Proyecto:** Laboratorio de Datos Meteorológicos  
**Alcance:** revisión documental de fuentes nacionales y globales para ampliar la investigación meteorológica y atmosférica a escala de localidad, provincia y país.  
**Estado:** fuentes identificadas y documentadas; esta revisión no incorpora conectores ni afirma que las series hayan sido descargadas y validadas por el Laboratorio.

## Síntesis

La expansión de los análisis no requiere reemplazar las fuentes actuales ni cambiar la identidad del Laboratorio. La estrategia más sólida es complementar los registros puntuales con productos de grilla y, cuando corresponda, series hidrométricas. Cada producto debe conservar su tipo, resolución, período, hora de referencia y limitaciones.

Tres recursos resultan especialmente relevantes:

1. **NASA GPM IMERG:** estimación satelital global de precipitación con cobertura de Argentina, resolución de 0,1° (aproximadamente 10 km) y productos subdiarios/diarios. La versión V07B cubre desde enero de 1998. El producto Early tiene latencia mínima aproximada de 4 horas; Late, alrededor de 14 horas; Final incorpora análisis con pluviómetros y llega con varios meses de demora. Los productos no son mediciones de estación y sus distintas corridas no deben mezclarse sin identificarlas.
2. **INA / DSIyAH:** API documentada para consultar estaciones, áreas de interés, series temporales puntuales y capas ráster. Ofrece formatos como CSV, JSON, GeoJSON y GeoTIFF. El alcance documentado corresponde a la Cuenca del Plata, por lo que es muy valioso para el NEA y otras zonas de esa cuenca, pero no debe describirse como cobertura hidrológica nacional completa.
3. **SNIH:** portal nacional con datos históricos consolidados y datos a tiempo útil. El propio portal advierte que el dato a tiempo útil puede ser el registro crudo del sensor y no estar validado. No es una red de alerta de inundaciones.

## Inventario y uso recomendado

| Fuente | Información útil | Alcance conocido | Estado para el Laboratorio |
|---|---|---|---|
| NASA GPM IMERG | Precipitación estimada cada 30 minutos y productos acumulados diarios | Global; 0,1° (~10 km); enero de 1998 al presente | Documentada; no integrada |
| INA / DSIyAH | Estaciones, series observadas y simuladas, niveles, caudales, precipitación y capas del ciclo hidrológico | Cuenca del Plata; cobertura por red, estación y variable | API documentada; inventario y series por validar |
| SNIH | Registros históricos consolidados y datos a tiempo útil de redes integradas | Estaciones adheridas; cobertura no homogénea | Portal documentado; revisar estación por estación |
| SMN | Observaciones oficiales y campos espaciales de precipitación | Red de estaciones y productos regionales; disponibilidad por producto | Fuentes identificadas; no se afirma integración de nuevos productos |
| INTA-SIGA | Observaciones y metadatos de estaciones | Según catálogo y estación | Snapshot archivado; requiere validación de variables y series |
| Ministerio de Producción de Corrientes | Registros diarios y mensuales de precipitación | Provincia de Corrientes; cobertura temporal y geográfica desigual | Snapshot archivado del 29/10/2026 |
| RainViewer | Mosaico compuesto de reflectividad radar y cuadros recientes | 14 radares integrados para Argentina; cobertura irregular | Capa de teselas operativa en el mapa, con atribución y límites de uso |
| NOAA GOES-19 ABI | GeoColor y secuencia sectorial de bandas visibles/infrarrojas | Disco completo y sector sur de Sudamérica | Visor GeoColor y secuencia NOAA integrados |
| SMN / SINARAME | Mosaicos e imágenes de radares oficiales | Red nacional; alcance variable por radar | Enlaces a visores oficiales; ingesta directa pendiente |
| IGN / Georef | Límites administrativos provinciales GeoJSON | 23 provincias y CABA | Geometrías integradas para agregación exploratoria por provincia |
| Open-Meteo | Pronóstico de 7 días e histórico ERA5 en puntos de muestreo | Cobertura nacional por combinación de puntos de grilla | Campos nacionales agregados por provincia; no es raster continuo ni promedio areal oficial |

## Detalles técnicos y advertencias

### NASA GPM IMERG

- Documentación general: https://gpm.nasa.gov/data/directory
- Documentación técnica V07: https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation
- IMERG Early: https://gpm.nasa.gov/taxonomy/term/1357
- IMERG Final: https://gpm.nasa.gov/taxonomy/term/1417

IMERG combina estimaciones de sensores satelitales de microondas y sensores infrarrojos. Los campos se generan sobre una grilla de 0,1° × 0,1°. La resolución no permite interpretar cada píxel como una medición puntual. En regiones con precipitación convectiva intensa puede haber diferencias respecto de pluviómetros.

Los productos tienen distintas latencias y etapas de procesamiento:
- Early: baja latencia, estimación rápida con propagación hacia adelante.
- Late: incorpora información adicional y propagación hacia atrás.
- Final: producto diferido con análisis de pluviómetros; adecuado para estudios retrospectivos, no para seguimiento inmediato.

Para acumulados diarios hay que respetar la convención temporal del producto y verificar si el día está definido en UTC. No comparar directamente con un pluviómetro local sin alinear el horario de corte y reconocer la diferencia de escala.

### INA / DSIyAH

- Descripción institucional de la API: https://www.argentina.gob.ar/ina/recursos/aplicacionweb-datos-hidrologicos
- Asistente y catálogo de servicios: https://alerta.ina.gov.ar/pub/gui/apibase
- Colección de estaciones: https://alerta.ina.gov.ar/pub/gui/metadata&layer=siyah:estaciones

La API permite consultar estaciones, áreas de interés y series numéricas, además de capas ráster observadas o simuladas. Antes de integrar se debe relevar el catálogo de redes, variables, series, fechas disponibles, unidades, referencias verticales de alturas y convenciones de tiempo. Los metadatos de estaciones del servicio advierten que algunas ubicaciones y descripciones pueden no ser oficiales.

La cobertura descrita es la Cuenca del Plata. No se debe extender esa cobertura a cuencas argentinas que no estén representadas.

### Sistema Nacional de Información Hídrica (SNIH)

- Portal: https://snih.hidricosargentina.gob.ar/
- Descripción institucional: https://www.argentina.gob.ar/obras-publicas/recursos-hidricos/sistema-nacional-de-informacion-hidrica-0

El portal distingue datos históricos consolidados de datos a tiempo útil. El propio sitio advierte que los datos a tiempo útil pueden ser registros crudos no validados y que la red no es un sistema de alerta contra inundaciones. Para una publicación de investigación, priorizar series históricas procesadas cuando estén disponibles y conservar la advertencia en cualquier visualización de telemetría reciente.

### Servicio Meteorológico Nacional (SMN)

- Descarga de datos: https://www.smn.gob.ar/descarga-de-datos
- Catálogo de estaciones: https://www.datos.gob.ar/dataset/smn-listado-estaciones-meteorologicas-smn
- Datos meteorológicos horarios: https://www.datos.gob.ar/dataset/smn-datos-meteorologicos-horarios
- Referencia de precipitación observada en campos de la Cuenca del Plata: https://www.smn.gob.ar/sites/default/files/Referencia_Pecipitacion_observada.pdf

El dataset horario publicado en Datos Argentina describe temperatura, presión, viento y humedad; no debe asumirse que contiene precipitación. El documento del SMN sobre campos de precipitación describe una interpolación espacial (Kriging) a partir de estaciones de superficie del SMN y la red GTS. Es un campo espacial derivado de observaciones, no un pluviómetro en cada celda. La fuente señala que la confiabilidad disminuye donde la densidad de estaciones es baja.

## Cómo aprovechar estas fuentes en las secciones existentes

No se propone crear módulos nuevos. Las capacidades se integrarían en la estructura actual:

- **Precipitaciones:** comparar acumulados de estaciones y estimaciones IMERG en ventanas diarias y multidiarias, siempre con etiquetas de tipo de dato y horario de corte.
- **Mapa de estaciones y referencias:** mostrar cobertura de estaciones, celdas satelitales y redes hidrológicas cuando sus catálogos estén verificados.
- **Exploración de datos:** permitir consultas por ubicación y período cuando la fuente ofrezca series históricas descargables y el flujo de actualización esté probado.
- **Preguntas climáticas:** analizar episodios de lluvia intensa, períodos secos/húmedos, anomalías y relaciones estadísticas con índices climáticos.
- **Método y límites:** explicar diferencias entre medición puntual, estimación satelital, campo interpolado, reanálisis y dato hidrológico modelado.

## Alcance territorial y temporal

La exploración debe poder realizarse a tres escalas complementarias:

- **Localidad o coordenada:** perfil de variables y series históricas/pronósticas para un punto, identificando si el valor procede de una estación o de una celda de grilla.
- **Provincia o región:** comparación de estaciones y celdas disponibles dentro del territorio. Los agregados deben declarar el método, la cantidad de puntos válidos y la cobertura temporal; no se debe sustituir el área por una única coordenada representativa.
- **Nación:** panorama espacial de productos con cobertura argentina o global, con capas independientes para observaciones, satélite, reanálisis, radar y pronóstico.

Gobernador Virasoro continúa como primera referencia territorial de investigación, pero no limita la cobertura ni la agenda nacional del Laboratorio.

## Fuentes atmosféricas y vigilancia de tormentas

- **GOES-19 ABI:** imágenes visibles, infrarrojas y vapor de agua. La disponibilidad por canal, sector, cadencia y latencia debe validarse en el flujo de datos antes de habilitar animación pública.
- **GOES GLM:** eventos, grupos y flashes eléctricos. La cobertura alcanza América, pero la integración debe conservar producto, hora y resolución, y no confundir detección satelital con una red terrestre de rayos.
- **SINARAME:** radar meteorológico argentino. Verificar mosaicos, reflectividad, velocidad radial, productos derivados, política de acceso y continuidad. Una imagen radar no debe reconstruirse a partir de precipitación modelada.
- **GPM IMERG y CHIRPS:** productos de precipitación satelital/estimada para análisis espacial e histórico; no son radar ni pluviómetros.
- **Open-Meteo / modelos numéricos:** variables de diagnóstico y pronóstico; identificar modelo, ciclo, hora de inicialización y horizonte.
- **Radiosondeos:** perfiles verticales de temperatura, humedad y viento para estudiar estructura atmosférica e inestabilidad, según disponibilidad de estaciones y horarios.


## Implementación de vigilancia atmosférica

La sección existente de Mapa de estaciones ahora incluye una capa RainViewer de reflectividad compuesta. El manifiesto público entrega cuadros históricos recientes, con intervalos aproximados de diez minutos y hasta dos horas; la interfaz permite avanzar, retroceder, pausar y recorrer el tiempo. La cobertura en Argentina es parcial, por lo que una zona sin ecos o sin teselas no debe interpretarse como ausencia de lluvia. El proveedor requiere atribución y limita el uso gratuito a fines personales, educativos y comunitarios de pequeña escala.

El mapa también enlaza los visores oficiales del SMN y SINARAME. No se declara ingestión propia de los productos oficiales: el usuario puede abrir los visores institucionales directamente.

Para vigilancia satelital se incorporó una secuencia NOAA GOES-19 ABI del sector sur de Sudamérica. La selección incluye banda 13 infrarroja (10,3 µm), banda 8 de vapor de agua (6,2 µm), banda 2 visible (0,64 µm) y banda 11 (8,4 µm). La página NOAA entrega hasta 24 imágenes recientes; la disponibilidad depende del producto y del estado del sitio. La secuencia es informativa, no operativa.

## Mapa nacional por provincia

Se integró la geometría GeoJSON provincial desde Georef/IGN. El mapa genera puntos de muestreo aproximados de 1° dentro de cada provincia y consulta Open-Meteo por lotes. Puede visualizar:

- Pronóstico de siete días para precipitación acumulada, nubosidad media, viento máximo diario y temperatura máxima.
- Histórico ERA5 de hasta 90 días para las mismas variables; la precipitación se acumula por punto y las otras variables se promedian temporalmente.
- Agregación provincial como promedio simple de puntos disponibles, con popup que informa media, rango y cantidad de puntos.
- Puntos de muestreo visibles de forma opcional.

La resolución de muestreo es aproximada y no corresponde a la resolución nativa de ERA5 ni de los modelos de pronóstico. No se pondera por área; los límites provinciales se usan para agrupar puntos, no para inventar valores de zonas sin cobertura. La consulta por localidad y el pronóstico puntual de hasta 16 días permanecen en Laboratorio abierto.

## Verificación antes de publicar capas

1. Confirmar URL/API o bucket y acceso sin credenciales privadas desde el entorno previsto.
2. Probar cobertura geográfica efectiva para Argentina y, cuando corresponda, para Corrientes/NEA.
3. Descargar una muestra histórica y otra reciente, comprobar fechas, unidades, proyección, resolución y licencias.
4. Comparar una muestra con una fuente independiente y documentar sesgos y límites.
5. Implementar caché, control de errores y fecha de última actualización sin presentar caché vencida como dato actual.
6. Activar cada capa solo cuando su flujo de datos sea reproducible y esté validado técnicamente.

No se adopta una localidad como único caso de investigación. El diseño nacional debe permitir comparar zonas y escalas; las investigaciones locales se eligen por preguntas y evidencia disponible.

## Próximas verificaciones técnicas

1. Probar una descarga histórica diaria de IMERG Final y una consulta reciente Early/Late para un punto y un evento conocidos.
2. Comparar acumulados IMERG con al menos una estación con serie y horario de corte documentados.
3. Extraer el catálogo de estaciones y variables de INA, y verificar qué estaciones tienen series históricas accesibles para el Paraná y el entorno de Itatí.
4. Identificar estaciones SNIH relevantes y distinguir datos históricos procesados de telemetría cruda.
5. Revisar licencias, límites de consulta, formatos y frecuencia de actualización antes de automatizar descargas.
6. Diseñar pruebas de calidad y metadatos antes de exponer cualquier serie nueva en la interfaz.

**Conclusión:** la combinación de observaciones, estimaciones satelitales y series hidrológicas puede ampliar sustancialmente las preguntas que investiga el Laboratorio. La integración debe hacerse después de probar cobertura, calidad y reproducibilidad; documentar una fuente no equivale a tenerla operativa.
