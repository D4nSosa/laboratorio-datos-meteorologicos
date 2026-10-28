# Laboratorio de Datos Meteorológicos y Territoriales

Este repositorio reúne investigaciones que estoy haciendo a partir de datos meteorológicos y territoriales. El punto de partida es Gobernador Virasoro, Corrientes, pero la idea es ampliar la mirada hacia la provincia, el NEA y otras regiones de Argentina cuando los datos permitan comparaciones útiles.

Me interesa entender mejor qué muestran los registros de lluvia, cómo cambian según el lugar y el período, y qué se puede decir —y qué no— cuando los comparamos con información climática y territorial.

No busco publicar gráficos sueltos. Cada investigación debe explicar de dónde salen los datos, cómo los procesé, qué encontré y cuáles son las limitaciones. Cuando sea posible, voy a dejar también los scripts para que otra persona pueda repetir el análisis.

## Investigaciones

1. **Precipitaciones en Gobernador Virasoro:** análisis local y revisión de fuentes disponibles.
2. **Corrientes y el NEA:** comparación regional, cuidando que las zonas y los períodos sean comparables.
3. **Contexto nacional:** ampliar el análisis a otras regiones de Argentina con una metodología consistente.
4. **Lluvia y variabilidad climática:** explorar relaciones posibles con fenómenos como El Niño y La Niña, sin confundir coincidencia con causalidad.

Estos temas son una hoja de ruta, no resultados anticipados. Cada etapa se publicará cuando los datos, los cálculos y las conclusiones estén revisados.

## Cómo trabajo

- Identifico la fuente y la fecha de consulta de cada conjunto de datos.
- Reviso cobertura temporal, ubicación, unidades y datos faltantes.
- Separo mediciones de estaciones, registros administrativos y productos de reanálisis. No son equivalentes.
- Documento los cálculos y las decisiones de limpieza.
- Comparo períodos solo cuando la cobertura y el método lo permiten.
- Evito completar valores faltantes con cifras inventadas o presentar estimaciones como mediciones.
- Distingo los resultados observados de las hipótesis y de cualquier modelo experimental.
- Publico los scripts utilizados y explico cómo ejecutarlos cuando la investigación esté lista.

El código y el análisis pueden desarrollarse con apoyo de herramientas de software y modelos de IA. Las fuentes, los cálculos y las conclusiones deben poder revisarse por separado.

## Estado del proyecto

La primera etapa incluye un análisis descriptivo de la base pública del departamento de Santo Tomé y una línea base ERA5 para el entorno de Gobernador Virasoro (1991–2025), ejecutada mediante GitHub Actions. El [informe documental de Virasoro](investigaciones/01-precipitacion-virasoro/informe_documental_virasoro.md) reúne la evidencia publicada y sus límites. ERA5 no equivale a mediciones de estación: para concluir sobre tendencias locales todavía se necesita conseguir y validar registros primarios continuos. Los [resultados preliminares de Santo Tomé](investigaciones/01-precipitacion-virasoro/resultados_santo_tome.md) se mantienen separados como contexto regional.

El laboratorio está en etapa de investigación. Los resultados y documentos públicos se incorporarán de manera gradual, una vez revisados. Mientras una investigación no esté terminada, sus preguntas y tareas pendientes no deben leerse como conclusiones.

## Autoría

Proyecto de investigación personal de **DAN SOSA**, desde Gobernador Virasoro, Corrientes, Argentina.

Sitio personal: https://dansosa.vercel.app

