# Resultados preliminares — Santo Tomé (Corrientes)

## Qué se analizó

Se procesó el archivo público `data/rainfall.json` del proyecto **Registro y Seguimiento de Precipitaciones**, publicado por el Departamento de Economía Agraria del Ministerio de Producción de Corrientes. Consulta documentada: 28 de octubre de 2026.

- [Tablero público](https://deaeconomiactes.github.io/Precipitaciones-Lluvias/)
- [Archivo de datos consultado](https://github.com/deaeconomiactes/Precipitaciones-Lluvias/blob/main/data/rainfall.json)
- [Repositorio y descripción del proyecto fuente](https://github.com/deaeconomiactes/Precipitaciones-Lluvias)

Este análisis usa únicamente los 12 valores mensuales de cada año completo para el departamento de Santo Tomé. No se mezclaron registros diarios ni valores de otros departamentos.

## Control de cobertura y resultados descriptivos

La base consultada contiene registros de 1993 a 2026. Se excluyeron los años incompletos y se usaron 32 años completos (1993–2025, sin 1999 ni 2026).

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

En esta base, 2023 acumuló 2.213,73 mm; 2024, 2.140,43 mm; y 2025, 2.507,23 mm. Estos resultados describen esta serie y este período; no prueban por sí solos una tendencia climática ni constituyen un récord oficial de estación.

## Archivos derivados

- `datos/santo_tome_totales_anuales.csv`: totales recalculados a partir de los doce meses.
- `datos/santo_tome_promedios_mensuales.csv`: promedios mensuales calculados con los años completos.
- `datos/santo_tome_mayo_por_anio.csv`: valores de mayo por año completo.
- Gráficos de Santo Tomé: se generan si están incluidos en la versión de trabajo; la automatización de este flujo publica los CSV como artefactos.

## Límites y relación con Virasoro

Santo Tomé es un departamento, no una medición puntual de Gobernador Virasoro. Estos datos no deben reemplazar valores publicados para la ciudad ni compararse como si fueran la misma estación. Diferencias con otras fuentes pueden deberse a cobertura geográfica, pluviómetros, períodos de corte y métodos de agregación.

Para cerrar una investigación de tendencias locales en Virasoro todavía hace falta verificar la fuente primaria de las cifras locales y contrastarla con una serie observada homogénea. No se evaluó aquí la relación estadística con ENSO.

## Reproducción

Desde la raíz del repositorio, con Python 3.12:

```bash
python -m pip install -r requirements.txt
python investigaciones/01-precipitacion-virasoro/scripts/analizar_santo_tome.py
```

El script valida la estructura JSON, los doce valores mensuales, los tipos numéricos, valores finitos/no negativos y registros anuales duplicados. Si no existe una copia local, descarga la fuente desde el repositorio original. Como la fuente externa puede actualizarse, los resultados reproducidos pueden cambiar; la fecha y la URL de consulta deben acompañar cualquier publicación.

## Fuentes históricas locales identificadas para la siguiente fase

La tesis de Andrés Gustavo Batalla (UNNE, 2019) documenta una figura histórica de precipitación y temperatura mensual de la estación del Instituto Agrotécnico Víctor Navajas Centeno para 1950–2000 y menciona registros locales posteriores. La figura no equivale a disponer de la serie original diaria o mensual. Antes de comparar cuantitativamente hay que localizar las planillas primarias y confirmar ubicación, cobertura y metodología.

- [Tesis de la UNNE](https://repositorio.unne.edu.ar/bitstream/handle/123456789/47752/RIUNNE_FCA_TM_Batalla_AG.pdf?isAllowed=y&sequence=1)
- [Aviso del ICAA sobre estaciones](https://icaa.gov.ar/disponible-acceso-directo-a-datos-de-estaciones-hidro-meteorologicas-en-tiempo-real/)
- [Instructivo del mapa](https://icaa.gov.ar/instructivo-acceso-estacion-icaa/)
- [Registro histórico del ICAA accesible en texto](https://icaa.gov.ar/registro-de-datos-meteorologicos/)

Estos documentos se registran como referencias y pistas de acceso, no como una serie local descargada y procesada en este repositorio.
