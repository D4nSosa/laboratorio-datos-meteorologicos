# Fuentes y metodología

Este documento establece cómo seleccionar, comparar, procesar y comunicar los datos utilizados por el Laboratorio de Datos Meteorológicos. Cada investigación debe citar las fuentes concretas que utilizó, no solamente las que aparecen en el inventario general.

## 1. Empezar por la pregunta

Antes de elegir una fuente, definir:

- Fenómeno: precipitación, temperatura, viento, tormenta, crecida, sequía u otro.
- Territorio: estación, localidad, departamento, provincia, cuenca o grilla.
- Escala temporal: subhoraria, horaria, diaria, mensual, estacional o anual.
- Período de interés y período de referencia.
- Tipo de evidencia necesario: observación, estimación satelital, reanálisis, pronóstico o simulación.

Una fuente útil para describir patrones regionales puede no ser adecuada para cuantificar la lluvia en un lote o confirmar un evento puntual.

## 2. Tipos de datos que no deben confundirse

| Tipo | Qué representa | Precaución |
|---|---|---|
| Observación de estación | Medición en un punto y momento | Revisar instrumento, ubicación, unidad, frecuencia, faltantes y controles de calidad. |
| Agregado territorial | Valor informado para departamento, región o área | No equivale a un pluviómetro puntual; verificar cómo se construyó. |
| Estimación satelital | Estimación de precipitación sobre una celda | Tiene resolución espacial, incertidumbre y sesgos; no es una medición directa en superficie. |
| Reanálisis | Reconstrucción de grilla que combina observaciones y modelos | No equivale a una estación ni a una observación independiente. |
| Pronóstico numérico | Estado futuro simulado por un modelo | Debe identificarse como pronóstico, con ciclo de emisión y horizonte. |
| Producto hidrológico | Nivel, caudal, humedad o simulación de una cuenca | Identificar si es observado, estimado o modelado y cuál es la estación/área representada. |
| Variable derivada | Acumulado, anomalía, índice o estadístico calculado | Publicar fórmula, unidades, cobertura y fuente de entrada. |

## 3. Fuentes consultadas y candidatas

El catálogo vivo está en [catalogo-fuentes.json](../docs/datos/catalogo-fuentes.json). El inventario y la revisión del 6 de noviembre de 2026 están en [actualización de fuentes meteorológicas e hidrológicas](actualizacion_fuentes_meteorologicas_hidrologicas_2026-11-06.md).

Fuentes de interés:

