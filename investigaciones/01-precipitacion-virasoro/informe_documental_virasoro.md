# Investigación de precipitaciones en Gobernador Virasoro — informe de resultados y límites

**Corte de investigación documental:** 28 de octubre de 2026  
**Estado:** revisión documental y primera serie de reanálisis procesada. La investigación queda lista para una primera devolución técnica, pero no demuestra una tendencia climática local ni reemplaza una serie pluviométrica primaria continua.

## Pregunta

¿Qué muestran las referencias históricas disponibles sobre las precipitaciones de Gobernador Virasoro y qué podemos concluir al compararlas con un reanálisis de varias décadas?

## 1. Serie ERA5 consultada para el entorno urbano

Se consultó Open-Meteo Historical Weather API, modelo ERA5, variable diaria `precipitation_sum`, del 1 de enero de 1991 al 31 de diciembre de 2025. La consulta solicitó latitud -28,05 y longitud -56,02. La API devolvió la celda ERA5 centrada en -28,00, -56,00, con elevación reportada de 133 m. Se recibieron los 12.784 días del intervalo sin valores faltantes; la descarga y los scripts pasaron el flujo automatizado de validación de GitHub Actions.

ERA5 es un reanálisis: combina observaciones con modelos y representa una celda espacial, no el pluviómetro de una dirección concreta. La serie sirve como referencia espacialmente consistente, pero no debe presentarse como precipitación observada en la ciudad.

| Indicador ERA5 | Resultado |
|---|---:|
| Período | 1991–2025 |
| Años completos | 35 |
| Media anual | 1.786,94 mm |
| Mediana anual | 1.783,50 mm |
| Mínimo anual | 2020: 1.126,80 mm |
| Máximo anual | 2002: 2.588,70 mm |
| 2023 | 1.910,80 mm |
| 2024 | 1.935,00 mm |
| 2025 | 1.829,20 mm |

Promedios mensuales del reanálisis (mm): enero 158,28; febrero 143,28; marzo 139,73; abril 170,97; mayo 136,74; junio 116,65; julio 113,01; agosto 95,03; septiembre 157,13; octubre 216,57; noviembre 164,90; diciembre 174,65.

Los valores anuales y mensuales se guardan en `datos/virasoro_era5/`; los metadatos incluyen coordenadas solicitadas y devueltas, período, variable y fecha de consulta. Los gráficos se generan en PNG y SVG. El resultado de ERA5 no se usa para corregir ni reemplazar los registros locales.

Archivos incorporados al repositorio:
- [Totales anuales ERA5 (CSV)](../../datos/virasoro_era5/precipitacion_anual.csv)
- [Climatología mensual ERA5 (CSV)](../../datos/virasoro_era5/climatologia_mensual.csv)
- [Resumen estadístico (JSON)](../../datos/virasoro_era5/resumen_estadistico.json)
- [Metadatos de la consulta (JSON)](../../datos/virasoro_era5/metadatos.json)
- [Gráfico de precipitación anual (SVG)](graficos/precipitacion_anual_era5.svg)
- [Gráfico de climatología mensual (SVG)](graficos/climatologia_mensual_era5.svg)

La serie diaria completa y los totales mensuales se generan en cada ejecución automatizada y quedan en el artefacto de validación de GitHub Actions; el repositorio conserva los agregados principales para facilitar la revisión sin incorporar el CSV diario de mayor tamaño.

## 2. Registros y referencias publicados para Virasoro

Las fuentes encontradas no componen una serie continua homogénea; describen estaciones, períodos y métodos diferentes.

