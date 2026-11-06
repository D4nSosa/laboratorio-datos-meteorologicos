# Arquitectura del Laboratorio de Datos Meteorológicos

## Propósito

El Laboratorio reúne una interfaz pública de exploración, conjuntos de datos archivados, conectores y herramientas de investigación reproducible. Su identidad y nombre se mantienen: la evolución consiste en ampliar la capacidad de investigación dentro de las secciones existentes, mejorar la explicación de los métodos y hacer más trazables las fuentes y los hallazgos.

El alcance geográfico crece de forma progresiva. La cobertura nacional se construye por fuente, variable, período y región; no se presume que una red o producto tenga cobertura homogénea en todo el país.

## Experiencia pública y componentes actuales

El frontend principal se publica como sitio estático desde `docs/` mediante GitHub Pages. La navegación actual integra:

1. **Panorama:** síntesis de la investigación, primera referencia ERA5 de Virasoro y hallazgos descriptivos disponibles.
2. **Precipitaciones:** exploración de totales anuales, anomalías, acumulados y climatología mensual de la serie archivada.
3. **Corrientes · registros diarios:** consulta del snapshot provincial disponible, con su cobertura y limitaciones.
4. **Laboratorio abierto:** consultas históricas de ERA5 por coordenadas, pronóstico multimodelo y acceso al consolidado INTA-SIGA.
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

NASA GPM IMERG está documentado como producto satelital global de precipitación de 0,1° (~10 km), con productos Early, Late y Final y latencias distintas. INA-SIyAH ofrece servicios de series observadas y simuladas y capas de la Cuenca del Plata; SNIH publica datos históricos consolidados y registros de tiempo útil que pueden ser crudos y no validados. Estas fuentes figuran en el catálogo, pero aún no constituyen conectores operativos del Laboratorio.

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
- GPM IMERG, INA-SIyAH y SNIH están documentados, pero no integrados como nuevas series operativas en el frontend.
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
