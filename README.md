# Laboratorio de Datos Meteorológicos

**Observación, análisis e investigación de fenómenos meteorológicos y su contexto territorial.**

El Laboratorio de Datos Meteorológicos es un proyecto abierto de investigación y desarrollo iniciado desde Gobernador Virasoro, Corrientes, Argentina. Su propósito es reunir, explorar y analizar información meteorológica de distintas escalas para formular preguntas, contrastar evidencia y documentar hallazgos reproducibles.

La expansión geográfica es progresiva: partimos de investigaciones locales y regionales y ampliamos el alcance a otras zonas del país cuando existen fuentes con cobertura, períodos y metadatos suficientes. La cobertura nacional es un objetivo de investigación, no una afirmación de que todas las variables o estaciones estén disponibles en todo el territorio.

**Sitio público:** [Explorador interactivo](https://d4nsosa.github.io/laboratorio-datos-meteorologicos/explorador-interactivo.html)

## Qué investigamos

El trabajo se organiza alrededor de preguntas que pueden abordarse con las capacidades existentes:

- Cómo varían las precipitaciones entre años, estaciones y regiones.
- Dónde existen registros meteorológicos y qué continuidad temporal tienen.
- Qué diferencias aparecen entre mediciones de estaciones, agregados territoriales, estimaciones satelitales y reanálisis.
- Cómo caracterizar episodios de lluvia intensa con datos diarios y subdiarios.
- Qué contexto meteorológico e hidrológico acompaña a crecidas, anegamientos y sequías.
- Qué relaciones estadísticas pueden explorarse entre precipitación, estacionalidad e índices de variabilidad climática como ENSO.

Estas preguntas no anticipan resultados. Cada conclusión debe estar respaldada por datos identificables, un método explícito y una revisión de sus limitaciones.

## El laboratorio hoy

La interfaz pública reúne las siguientes capacidades existentes:

- **Panorama e investigación de precipitaciones:** primera referencia de 35 años de ERA5 para la celda de grilla próxima a Gobernador Virasoro (1991–2025), con totales anuales, climatología mensual y lectura descriptiva.
- **Exploración de series:** filtros temporales, anomalías y acumulados de la serie anual archivada.
- **Registros diarios de Corrientes:** explorador del conjunto publicado por el Departamento de Economía Agraria. El snapshot archivado contiene 5.186 filas, 25 departamentos y fechas entre 2023-01-01 y 2026-10-25; no incluye registros diarios etiquetados explícitamente como Virasoro.
- **Mapa de estaciones y referencias:** catálogo INTA-SIGA, inventario AgroClima, referencias de grilla y filtros geográficos. La presencia de una estación en un catálogo no garantiza datos recientes ni calidad instrumental.
- **Conjuntos y consulta histórica:** consulta de ERA5 para coordenadas y períodos admitidos por el proveedor, pronóstico multimodelo y descarga del consolidado de observaciones atribuidas a SIGA-INTA.
- **Centro de operaciones:** catálogo de fuentes, estado de integración, cobertura, resoluciones y limitaciones. Informa arquitectura y estado de investigación; no es un monitor en tiempo real.

### Datos archivados y advertencias

- La serie ERA5 de Virasoro contiene 35 años completos (1991–2025) para una celda de reanálisis centrada en -28,00 / -56,00. Es una representación de grilla, no una medición puntual de pluviómetro.
- El repositorio conserva un consolidado comunitario atribuido a SIGA-INTA con 1.177.258 filas y un catálogo de 182 estaciones. La integridad del archivo no demuestra calibración, homogeneidad ni validación instrumental. Hay claves estación-fecha repetidas que requieren tratamiento antes de producir estadísticas definitivas.
- El snapshot provincial de Corrientes contiene registros diarios y mensuales con cobertura desigual. Los agregados departamentales no son equivalentes a mediciones puntuales.
- El conector de AgroClima consulta observaciones publicadas por estación. Su ventana reciente no reemplaza un archivo histórico diario de precipitaciones.
- NASA GPM IMERG, INA-SIyAH y SNIH están documentados como fuentes candidatas para ampliar análisis de precipitación y contexto hidrológico. Su registro en el catálogo no significa que ya estén integrados en la interfaz.

## Cómo trabajamos

1. **Pregunta primero.** Definimos qué fenómeno, territorio, período y escala temporal necesitamos estudiar.
2. **Procedencia.** Identificamos organismo, producto, versión, fecha de consulta, licencia y URL original.
3. **Cobertura.** Revisamos coordenadas, resolución, frecuencia, períodos incompletos, faltantes y cambios de estación.
4. **Calidad.** Separamos integridad técnica, controles automáticos y validación meteorológica. Son niveles distintos.
5. **Análisis reproducible.** Conservamos scripts, fórmulas, decisiones de limpieza y archivos derivados.
6. **Interpretación prudente.** Distinguimos observaciones, estimaciones, reanálisis, modelos, hipótesis y conclusiones.
7. **Revisión.** Los hallazgos se actualizan cuando aparecen nuevos datos o evidencia que modifica la interpretación.

No convertimos datos faltantes en cero, no inventamos mediciones y no presentamos una salida experimental como pronóstico validado. La plataforma no sustituye los sistemas oficiales de alerta.

## Líneas de investigación

| Línea | Pregunta principal | Estado |
|---|---|---|
| [Precipitaciones en Gobernador Virasoro](investigaciones/01-precipitacion-virasoro/README.md) | ¿Qué muestran las referencias históricas y la serie ERA5 del entorno local? | Primera fase documental y descriptiva procesada; falta una serie primaria continua y homogénea. |
| [Corrientes y el NEA](investigaciones/02-corrientes-nea/README.md) | ¿Cómo se distribuye la precipitación entre zonas comparables? | Planificada; requiere consolidar períodos y coberturas comparables. |
| [Contexto nacional](investigaciones/03-contexto-nacional/README.md) | ¿Cómo se ubican los patrones regionales dentro del país? | En evaluación de fuentes y métodos. |
| [Lluvia y variabilidad climática](investigaciones/04-lluvia-y-variabilidad-climatica/README.md) | ¿Qué asociaciones aparecen con ENSO y otros indicadores? | Pendiente de series compatibles y evaluación estadística. |
| Eventos de lluvia y contexto hidrológico | ¿Cómo se relacionan la precipitación acumulada, las crecidas y los anegamientos? | Línea de investigación; INA/SNIH y GPM están documentados, aún sin integración operativa. |

## Documentación principal

- [Arquitectura y componentes](docs/arquitectura-lnm.md)
- [Fuentes y metodología](fuentes/fuentes_y_metodologia.md)
- [Actualización de fuentes meteorológicas e hidrológicas — 6 de noviembre de 2026](fuentes/actualizacion_fuentes_meteorologicas_hidrologicas_2026-11-06.md)
- [Catálogo público de fuentes](docs/datos/catalogo-fuentes.json)
- [Auditoría técnica y de datos](investigaciones/auditoria-tecnica-datos-2026-10-29.md)
- [Conector AgroClima en Vercel](docs/agroclima-vercel.md)
- [Archivo y criterios de revisión de eventos](research/events/README.md)
- [Entorno experimental de investigación neuronal](research/neural/README.md)

## Desarrollo y validación

El frontend público estático vive en `docs/` y se publica mediante GitHub Pages. Vercel aloja endpoints API; no es una segunda copia del frontend.

Requisitos principales: Python 3.12 y Node.js para comprobaciones del sitio.

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m lnm sources
PYTHONPATH=src python -m lnm events
node --check docs/assets/js/laboratorio-nacional.js
node --check docs/assets/js/lnm-center.js
```

Las dependencias de aprendizaje automático están separadas en `requirements-neural.txt` y no forman parte del flujo de publicación del sitio.

## Autoría y uso

Proyecto personal de **DAN SOSA**, desde Gobernador Virasoro, Corrientes, Argentina.

Sitio personal: https://dansosa.vercel.app

La licencia MIT de la raíz aplica al código original de este repositorio, no a datos, imágenes, documentos ni materiales de terceros. Cada fuente conserva sus propias condiciones de uso y atribución.