| Período o referencia | Valor publicado | Procedencia y límite |
|---|---:|---|
| 1950–2000 | Ciclo mensual histórico de precipitación y temperatura | Figura atribuida a la estación del Instituto Agrotécnico Víctor Navajas Centeno (IAVNC) en una tesis de la UNNE. La figura no contiene la serie mensual original. |
| Promedio 1992–1999 | 1.907,7 mm/año | Tabla secundaria que atribuye los valores al IAVNC. Requiere comprobar la publicación primaria y la metodología. |
| Tabla climatológica de la UNNE | 1.419 mm/año | Atlas geográfico con medias mensuales; el período exacto de cálculo no quedó confirmado. No se puede tratar automáticamente como normal 1991–2020. |
| Diez años previos a 2022 | 1.923 mm/año | Promedio atribuido al Centro Meteorológico del IAVNC en un trabajo académico; no se detallan allí los años exactos ni la serie fuente. |
| Junio–diciembre de 2018 | 954,2 mm en siete meses | Suma de los valores mensuales publicados en un trabajo de la UNNE, procedentes de una estación cercana a los lotes en Virasoro. No es un total anual. |
| 2019 | 1.718 mm | Registro in situ de un establecimiento (Granja Santa Marta), reproducido en un trabajo de la UNNE. |
| 2020 | 1.498 mm | Mismo establecimiento y fuente académica. |
| 2021 | 1.557 mm | Mismo establecimiento y fuente académica. |
| 2022 | 1.761 mm | Mismo establecimiento y fuente académica. |
| 2023 | 2.609,3 mm | Cifra local reportada por prensa, atribuida a fuentes provinciales; falta verificar la planilla primaria. |
| 2024 | 2.346 mm | Cifra local reportada por prensa, atribuida a fuentes provinciales; falta verificar la planilla primaria. |
| Enero–mayo de 2025 | 925,6 mm | Cifra publicada por prensa para Virasoro; se debe verificar la fuente primaria y la fecha de corte. |
| Mayo de 2025 | 506,4 mm | Cifra publicada por prensa para Virasoro; no se presenta aquí como récord oficial verificado. |

Fuentes académicas y documentales:
- Batalla, A. G. (2019), tesis de Maestría en Producción Vegetal, UNNE: https://repositorio.unne.edu.ar/bitstream/handle/123456789/47752/RIUNNE_FCA_TM_Batalla_AG.pdf?isAllowed=y&sequence=1
- Trabajo final de la UNNE con registros del establecimiento Granja Santa Marta (2019–2022): https://repositorio.unne.edu.ar/bitstream/handle/123456789/56560/RIUNNE_FCA_FG_Decoppet_MF.pdf?isAllowed=y&sequence=1
- Trabajo final de la UNNE con datos de la estación cercana a los lotes en 2018: https://repositorio.unne.edu.ar/bitstream/handle/123456789/58481/RIUNNE_FCA_FG_Venhaus_Held_S.pdf?sequence=1
- Atlas geográfico de la provincia de Corrientes, UNNE: https://repositorio.unne.edu.ar/xmlui/bitstream/handle/123456789/56284/RIUNNE_FHUM_AR_Bruniard-Alberto-Falcon.pdf?isAllowed=y&sequence=1
- Tabla secundaria con referencia al IAVNC y período 1992–1999: https://mexpedia.org/index.php/Gobernador_Virasoro
- Instalación de estaciones completas de la red ACPA en Virasoro, informada en diciembre de 2013: https://www.ellitoral.com.ar/corrientes/2013-12-16-15-21-0-amplian-la-red-de-estaciones-meteorologicas-en-puntos-estrategicos
- Cifras de lluvia de 2023–2024 y episodio de mayo de 2025, reportadas por prensa: https://www.ellitoral.com.ar/sociedad/2025-1-11-22-5-0--cuanto-llovio-en-corrientes-durante-el-2024 y https://www.ellitoral.com.ar/sociedad/2025-5-29-21-32-0-mayo-cierra-con-un-acumulado-record-de-lluvias-en-algunas-zonas-alcanzo-los-560-mm

## 3. Qué significa la comparación con ERA5

