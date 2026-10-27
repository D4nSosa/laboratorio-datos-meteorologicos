# Fuentes y metodología

Este documento reúne criterios generales para elegir, revisar y citar los datos del laboratorio. Cada investigación debe agregar las fuentes concretas que utilizó, la fecha de consulta, las variables y el período analizado.

## Antes de comparar datos

No todos los registros de lluvia representan lo mismo. Una estación meteorológica mide en un punto; un resumen departamental puede reunir información de distintas estaciones o localidades; un producto de reanálisis combina observaciones con un modelo físico de la atmósfera. Pueden servir para preguntas diferentes, pero no deben mezclarse como si fueran una sola serie.

Antes de calcular tendencias o anomalías, voy a revisar:

- Qué organismo o equipo publicó los datos y cuál es la fuente original.
- Qué lugar representa cada registro y cuál es su unidad geográfica.
- Qué período cubre y si hay meses o años incompletos.
- Si cambió la estación, el método, la cobertura territorial o el procesamiento.
- Si los datos son mediciones, estimaciones, promedios o resultados de un modelo.
- Qué licencia o condiciones rigen la reutilización y redistribución.

## Fuentes a consultar

Estas son fuentes de referencia para investigar. Su inclusión en esta lista no significa que todas se hayan usado en una investigación ni que se haya descargado información de ellas. Cada informe debe indicar cuáles se utilizaron realmente.

- **Servicio Meteorológico Nacional (SMN):** https://www.smn.gob.ar/
- **Instituto Nacional de Tecnología Agropecuaria (INTA):** https://www.argentina.gob.ar/inta
- **Instituto Geográfico Nacional (IGN):** https://www.ign.gob.ar/
- **Open-Meteo, documentación de Historical Weather API:** https://open-meteo.com/en/docs/historical-weather-api
- **NOAA Climate Prediction Center, Oceanic Niño Index (ONI):** https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/
- **NOAA Climate Prediction Center, Relative Oceanic Niño Index (RONI):** https://cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/

También pueden incorporarse bases provinciales, publicaciones técnicas y conjuntos de datos abiertos, siempre que se pueda identificar su procedencia y evaluar su cobertura.

## Criterios de análisis

### Períodos completos

Para comparar totales anuales, se usarán años con los doce meses disponibles, salvo que el análisis indique expresamente otra cosa. Los años parciales se mostrarán como parciales y no se compararán directamente con años completos.

### Datos faltantes

No voy a convertir meses sin datos en cero ni completar valores faltantes sin un método explícito y una justificación. Si se realiza alguna imputación como parte de un análisis, debe quedar identificada y separada de los datos originales.

### Comparaciones geográficas

Una cifra de Gobernador Virasoro no equivale automáticamente a un total del departamento Santo Tomé ni a un promedio de la provincia de Corrientes. Las diferencias de cobertura, ubicación y método deben quedar explicadas.

### Promedios, anomalías y extremos

Cada cálculo debe indicar el período de referencia y la fórmula utilizada. Para hablar de récords, primero hay que verificar que la serie sea comparable a lo largo del tiempo. Si eso no está confirmado, la conclusión se limita a lo observado en el conjunto de datos utilizado.

### Variabilidad climática

Los índices como ONI describen condiciones oceánicas y atmosféricas a escala regional; no son mediciones de lluvia local. Una coincidencia temporal entre un índice y las precipitaciones no demuestra por sí sola que uno haya causado las otras.

### Modelos y predicciones

Cualquier modelo experimental debe compararse con una referencia sencilla y evaluarse con datos que no se hayan usado para ajustarlo. No se publicarán afirmaciones de capacidad predictiva sin una evaluación adecuada.

## Qué debe documentar cada investigación

- Fuente original, enlace y fecha de consulta.
- Cobertura espacial y temporal.
- Variables, unidades y reglas de selección.
- Limpieza y transformaciones aplicadas.
- Fórmulas y decisiones metodológicas.
- Scripts realmente usados para producir los resultados.
- Resultados principales, incertidumbres y limitaciones.
- Licencia o condiciones de uso de los datos, cuando estén disponibles.
