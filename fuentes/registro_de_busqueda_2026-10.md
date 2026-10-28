# Registro de búsqueda — 28 de octubre de 2026

Este registro deja constancia de las fuentes consultadas y de lo que permiten afirmar. No es una bibliografía exhaustiva ni reemplaza la verificación de cada serie descargada.

## 1. Reanálisis de precipitación

**Open-Meteo Historical Weather API / ERA5**  
https://open-meteo.com/en/docs/historical-weather-api

La documentación indica que ERA5 ofrece datos horarios desde 1940, con resolución espacial aproximada de 0,25° (~25 km), y recomienda usar ERA5 o ERA5-Land de forma consistente para análisis de varias décadas. Los reanálisis combinan observaciones con modelos y rellenan espacios mediante estimaciones; por eso no equivalen a mediciones de pluviómetro en Virasoro.

La consulta de datos debe registrar las coordenadas solicitadas y las coordenadas de la celda devuelta. La serie inicial propuesta cubre 1991–2025 para evitar comparar un año parcial con años cerrados. El script comprueba que estén todos los días del intervalo antes de agregar.

## 2. Observaciones oficiales argentinas

**Servicio Meteorológico Nacional — observaciones**  
https://ws2.smn.gob.ar/observaciones

Es un punto de entrada oficial para observaciones. La búsqueda no permite afirmar, por sí sola, que esté disponible una serie diaria histórica completa de una estación en Gobernador Virasoro. Hay que identificar estación, ubicación, período, faltantes y método antes de usarla como referencia.

**Sistema Nacional de Información Hídrica**  
https://snih.hidricosargentina.gob.ar/

Publica datos hidrológicos históricos consolidados y datos a tiempo útil. Su advertencia distingue registros crudos sin validar de datos procesados. Puede ser útil para contextualizar eventos hidrológicos, pero no se debe confundir una medición de nivel/caudal con precipitación local.

## 3. Variabilidad climática y ENSO

**NOAA Climate Prediction Center — Oceanic Niño Index (ONI), versión 6**  
https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/

El ONI se calcula como una media móvil de tres meses de anomalías de temperatura superficial del mar en la región Niño 3.4. NOAA informa que el seguimiento operativo oficial pasó a utilizar RONI en 2026; ONI sigue siendo una referencia histórica, pero conviene registrar la versión de la serie y no mezclar versiones sin anotarlo. Los trimestres móviles se solapan: no son observaciones independientes ni una medida directa de la lluvia en Corrientes.

**NOAA — explicación del Relative Oceanic Niño Index (RONI)**  
https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/pdf/roni-info.pdf

RONI compara las anomalías de la región ENSO con las de los trópicos globales. Si la investigación compara ENSO y lluvia, debe decidir previamente qué índice se usa, respetar sus períodos y probar relaciones con desfases razonables sin interpretar correlación como causalidad.

**IPCC AR6 WGI — Atlas, sección América del Sur**  
https://www.ipcc.ch/report/ar6/wg1/chapter/atlas/

El IPCC describe múltiples factores de variabilidad climática en Sudamérica, incluido ENSO, y señala diferencias en la capacidad de los modelos para representar patrones regionales. La evidencia general de Sudamérica no debe presentarse como una conclusión específica para Virasoro sin análisis local.

## 4. Registros locales citados por prensa

- El Litoral, 11 de enero de 2025: https://www.ellitoral.com.ar/sociedad/2025-1-11-22-5-0--cuanto-llovio-en-corrientes-durante-el-2024
- El Litoral, 29 de mayo de 2025: https://www.ellitoral.com.ar/sociedad/2025-5-29-21-32-0-mayo-cierra-con-un-acumulado-record-de-lluvias-en-algunas-zonas-alcanzo-los-560-mm

Las notas atribuyen cifras a fuentes provinciales. Hasta encontrar y comprobar el registro primario, esas cifras deben citarse como datos reportados por la nota, con el período y la localidad exactos. No deben combinarse directamente con ERA5 ni con totales del departamento de Santo Tomé.

## Criterios de inclusión de fuentes

Para cada dataset registrar: organismo responsable, enlace, variable, unidad, cobertura geográfica, período, resolución temporal/espacial, fecha de consulta, licencia, metodología y faltantes conocidos. Si alguno de estos datos no se puede confirmar, indicarlo explícitamente y no presentar el dataset como una medición observada local.


## 5. Base mensual del Departamento de Economía Agraria

**Registro y Seguimiento de Precipitaciones — Ministerio de Producción de Corrientes**

- Tablero: https://deaeconomiactes.github.io/Precipitaciones-Lluvias/
- Repositorio: https://github.com/deaeconomiactes/Precipitaciones-Lluvias
- Archivo consultado: https://github.com/deaeconomiactes/Precipitaciones-Lluvias/blob/main/data/rainfall.json
- Fecha de consulta: 28 de octubre de 2026.