- [ERA5 / Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api): reanálisis histórico de grilla.
- [INTA-SIGA](https://siga.inta.gob.ar/): metadatos y registros de estaciones; verificar por estación.
- [SMN — descarga de datos](https://www.smn.gob.ar/descarga-de-datos): observaciones y productos oficiales; comprobar qué variables y períodos ofrece cada archivo.
- [SMN — precipitación observada en campos de la Cuenca del Plata](https://www.smn.gob.ar/sites/default/files/Referencia_Pecipitacion_observada.pdf): campos espaciales interpolados a partir de observaciones, no mediciones en cada celda.
- [NASA GPM IMERG](https://gpm.nasa.gov/data/directory): estimaciones satelitales globales de precipitación, 0,1° y múltiples latencias/productos.
- [NOAA GOES-R ABI/GLM](https://www.ncei.noaa.gov/products/goes-terrestrial-weather-abi-glm): imágenes geoestacionarias y actividad eléctrica sobre América; GOES-19 es GOES East operativo y cubre Sudamérica.
- [NOAA GOES-19 sector sur](https://www.star.nesdis.noaa.gov/goes-draft/sector_band.php?band=13&length=24&sat=G19&sector=ssa): secuencias ABI de 24 imágenes recientes para bandas visibles e infrarrojas.
- [NOAA GOES-19 GLM FED sector sur](https://www.star.nesdis.noaa.gov/GOES/sector_band.php?band=EXTENT3&length=24&sat=G19&sector=ssa): densidad de extensión de flashes eléctricos sobre GeoColor, en ventanas de aproximadamente cinco minutos.
- [RainViewer API](https://www.rainviewer.com/api.html): mosaico compuesto de reflectividad en teselas, cuadros recientes y cobertura parcial; uso personal/educativo/comunitario con atribución.
- [SMN — imágenes de radar](https://ws2.smn.gob.ar/radar): visor oficial de mosaicos y radares individuales.
- [SINARAME — imágenes](https://radares.hidricosargentina.gob.ar/): visor del sistema nacional de radares; no implica que el Laboratorio tenga un conector propio.
- [Georef — provincias GeoJSON](https://apis.datos.gob.ar/georef/api/v2.0/provincias.geojson) y [IGN — geoservicios](https://ide.ign.gob.ar/geoservicios/rest/services/servicio_fondos/MapServer/0): geometrías administrativas de referencia.
- [SINARAME](https://www.argentina.gob.ar/obras-publicas/recursos-hidricos/sistema-nacional-de-radares-meteorologicos-sinarame): red argentina de radares; verificar productos, acceso y cobertura útil por localidad antes de integrar.
- [Open-Meteo Forecast, Historical y Historical Forecast](https://open-meteo.com/en/docs): pronósticos globales de hasta 16 días, reanálisis ERA5 y archivo de pronósticos anteriores para evaluación.
- [CHIRPS](https://www.chc.ucsb.edu/data/chirps): estimación de precipitación satelital y pluviómetros sobre tierra, con resolución y latencia propias.
- [INA — API de datos hidrológicos](https://www.argentina.gob.ar/ina/recursos/aplicacionweb-datos-hidrologicos): estaciones y series de la Cuenca del Plata, observadas y simuladas.
- [SNIH](https://snih.hidricosargentina.gob.ar/): datos históricos consolidados y registros a tiempo útil; estos últimos pueden ser crudos y no validados.
- [ICAA — acceso a estaciones hidrometeorológicas](https://icaa.gov.ar/instructivo-acceso-estacion-icaa/): red y estaciones disponibles en Corrientes.
- [NOAA CPC — ONI](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/) y [RONI](https://cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/): índices de variabilidad climática de gran escala.

La inclusión de una fuente en esta lista no significa que el Laboratorio tenga un conector activo, que haya descargado sus datos o que la cobertura esté verificada para todas las localidades. El alcance nacional se logra combinando productos distintos y no implica observación directa homogénea en cada punto.


## 4 bis. Agregación espacial del mapa nacional

El mapa provincial obtiene límites administrativos desde Georef/IGN y genera puntos de muestreo dentro de cada polígono, aproximadamente cada 1° de latitud/longitud sobre el territorio continental argentino (la zona antártica no se muestrea en esta primera capa). Cada punto consulta por separado el producto elegido de Open-Meteo. Los pronósticos usan el selector best_match; las fechas y acumulaciones diarias del mapa se interpretan en UTC. Los valores de cada provincia se calculan como promedio de las muestras disponibles; para precipitación histórica, primero se suma la precipitación diaria en cada punto y luego se promedian los totales entre puntos. No se pondera por superficie, población ni densidad de estaciones. No se rellenan provincias sin muestras y se informa el número de puntos usados.

Esta agregación sirve para exploración y comparación descriptiva de campos de modelo/reanálisis. No debe llamarse observación provincial, interpolación, grilla nativa del modelo ni promedio areal oficial. Para estudios cuantitativos de mayor precisión, se requiere una grilla nativa descargable y un método espacial reproducible (por ejemplo, ponderación por área de celda).

## 4 ter. Interpretación de radar y satélite

- **Radar:** mide ecos de precipitación/reflectividad dentro del alcance y geometría del radar. La capa RainViewer es un mosaico de terceros de cobertura parcial, con latencia y huecos.
- **Satélite ABI:** observa radiancias en bandas visibles e infrarrojas; vapor de agua, temperatura de brillo y estructura de nubes se interpretan según banda. No mide directamente lluvia en superficie.
- **GLM FED:** muestra densidad/extensión de flashes en celdas durante ventanas de cinco minutos; no equivale a una red terrestre que geolocaliza cada rayo.
- **Modelo/reanálisis:** aporta variables calculadas o reconstruidas en puntos/celdas. No es una observación directa.
- **Visores oficiales:** el SMN y SINARAME conservan la autoridad de sus productos y advertencias. La visualización experimental del Laboratorio no emite alertas ni sustituye avisos oficiales.

## 4. Reglas de cobertura y comparación

### Períodos completos

Para comparar totales anuales, utilizar años con doce meses disponibles, salvo que el análisis esté diseñado explícitamente para períodos parciales. Mostrar los años incompletos como tales y no compararlos directamente con años completos.

### Datos faltantes y duplicados

- No convertir datos ausentes en cero.
- Contabilizar faltantes y porcentaje de cobertura por estación y período.
- Detectar duplicados por clave de estación, variable y tiempo antes de agregar.
- No eliminar duplicados automáticamente sin determinar si son registros repetidos, observaciones distintas o revisiones.
- Conservar una copia de la fuente original y documentar cada transformación.

### Comparaciones espaciales

Una estación, una celda satelital de 0,1°, una celda ERA5 y un total departamental representan escalas distintas. Antes de compararlos, definir si se está contrastando el mismo período, variable, unidad, horario de corte y área representada. No interpolar ni promediar estaciones sin explicar el método y su incertidumbre.

### Hora y acumulación de precipitación

Registrar la zona horaria y el horario de corte de cada producto. Los acumulados diarios de productos satelitales pueden estar referidos a UTC; no asumir que coinciden con el día calendario local. Para acumulados de 24, 72 horas o 7/14/30 días, especificar si la ventana es móvil, el extremo temporal y el tratamiento de días incompletos.

### Unidades

Normalizar unidades solo después de confirmar su significado. Una tasa en mm/h no es lo mismo que una acumulación en mm. Si se integra una tasa en el tiempo, documentar el intervalo y el método de integración.

## 5. Análisis de extremos y eventos

Los acumulados anuales no describen la intensidad ni la frecuencia de los eventos diarios. Para estudiar extremos pueden considerarse índices ETCCDI como:

- Rx1day: máximo de precipitación en un día.
- Rx5day: máximo acumulado en cinco días consecutivos.
- R10mm y R20mm: cantidad de días que superan umbrales de 10 y 20 mm.
- CDD y CWD: duración máxima de períodos secos y húmedos consecutivos.

Antes de calcularlos, verificar continuidad, cobertura, definición de día, datos faltantes y homogeneidad. No aplicar umbrales universales sin explicar su pertinencia regional.

Para reconstruir un episodio de lluvia o inundación, combinar evidencia temporal y espacial: estaciones, estimaciones satelitales, campos interpolados, niveles hidrométricos, caudales, reportes oficiales y contexto territorial. La coincidencia temporal entre lluvia y crecida no demuestra por sí sola una relación causal; hay que considerar la cuenca, humedad antecedente, aportes aguas arriba, operación de embalses y tiempos de respuesta.

## 6. Calidad y confianza

Separar explícitamente:

1. **Integridad del archivo:** hash, descarga completa y formato legible.
2. **Validez estructural:** campos, tipos, rangos y esquema.
3. **Control de calidad automático:** valores sospechosos, duplicados, discontinuidades y consistencia.
4. **Validación de origen:** contraste con documentación del proveedor y metadatos de estación.
5. **Validación científica:** comparación independiente y evaluación de incertidumbre.

Una prueba de software exitosa acredita el comportamiento esperado del código, no la calidad meteorológica de todos los registros.

## 7. Variabilidad climática y causalidad

Índices como ONI describen condiciones oceánicas y atmosféricas de gran escala; no son mediciones de lluvia local. Alinear fechas y escalas temporales antes de comparar. Evaluar asociaciones, estacionalidad, desfases, autocorrelación y períodos comunes. Una correlación no demuestra que ENSO haya causado un evento particular.

## 8. Modelos y predicciones

Cualquier modelo experimental debe compararse con una línea base sencilla, evaluarse con datos no utilizados en el ajuste y separarse por evento y tiempo cuando corresponda. Registrar versión de datos, código, hiperparámetros, semillas, métricas y limitaciones. No publicar capacidad predictiva sin evaluación independiente ni presentar una salida experimental como alerta oficial.

## 9. Ficha mínima para cada investigación

Cada informe debe incluir:

- Pregunta, objetivo y alcance.
- Fuente original, organización, enlace, producto y versión.
- Fecha de consulta y período analizado.
- Cobertura geográfica, resolución espacial y temporal.
- Variables, unidades, zona horaria y horario de corte.
- Criterios de selección, limpieza y control de calidad.
- Duplicados, faltantes y decisiones de tratamiento.
- Fórmulas, scripts y pasos para reproducir.
- Resultados observados, incertidumbre y limitaciones.
- Interpretación: qué se puede afirmar y qué queda como hipótesis.
- Referencias y condiciones de uso.

## 10. Comunicación de resultados

Los textos del sitio deben separar cuatro niveles:

- **Qué investigamos:** pregunta y motivación.
- **Qué datos utilizamos:** fuente, escala y período.
- **Qué encontramos:** resultados realmente calculados.
- **Qué falta saber:** incertidumbres, limitaciones y próximos pasos.

No usar expresiones como “récord”, “tendencia”, “aumentó el riesgo” o “causó la inundación” si el método y la evidencia no permiten sostenerlas.
