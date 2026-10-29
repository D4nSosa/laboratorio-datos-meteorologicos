# Laboratorio de Datos Meteorológicos y Territoriales

Este repositorio reúne investigaciones personales sobre datos meteorológicos y territoriales. El punto de partida es Gobernador Virasoro, Corrientes, con la intención de ampliar el análisis a la provincia, el NEA y otras regiones cuando los datos permitan comparaciones útiles.

Cada investigación debe explicar de dónde salen los datos, cómo se procesaron, qué se encontró y cuáles son las limitaciones. Cuando sea posible, se publican también los scripts para repetir los análisis.

## Investigaciones

1. **Precipitaciones en Gobernador Virasoro:** análisis local y revisión de fuentes disponibles.
2. **Corrientes y el NEA:** comparación regional con cobertura y períodos comparables.
3. **Contexto nacional:** ampliar el análisis a otras regiones con metodología consistente.
4. **Lluvia y variabilidad climática:** explorar relaciones posibles con ENSO sin confundir coincidencia con causalidad.

Estas líneas son una hoja de ruta, no resultados anticipados.

## Criterios de trabajo

- Identificar la fuente y fecha de consulta.
- Revisar cobertura temporal, ubicación, unidades, faltantes y consistencia.
- Separar mediciones de estaciones, registros administrativos y reanálisis.
- Documentar cálculos y decisiones de limpieza.
- No completar valores faltantes con cifras inventadas ni presentar estimaciones como mediciones.
- Distinguir resultados observados, hipótesis y modelos experimentales.

El código y el análisis pueden desarrollarse con apoyo de herramientas de software e IA. Las fuentes, cálculos y conclusiones deben poder revisarse por separado.

## Estado del proyecto

La primera etapa incluye el análisis descriptivo de la base pública del departamento de Santo Tomé y una línea base ERA5 para el entorno de Gobernador Virasoro (1991–2025). El [informe documental de Virasoro](investigaciones/01-precipitacion-virasoro/informe_documental_virasoro.md) reúne la evidencia publicada y sus límites. ERA5 no equivale a mediciones de estación: para concluir sobre tendencias locales todavía se necesita conseguir y validar registros primarios continuos. Los [resultados preliminares de Santo Tomé](investigaciones/01-precipitacion-virasoro/resultados_santo_tome.md) se mantienen separados como contexto regional.

### Dataset nacional descargado

Se incorporó el consolidado público de observaciones SIGA-INTA para 182 estaciones, con 1.177.258 filas y 38 columnas. El archivo original de 151 MB fue verificado mediante SHA-256 y archivado comprimido en [estaciones-observaciones.csv.gz](datos/fuentes-externas/inta-siga/estaciones-observaciones.csv.gz). La [metadata de validación](datos/fuentes-externas/inta-siga/observaciones-metadata.json) documenta integridad y estructura; no implica que cada observación esté validada instrumentalmente ni que exista cobertura exhaustiva nacional.

El catálogo y la procedencia están en [INTA-SIGA](datos/fuentes-externas/inta-siga/README.md). El [informe de descargas](fuentes/estado_descargas_dataset_2026-10-29.md) separa lo ya archivado de las fuentes pendientes. Se está automatizando un resumen de cobertura por estación/año y un recorte de estaciones cercanas a Virasoro; sus totales son exploratorios hasta confirmar unidades y frecuencia.

El flujo automatizado valida la estructura de datos, ejecuta los scripts y conserva artefactos de cada ejecución. Una ejecución exitosa acredita reproducibilidad computacional del flujo, no validación científica independiente.

## Reproducibilidad y licencia

Se usa Python 3.12 y las dependencias declaradas en `requirements.txt` están fijadas a versiones concretas. Consultá los archivos de metodología para fuentes, cobertura y limitaciones. La licencia MIT de la raíz aplica al código original de este repositorio, no a datos ni materiales de terceros; para esos materiales rigen sus condiciones originales.

## Autoría

Proyecto personal de **DAN SOSA**, desde Gobernador Virasoro, Corrientes, Argentina.

Sitio personal: https://dansosa.vercel.app
