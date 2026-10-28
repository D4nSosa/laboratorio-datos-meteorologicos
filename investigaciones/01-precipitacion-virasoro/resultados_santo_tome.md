# Resultados preliminares — Santo Tomé (Corrientes)

## Qué se analizó

Se procesó el archivo público `data/rainfall.json` del proyecto **Registro y Seguimiento de Precipitaciones**, publicado por el Departamento de Economía Agraria del Ministerio de Producción de Corrientes. La base contiene filas mensuales por departamento y año. Consulta realizada: 28 de octubre de 2026.

- [Tablero público](https://deaeconomiactes.github.io/Precipitaciones-Lluvias/)
- [Archivo de datos consultado](https://github.com/deaeconomiactes/Precipitaciones-Lluvias/blob/main/data/rainfall.json)
- [Repositorio y descripción del proyecto fuente](https://github.com/deaeconomiactes/Precipitaciones-Lluvias)

Este análisis usa únicamente los 12 valores mensuales de cada año para el departamento de Santo Tomé. No se mezclaron registros diarios ni valores de otros departamentos.

## Control de cobertura

La base contiene 34 registros anuales de Santo Tomé entre 1993 y 2026. Para comparar totales anuales se usaron 32 años completos: 1993–2025, excluyendo 1999 (10 meses con valor) y 2026 (enero–mayo; cinco meses). No se rellenaron los meses faltantes.

## Resultados descriptivos

| Indicador | Resultado |
|---|---:|
| Años completos analizados | 32 |
| Media anual | 1781.40 mm |
| Mediana anual | 1718.28 mm |
| Menor total anual | 2004: 1068.10 mm |
| Mayor total anual | 2017: 2709.40 mm |
| Media de mayo | 153.17 mm |
| Mayo de 2025 | 480.73 mm |
| Mayo de 2017 | 480.70 mm |

En esta base, 2023 acumuló 2.213,73 mm; 2024, 2.140,43 mm; y 2025, 2.507,23 mm. Frente a la media de los 32 años completos, los desvíos son +24,3%, +20,2% y +40,7%, respectivamente. Estos porcentajes describen esta serie y este período; no prueban por sí solos una tendencia climática.

Mayo de 2025 fue el valor mensual más alto de mayo en los años completos de esta base, por una diferencia de apenas 0,03 mm respecto de mayo de 2017. La afirmación se limita a este archivo y su método de agregación; no se presenta como récord meteorológico oficial de una estación.

## Gráficos y tablas derivados

- `datos/santo_tome_totales_anuales.csv`: totales recalculados a partir de los 12 meses de cada año completo.
- `datos/santo_tome_promedios_mensuales.csv`: promedios mensuales calculados con los mismos 32 años.
- `datos/santo_tome_mayo_por_anio.csv`: valores de mayo de todos los años completos.
- `investigaciones/01-precipitacion-virasoro/graficos/santo_tome_totales_anuales.svg`: evolución anual.
- `investigaciones/01-precipitacion-virasoro/graficos/santo_tome_promedio_mensual.svg`: ciclo mensual promedio.

## Límites y relación con Virasoro

Santo Tomé es un departamento, no una medición puntual de Gobernador Virasoro. Estos datos no deben reemplazar los valores publicados para la ciudad ni compararse con ellos como si fueran una misma estación. Por ejemplo, las cifras de prensa que atribuyen a Virasoro 2.609,3 mm en 2023 y 2.346 mm en 2024 difieren de los totales departamentales de esta base. Esa diferencia no significa automáticamente que una fuente esté equivocada: la cobertura geográfica, los pluviómetros, el período de corte y la agregación pueden ser distintos.

Este resultado sirve como contexto regional y como una primera comprobación de la estructura de datos. Para cerrar la investigación de Virasoro aún falta verificar la fuente primaria de las cifras locales y ejecutar/contrastar una serie de reanálisis homogénea. No se evaluó todavía la relación estadística con ENSO.

## Reproducción

El cálculo utilizado para estos resultados se documenta en `scripts/analizar_santo_tome.py`. El archivo fuente original debe descargarse por separado; no se redistribuye aquí como si fuera propio. El script valida cobertura mensual y excluye los años incompletos del cálculo anual.
