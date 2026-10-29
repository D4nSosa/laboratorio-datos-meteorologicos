# Snapshot de datos meteorológicos — Corrientes

Fecha de recuperación: 2026-10-29. Fuente original: [Departamento de Economía Agraria, Ministerio de Producción de Corrientes](https://github.com/deaeconomiactes/Precipitaciones-Lluvias) y [portal de datos](https://deaeconomiactes.github.io/Precipitaciones-Lluvias/).

Este directorio conserva una copia de los archivos publicados por la fuente provincial y una versión CSV derivada para análisis. No es una base nacional ni una serie homogénea de estaciones meteorológicas.

## Archivos

- `rainfall-daily.json`: archivo original de registros diarios por departamento/localización.
- `rainfall-daily.csv`: representación tabular derivada del JSON diario.
- `rainfall.json`: archivo original de precipitación mensual por departamento y año.
- `rainfall-monthly.csv`: datos mensuales expandidos a una fila por año, departamento y mes.
- `stations.json`: tabla original con registros meteorológicos mensuales por estación.
- `source-catalog.json`: catálogo de fuentes que declara el proyecto original.
- `metadata.json`: metadatos originales del portal.
- `qa-summary.json`: resumen de estructura, cobertura y controles básicos ejecutados al recuperar la copia.

## Resultados del control básico

- Registros diarios: 5,186.
- Departamentos con registros diarios: 25.
- Cobertura diaria declarada por los registros: 2023-01-01 a 2026-10-25.
- Registros diarios sin fecha/número válido o con precipitación negativa: 0.
- Registros diarios sin coordenadas numéricas: 0.
- Registros diarios etiquetados explícitamente como Virasoro: 0.
- Registros mensuales: 817; años declarados en filas: 1993–2026.

## Advertencias

La base diaria no contiene filas cuyo campo `department` sea Virasoro, aunque Virasoro figure en el catálogo de estaciones del portal. No inferir que una coordenada de un registro equivale a una estación pluviométrica oficial sin consultar la documentación y el origen de ese registro. Las agregaciones mensuales departamentales no son intercambiables con mediciones puntuales. No imputar faltantes como cero. La fuente original no declara una licencia universal clara para todos los archivos; estos datos se mantienen atribuidos y enlazados a la fuente original. La licencia MIT del repositorio de investigación no se extiende a los datos de terceros.

Este snapshot cubre únicamente Corrientes. Las descargas nacionales del SMN, INA/SNIH e INTA-SIGA siguen siendo tareas separadas; no se debe anunciar cobertura nacional hasta obtener y verificar esos conjuntos.
