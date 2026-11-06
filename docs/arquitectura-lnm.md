# Arquitectura del Laboratorio de Datos Meteorológicos

## Propósito

El Laboratorio reúne una interfaz pública de exploración, conjuntos de datos archivados, conectores y herramientas de investigación reproducible. Su identidad y nombre se mantienen: la evolución consiste en ampliar la capacidad de investigación dentro de las secciones existentes, mejorar la explicación de los métodos y hacer más trazables las fuentes y los hallazgos.

El alcance de exploración es nacional. El laboratorio combina fuentes puntuales argentinas con grillas satelitales y modelos globales. La cobertura nacional de una grilla no significa que existan observaciones de estación en cada localidad ni que todas las variables estén disponibles en cada región.

## Experiencia pública y componentes actuales

El frontend principal se publica como sitio estático desde `docs/` mediante GitHub Pages. La navegación actual integra:

1. **Panorama:** síntesis de la investigación, primera referencia ERA5 de Virasoro y hallazgos descriptivos disponibles.
2. **Precipitaciones:** exploración de totales anuales, anomalías, acumulados y climatología mensual de la serie archivada.
3. **Corrientes · registros diarios:** consulta del snapshot provincial disponible, con su cobertura y limitaciones.
4. **Laboratorio abierto:** consultas históricas por coordenadas/localidad y pronósticos multimodelo; incluye variables atmosféricas y series de estación cuando hay datos verificables.
5. **Centro de operaciones:** estado de las capacidades y catálogo de fuentes.
6. **Mapa de estaciones:** exploración geográfica de catálogos, coordenadas, filtros y referencias.
7. **Conjuntos de datos:** descripción y acceso a archivos utilizados.
8. **Preguntas climáticas:** agenda de investigación y estado de cada pregunta.
9. **Método y límites:** procedencia, escalas, criterios de calidad e interpretación.
10. **Participar:** recepción de observaciones comunitarias como insumos para formular preguntas, nunca como mediciones validadas automáticamente.

Estas secciones son partes de una misma experiencia. Las nuevas investigaciones deben incorporarse en ellas cuando corresponda, sin crear módulos redundantes ni duplicar consultas o catálogos.

## Arquitectura técnica

- `docs/`: HTML, CSS, JavaScript y archivos de datos públicos del frontend.
- `docs/datos/`: datasets y catálogos servidos por GitHub Pages.
- `backend/api/`: endpoints serverless de Vercel.
- `datos/`: fuentes archivadas, snapshots, metadatos y derivados de investigación.
- `investigaciones/`: preguntas, informes, scripts y resultados reproducibles.
- `fuentes/`: inventarios, metodología y auditorías de fuentes.
- `src/lnm/`: validadores y utilidades de catálogo, manifiestos y eventos.
- `schemas/`: contratos JSON.
- `research/events/`: registro trazable de eventos investigados.
- `research/neural/`: infraestructura experimental de aprendizaje automático.

Vercel aloja endpoints API; no publica una segunda copia del frontend. El sitio estático no debe depender de credenciales privadas ni exponer secretos en el navegador.

## Fuentes y tipos de información

El catálogo público está en `docs/datos/catalogo-fuentes.json`. Los estados significan:

- `archived`: existe una copia archivada en el repositorio; puede seguir pendiente la validación científica.
- `documented`: la fuente y su producto fueron documentados; no implica conector operativo.
- `not_integrated`: fuente candidata todavía no integrada.
- `investigation_required`: faltan verificaciones de acceso, cobertura, licencia o disponibilidad.

Los tipos de dato deben mantenerse separados:

- Observación puntual de estación.
- Registro administrativo o agregado territorial.
- Estimación satelital.
- Producto de radar.
- Reanálisis.
- Pronóstico numérico.
- Variable derivada o resultado estadístico.
- Observación hidrométrica, caudal o producto hidrológico modelado.

La resolución, el período, la hora de referencia, la unidad, el origen y la fecha de recuperación deben acompañar cada dataset. La hora de consulta de una API no equivale a la hora de observación.

## Expansión de capacidades dentro de las secciones existentes

La incorporación de nuevas fuentes debe mejorar preguntas ya presentes en la interfaz:

