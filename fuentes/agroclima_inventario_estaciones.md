# Inventario de estaciones AgroClima

La exploración se ejecuta mediante GitHub Actions con el script
`scripts/descubrir_estaciones_agroclima.py`.

## Qué hace

1. Inspecciona el HTML público del mapa y los JavaScript enlazados para registrar
   posibles referencias a endpoints y números de estación.
2. Explora un rango acotado de IDs (por defecto 1400–1700), además de IDs semilla
   documentados durante la investigación.
3. Comprueba cada página pública en las dos rutas conocidas de AgroClima.
4. Conserva únicamente páginas con evidencia de contenido meteorológico y genera
   `datos/agroclima/estaciones.json` y `estaciones.csv`.
5. Publica esos archivos como commit en esta rama y como artefacto de Actions.

## Ejecución

En GitHub: Actions → Descubrir estaciones AgroClima → Run workflow.
El rango inicial por defecto es 1400–1700. Se puede ajustar manualmente, con un
máximo de 1501 IDs por ejecución. También se ejecuta semanalmente.

## Criterios y límites

- Una página validada indica que el ID conduce a una página con contenido
  meteorológico; no demuestra por sí sola que la estación esté activa ni que
  ofrezca una serie histórica descargable.
- Coordenadas y última observación quedan nulas si no aparecen de forma legible
  en el HTML inspeccionado.
- La exploración por rango es una estrategia de descubrimiento, no una garantía
  de inventario completo. El mapa puede usar un catálogo/API dinámico que no
  esté expuesto en el HTML inicial.
- Los endpoints candidatos encontrados en JavaScript se registran para análisis;
  no se invocan endpoints privados o no documentados automáticamente.
- El proceso no descarga ni integra observaciones meteorológicas en el laboratorio.
  Primero produce un inventario auditable de estaciones.

## IDs semilla

1490, 1528, 1578, 1584, 1609 y 1620. Son IDs identificados durante la investigación
previa y se vuelven a validar en cada ejecución.
