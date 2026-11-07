# Cierre de estabilización — 7 de noviembre de 2026

## Alcance de esta revisión

Revisión estática del repositorio en `main` (commit base `53563b1511fdf60f5bfd92aadefae3cf3e4a2097`), metadatos de GitHub Actions y despliegues de Vercel. No equivale a una prueba manual completa del navegador ni a una validación meteorológica independiente.

## Estado técnico observado

- El último commit de `main` tenía una ejecución exitosa del workflow `Validar base del Laboratorio de Datos Meteorológicos` (run 108).
- Vercel registraba un despliegue de producción `READY` asociado al mismo SHA. La arquitectura documentada establece que Vercel aloja endpoints API y que el frontend estático se publica por GitHub Pages.
- La raíz del despliegue Vercel no es la URL pública del laboratorio; la respuesta 404 de la raíz es coherente con un proyecto backend-only y no demuestra un fallo del sitio estático.
- La URL pública de GitHub Pages no pudo verificarse con una prueba de navegador en esta revisión. La publicación de Pages debe confirmarse con su workflow y una comprobación externa del HTML.
- No se detectaron PR abiertos en el repositorio al iniciar esta revisión.

## Ajustes de experiencia pública

- Se incorpora «Preguntas y evidencia» al selector principal, para que la agenda de investigación deje de estar oculta detrás de enlaces secundarios.
- Se cambia el título de la sección a «Preguntas, respuestas y evidencia» y se incorpora un resumen explícito del estado de conocimiento.
- Se eliminan dos entradas duplicadas: la pregunta sobre aumento/disminución de la precipitación anual (ya cubierta por la pregunta general sobre tendencias) y la segunda formulación equivalente de la pregunta ENSO.
- La sección queda con nueve preguntas diferenciadas: una respuesta descriptiva parcial sobre variabilidad de precipitación; una orientación operativa sobre monitoreo y pronóstico; y siete líneas que requieren datos o análisis adicionales.

## Estado científico de las preguntas

La serie ERA5 1991–2025 próxima a Gobernador Virasoro permite describir variabilidad interanual y explorar una pendiente matemática. No permite, por sí sola, confirmar una tendencia climática regional, atribuir causas ni caracterizar extremos diarios.

La relación lluvia–ENSO no está calculada. La severidad y frecuencia de tormentas requieren series diarias/subdiarias, índices de extremos y contraste con observaciones independientes. Las relaciones lluvia–crecida requieren reconstrucción por cuenca con precipitación antecedente, niveles, caudales y evidencia documental. Los pronósticos son escenarios de modelos, no certeza ni alertas oficiales.

## Fuentes e integraciones

- INA/DSIyAH cuenta con un adaptador de consulta directa de series. Para obtener resultados se necesita un `seriesId` válido y un período disponible; la selección, catalogación y validación sistemática de series sigue siendo trabajo pendiente.
- GOES-19 ABI y GLM FED están disponibles mediante visores/productos NOAA, sujetos a disponibilidad y limitaciones documentadas.
- RainViewer es un mosaico compuesto de cobertura parcial, no una red radar oficial nacional.
- GPM IMERG, CHIRPS, radiosondeos y SNIH no deben presentarse como conectores completos mientras no se pruebe y documente su flujo de datos.
- El catálogo diferencia conectores operativos, archivos, fuentes documentadas y fuentes pendientes; esos estados no equivalen a validación científica.

## Criterios para considerar cerrado el release

1. La validación automática del pull request debe terminar correctamente.
2. La publicación de GitHub Pages debe completarse y mostrar el selector actualizado y la sección de preguntas.
3. Deben verificarse manualmente en el sitio: navegación, gráficos históricos, búsqueda de localidad, consultas ERA5/NASA POWER, pronóstico, mapa, radar, GOES-19/GLM, AgroClima y consulta INA con un ID conocido.
4. Los endpoints de AgroClima en Vercel deben responder desde el frontend de Pages; un estado de despliegue `READY` no sustituye esa prueba.
5. Cualquier fuente indisponible debe mostrar un estado claro y no reutilizar datos vencidos como actuales.

## Límite de esta entrega

Este documento registra hallazgos y criterios de cierre; no declara que se haya realizado una prueba de navegador completa, que todas las APIs externas estén disponibles o que las preguntas científicas estén resueltas. La estabilización de software y la validación meteorológica son procesos distintos.