- **Precipitaciones:** acumulados diarios y multidiarios, comparación temporal y espacial, anomalías e índices de extremos cuando haya series aptas.
- **Mapa y conjuntos de datos:** distinguir cobertura de estaciones, estimaciones en grilla y áreas sin información; mostrar procedencia y período disponible.
- **Preguntas climáticas:** investigar variabilidad, estacionalidad, ENSO y extremos sin anticipar conclusiones.
- **Método y límites:** explicar incertidumbre, resolución, sesgos, datos faltantes y diferencias entre medición, estimación y modelo.
- **Contexto hidrológico:** relacionar episodios de lluvia con series de niveles y caudales cuando exista cobertura de estaciones; no inferir causalidad ni emitir alertas.

NASA GPM IMERG aporta estimaciones globales de precipitación de 0,1° (~10 km), con corridas Early, Late y Final de distinta latencia. GOES-19 (GOES East) ofrece observación geoestacionaria de Sudamérica mediante ABI y actividad eléctrica mediante GLM. SINARAME aporta infraestructura radar nacional, incluido el radar RMA19 de Ituzaingó; la disponibilidad de productos de radar para consumo directo debe verificarse. Open-Meteo ya está integrado en el Laboratorio abierto para consultas puntuales de reanálisis ERA5 y pronósticos; su Historical Forecast API permite evaluar pronósticos archivados. INA-SIyAH y SNIH aportan contexto hidrológico con coberturas de redes y cuencas, no una malla homogénea nacional. El catálogo distingue conectores activos de fuentes documentadas o pendientes.

## Calidad, procedencia y revisión

La integridad de un archivo, la validez estructural, el control de calidad automático y la validación meteorológica son niveles diferentes. Una ejecución exitosa de CI demuestra que el flujo computacional terminó según sus controles; no certifica por sí sola la calidad instrumental ni la interpretación científica.

Cada análisis debe poder responder:

1. ¿Qué pregunta intenta resolver?
2. ¿Qué fuente, producto y versión se utilizaron?
3. ¿Qué lugar y período representa?
4. ¿Qué unidad y frecuencia tienen los datos?
5. ¿Cómo se trataron duplicados, faltantes y valores atípicos?
6. ¿Qué cálculos y transformaciones se realizaron?
7. ¿Qué resultado se observó y qué no puede concluirse?
8. ¿Cómo se puede reproducir o revisar el resultado?

No convertir ausencias en cero, no mezclar escalas espaciales incompatibles, no presentar estimaciones como mediciones y no inferir causalidad a partir de correlaciones.

## Eventos e investigación experimental

El archivo de eventos comienza vacío deliberadamente. Cada candidato requiere intervalo temporal, región, fenómeno, evidencia trazable y estado de revisión (`candidate`, `reviewed`, `confirmed` o `rejected`). Una detección algorítmica no equivale a un fenómeno confirmado.

El entorno neuronal es experimental. No hay un modelo entrenado ni una predicción propia operativa. Los experimentos futuros requieren datos etiquetados, separación por evento y tiempo, líneas base, evaluación independiente y revisión manual antes de publicar resultados.

## Límites operativos actuales

- El dashboard histórico de Virasoro se basa en ERA5 para una celda de grilla, no en un pluviómetro local.
- El consolidado INTA-SIGA archivado procede de un proyecto comunitario y requiere revisión de duplicados, unidades, frecuencia y homogeneidad.
- Los datos diarios provinciales de Corrientes tienen cobertura desigual y el snapshot archivado no contiene filas diarias explícitamente etiquetadas como Virasoro.
- El conector AgroClima consulta fichas/observaciones recientes; no reemplaza una serie histórica diaria de lluvia.
- GOES ABI/GLM, GPM IMERG, SINARAME, CHIRPS, radiosondeos, INA-SIyAH y SNIH están documentados o en verificación; no se deben mostrar como capas activas hasta probar ingestión, latencia, cobertura y calidad. Open-Meteo sí ofrece consultas puntuales históricas y de pronóstico en Laboratorio abierto, no una visualización ráster nacional en tiempo real.
- El Laboratorio no es un sistema oficial de pronóstico ni de alerta hidrometeorológica.

## Validación

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m lnm sources
PYTHONPATH=src python -m lnm events
node --check docs/assets/js/lnm-center.js
node --check docs/assets/js/laboratorio-nacional.js
```