El README del proyecto fuente identifica al Departamento de Economía Agraria y explica que `data/rainfall.json` contiene la base mensual histórica por año y departamento. También advierte que el tablero combina registros mensuales con acumulados derivados de datos diarios cuando falta una carga mensual específica. Para evitar mezclar métodos, este análisis tomó directamente los 12 valores mensuales de cada registro de Santo Tomé y recalculó el total anual a partir de esos valores. No usó acumulados diarios mensualizados ni datos de otros departamentos.

La base contiene 34 filas para Santo Tomé entre 1993 y 2026. Se excluyeron 1999 (10 meses con valor) y 2026 (enero a mayo) de los totales anuales comparables. Quedaron 32 años completos. Las cifras derivadas y los gráficos se encuentran en `investigaciones/01-precipitacion-virasoro/resultados_santo_tome.md`.

Esta serie representa el departamento, no una estación meteorológica puntual en Gobernador Virasoro. La atribución institucional procede de la documentación del repositorio fuente; antes de publicar conclusiones locales, se debe buscar el registro primario que respalde las cifras reportadas por prensa.


## 6. Antecedentes locales de Virasoro y acceso provincial a estaciones

**Universidad Nacional del Nordeste — tesis sobre fenología de yerba mate en Virasoro**

https://repositorio.unne.edu.ar/bitstream/handle/123456789/47752/RIUNNE_FCA_TM_Batalla_AG.pdf?isAllowed=y&sequence=1

La tesis de Andrés Gustavo Batalla (2019) indica que la estación meteorológica del Instituto Agrotécnico Víctor Navajas Centeno (IAVNC) registró precipitación y temperatura media mensual histórica para el período 1950–2000 (figura 3). También describe condiciones climáticas locales y cita registros de temperatura de 1993–2003. En los resultados menciona datos de precipitación de la estación ACPA, ubicada en el Instituto Agrotécnico, para agosto de 2015 a julio de 2018. Es una referencia académica para localizar la serie original; la figura publicada no sustituye los datos mensuales o diarios de origen.

**Instituto Correntino del Agua y del Ambiente (ICAA) — acceso a estaciones**

https://icaa.gov.ar/disponible-acceso-directo-a-datos-de-estaciones-hidro-meteorologicas-en-tiempo-real/

Aviso fechado el 27 de octubre de 2026. Informa acceso directo a datos en tiempo real de estaciones de varias redes en Corrientes. Próximo paso: revisar el mapa y comprobar estación, ubicación, variables, período de historia descargable y estado de validación antes de incorporarla al análisis.

**Criterio:** hasta confirmar estación, cobertura y datos primarios, no presentar estos antecedentes como si ya se hubiera obtenido una serie completa de Virasoro.

## 7. Otra referencia académica con valores locales de 2019–2022

**UNNE — trabajo final de graduación sobre una estrategia de manejo en yerba mate en Virasoro**

https://repositorio.unne.edu.ar/bitstream/handle/123456789/56560/RIUNNE_FCA_FG_Decoppet_MF.pdf?isAllowed=y&sequence=1

El trabajo cita al Centro Meteorológico del Instituto Agrotécnico Víctor Navajas Centeno (2022), que reporta un promedio anual de 1.923 mm para los diez años anteriores; el documento no detalla allí los años exactos ni la serie utilizada. Además, presenta un climograma para el establecimiento Granja Santa Marta, en Gobernador Virasoro, con precipitaciones anuales de 1.718 mm (2019), 1.498 mm (2020), 1.557 mm (2021) y 1.761 mm (2022). El texto indica que la precipitación se tomó de registros in situ del establecimiento, mientras que la temperatura procede de la Red de Centrales de la Bolsa de Cereales. Por lo tanto, son datos locales de un establecimiento y no deben etiquetarse como una serie oficial de la estación urbana ni combinarse automáticamente con el departamento de Santo Tomé o ERA5. El documento es una fuente secundaria que reproduce los valores; el siguiente paso sería solicitar o localizar las planillas originales y confirmar acumulación, días faltantes y criterios de cada campaña.

**Referencia climatológica histórica tabulada para Gobernador Virasoro**

https://repositorio.unne.edu.ar/xmlui/bitstream/handle/123456789/56284/RIUNNE_FHUM_AR_Bruniard-Alberto-Falcon.pdf?isAllowed=y&sequence=1

El documento contiene una tabla de precipitación para la estación “Gobernador Virasoro”: media mensual y anual de 1.419 mm, además de valores máximos y mínimos. En el fragmento consultado no queda suficientemente establecido el período exacto que sustenta la tabla ni la continuidad de la estación. Se registra como referencia climatológica por verificar, no como base apta para calcular tendencias hasta confirmar período, procedencia y definición de máximos/mínimos.

**Lectura conjunta:** ahora hay al menos tres pistas documentales distintas para Virasoro —una figura histórica 1950–2000 citada en una tesis, registros locales de establecimiento para 2019–2022 y cifras difundidas por prensa para 2023–2025—, pero todavía no forman una única serie homogénea. No se deben concatenar ni calcular tendencias mezclándolas sin validar estación, ubicación, período y método.
