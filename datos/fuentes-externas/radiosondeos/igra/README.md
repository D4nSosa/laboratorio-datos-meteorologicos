# IGRA 2.2 — inventario de estaciones argentinas

Inventario derivado del archivo oficial `igra2-station-list.txt` de NOAA/NCEI. Contiene las estaciones cuyo identificador comienza con `ARM` (Argentina), tal como aparecen en el inventario consultado el 7 de noviembre de 2026.

- Archivo de origen: https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt
- Países/códigos: https://www.ncei.noaa.gov/pub/data/igra/igra2-country-list.txt
- Documentación: https://www.ncei.noaa.gov/pub/data/igra/igra2-readme.txt
- Versión: IGRA 2.2
- Columnas: ID, coordenadas, elevación, nombre, primer y último año disponible y cantidad de observaciones informada por NOAA.
- Registros: 20 identificadores de estación.
- Fecha de consulta: 2026-11-07.

## Importante

Este archivo es un inventario de disponibilidad, no contiene perfiles verticales (radiosondeos). La cantidad de observaciones es la cifra del inventario NOAA y no equivale a cantidad de perfiles únicos validados ni garantiza continuidad temporal. La cobertura argentina no es homogénea: varias estaciones tienen períodos cortos o históricos discontinuos. El archivo `posibles-estaciones-cercanas.csv` señala tres pares para revisión (Resistencia, Mendoza y Buenos Aires); no se consideran duplicados confirmados ni se fusionan. Para el análisis regional también deben evaluarse estaciones limítrofes de Uruguay, Brasil, Paraguay, Chile y Bolivia.

Los perfiles individuales se distribuyen en el repositorio web de IGRA 2.2, principalmente bajo:
https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/

Citar NOAA/NCEI e IGRA 2.2 en cualquier producto o publicación derivada. Consultar los términos y documentación oficiales antes de redistribuir archivos de perfiles.