Los acumulados locales reportados para 2023 y 2024 (2.609,3 y 2.346 mm) son superiores a los de la celda ERA5 para esos años (1.910,8 y 1.935,0 mm). En 2025, la cifra periodística para enero–mayo y mayo también difiere de la celda de reanálisis. Esto no demuestra por sí solo que una fuente esté equivocada: las fuentes pueden representar puntos y áreas distintas, instrumentos diferentes, períodos de corte y procedimientos de agregación diferentes. La discrepancia es precisamente una razón para no mezclar ni sustituir series sin validación.

Como contexto regional, el análisis de la base pública del Departamento de Economía Agraria para el departamento de Santo Tomé obtuvo 1.781,40 mm de media anual en 32 años completos (1993–2025, excluyendo 1999 y 2026 por incompletos). Esa serie se documenta por separado y no se usa como medición de Virasoro.

## 4. Estaciones y acceso a registros primarios

La documentación histórica identifica al IAVNC y a la estación ACPA como vías concretas para buscar planillas originales. Las notas de 2013 confirman que se instaló una estación meteorológica completa en Virasoro dentro de una red provincial vinculada con ACPA y el Ministerio de Producción.

El ICAA anunció el 27 de octubre de 2026 un mapa que integra estaciones de varias redes y permite consultar datos en tiempo real y registros históricos, pero el mapa necesita JavaScript. La versión textual accesible no permitió confirmar qué estación de Virasoro está disponible ni qué período puede descargarse. El archivo histórico accesible en la página tradicional del ICAA corresponde a la estación de Corrientes Capital, por lo que no reemplaza la serie local.

- Aviso del ICAA: https://icaa.gov.ar/disponible-acceso-directo-a-datos-de-estaciones-hidro-meteorologicas-en-tiempo-real/
- Instructivo del mapa: https://icaa.gov.ar/instructivo-acceso-estacion-icaa/
- Registro de la estación automática del ICAA en Corrientes Capital: https://icaa.gov.ar/registro-de-datos-meteorologicos/
- Portal SNIH: https://snih.hidricosargentina.gob.ar/ (distingue registros crudos a tiempo útil de datos históricos procesados).

## 5. Conclusiones que sí se sostienen

1. Virasoro cuenta con referencias climatológicas de larga data y con registros locales publicados de distintos establecimientos y estaciones.
2. ERA5 ofrece una serie completa y reproducible para 1991–2025 en la celda que cubre el entorno urbano. Sus resultados son una estimación de reanálisis, no mediciones de pluviómetro.
3. Los datos locales publicados para 2019–2025 muestran variabilidad entre años, pero los períodos y las fuentes no son homogéneos.
4. Las cifras históricas de 1.419, 1.907,7 y 1.923 mm/año no deben promediarse entre sí: los períodos, el origen y la metodología no están suficientemente documentados para tratarlas como equivalentes.
5. Con lo disponible no corresponde afirmar una tendencia climática de largo plazo para Virasoro ni atribuir los años lluviosos exclusivamente a El Niño. Hace falta una serie observada consistente y un análisis estadístico específico.

## 6. Estado de cierre

La primera revisión documental y la línea base ERA5 ya están procesadas y el código pasó una ejecución automatizada en GitHub Actions. Eso permite cerrar una **primera fase exploratoria** sin presentar resultados como definitivos.

La limitación pendiente para una investigación local concluyente es conseguir los registros primarios (idealmente diarios o mensuales) de IAVNC/ACPA/Ministerio de Producción o confirmar una estación del SNIH con cobertura y metadatos adecuados. Esa gestión puede requerir contacto directo con los organismos o el Instituto Agrotécnico; no puede resolverse solamente reinterpretando las publicaciones disponibles.

Por lo tanto, este informe cierra la búsqueda documental abierta en esta fase, pero no afirma que ya se haya demostrado una tendencia climática local. Cualquier ampliación futura deberá partir de una serie observada validada, compararla con ERA5 en el período común y documentar cambios de estación, faltantes y métodos.
