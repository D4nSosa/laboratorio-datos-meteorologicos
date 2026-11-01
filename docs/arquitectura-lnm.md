# Arquitectura del Laboratorio Meteorológico Nacional

## Propósito

Evolucionar el laboratorio de datos meteorológicos y territoriales existente hacia una infraestructura de investigación atmosférica nacional, preservando las series y estudios publicados. La interfaz pública no se convierte en una fuente de pronóstico oficial.

## Componentes integrados

1. Infraestructura de datos: catálogo de fuentes, contratos de metadatos, control de calidad, almacenamiento y trazabilidad.
2. Observación: estaciones, SMN, GOES ABI, GLM, radar y precipitación satelital. Cada fuente se habilita después de verificar acceso, cobertura, latencia y condiciones de uso.
3. Reconstrucción: ERA5 y otros reanálisis, series históricas y archivo de eventos.
4. Diagnóstico: perfiles verticales, sondeos, inestabilidad y dinámica atmosférica. Los cálculos requieren entradas identificadas y métodos reproducibles.
5. Modelos numéricos: GFS, GEFS, ECMWF Open Data e ICON; sus salidas se etiquetan como pronóstico.
6. Seguimiento de tormentas: segmentación, asociación temporal, trayectorias e historial de objetos. Una detección automática no equivale a una clasificación meteorológica confirmada.
7. Investigación experimental: métodos estadísticos, líneas base y experimentos reproducibles.
8. LNM Neural Research Engine: modelos especializados con datos etiquetados y particiones independientes por evento/tiempo. No hay modelo entrenado ni predicción operativa en esta versión.
9. Centro de operaciones: interfaz integrada que expone estado de módulos y fuentes, sin representar datos no conectados como tiempo real.

## Contratos y procedencia

El catálogo público está en docs/datos/catalogo-fuentes.json. Cada fuente tiene un estado explícito: archived, documented, not_integrated o investigation_required. Estos estados describen el nivel de integración, no una evaluación de calidad científica.

Los manifiestos de datasets distinguen station_observation, satellite_estimate, radar_product, reanalysis, forecast y derived. Las fechas deben ser ISO 8601 con zona horaria. Unidades, resoluciones, período, URL de origen, fecha de recuperación y estado de calidad son obligatorios.

El archivo de eventos empieza vacío deliberadamente. Cada evento debe conservar evidencia trazable y estado de revisión: candidate, reviewed, confirmed o rejected.

## Aprendizaje automático

La primera arquitectura de referencia es CNN + GRU para secuencias de imágenes. PyTorch se instala como dependencia opcional fuera del entorno del sitio. Los conjuntos se dividen por evento y tiempo para evitar fuga de información. Los modelos se versionan y evalúan antes de cualquier publicación; no se actualizan automáticamente con cada ingesta.

## Límites operativos

Esta incorporación agrega contratos, catálogos, validaciones, documentación y una vista de estado. No incorpora todavía conectores operativos de GOES/GLM, radares, sondeos ni modelos numéricos, ni entrena una red neuronal. Esas capacidades requieren verificar datos de entrada y ejecutar pruebas de integración específicas.

## Validación

- python -m pip install -r requirements.txt
- PYTHONPATH=src python -m unittest discover -s tests -v
- PYTHONPATH=src python -m lnm sources
- PYTHONPATH=src python -m lnm events
- node --check docs/assets/js/lnm-center.js
