# 01 — Precipitaciones en Gobernador Virasoro

## Estado

Investigación en curso. Este directorio contiene un procedimiento reproducible para consultar una serie de reanálisis y analizarla. No es un informe final ni sustituye los registros de una estación meteorológica.

## Pregunta inicial

¿Cómo varían las precipitaciones anuales y el ciclo mensual en el entorno de Gobernador Virasoro, y qué diferencias aparecen entre una serie de reanálisis y los registros locales publicados?

## Fuentes consultadas

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): documentación de ERA5 y parámetros de consulta.
- [Tesis de la UNNE sobre manejo de yerba mate en Virasoro](https://repositorio.unne.edu.ar/bitstream/handle/123456789/56560/RIUNNE_FCA_FG_Decoppet_MF.pdf?isAllowed=y&sequence=1): presenta precipitaciones de 2019–2022 tomadas de registros in situ de un establecimiento; no es una serie oficial de estación urbana.
- [Referencia climatológica tabulada de Gobernador Virasoro en un documento de la UNNE](https://repositorio.unne.edu.ar/xmlui/bitstream/handle/123456789/56284/RIUNNE_FHUM_AR_Bruniard-Alberto-Falcon.pdf?isAllowed=y&sequence=1): incluye una media anual de 1.419 mm, pero el período de referencia aún debe confirmarse.
- [Servicio Meteorológico Nacional — observaciones](https://ws2.smn.gob.ar/observaciones): referencia oficial para observaciones meteorológicas. La disponibilidad de la página no garantiza que exista una serie histórica completa y descargable para la localidad.
- [Nota de El Litoral sobre las precipitaciones de 2024 en Corrientes](https://www.ellitoral.com.ar/sociedad/2025-1-11-22-5-0--cuanto-llovio-en-corrientes-durante-el-2024): fuente periodística que cita cifras del Ministerio de Producción. Publica para Virasoro 2.346 mm en 2024 y 2.609,3 mm en 2023.
- [Nota de El Litoral sobre las lluvias de mayo de 2025](https://www.ellitoral.com.ar/sociedad/2025-5-29-21-32-0-mayo-cierra-con-un-acumulado-record-de-lluvias-en-algunas-zonas-alcanzo-los-560-mm): referencia periodística para el episodio de mayo de 2025. Las cifras deben atribuirse a la fuente y no mezclarse con otras series sin comprobar estaciones, fechas y metodología.

## Procedimiento reproducible

Los scripts están en `scripts/`:

- `descargar_era5.py`: consulta la precipitación diaria de ERA5 para una coordenada aproximada del casco urbano, guarda la serie y sus metadatos, y comprueba que el intervalo tenga todos los días esperados.
- `analizar_era5.py`: calcula estadísticas descriptivas y genera un gráfico de totales anuales y otro del promedio mensual.

Desde la raíz del repositorio:

```bash
pip install -r requirements.txt
python investigaciones/01-precipitacion-virasoro/scripts/descargar_era5.py
python investigaciones/01-precipitacion-virasoro/scripts/analizar_era5.py
```

La serie inicial cubre 1991–2025 para comparar años calendario completos. Los datos se guardan en `datos/virasoro_era5/` y las figuras en `investigaciones/01-precipitacion-virasoro/graficos/`. La ejecución debe revisarse antes de incorporar esos archivos al repositorio.

## Límites que importan

ERA5 es un reanálisis: combina observaciones y modelos para producir una serie espacialmente completa. No equivale a una medición de pluviómetro en Gobernador Virasoro. El script registra las coordenadas de la celda devuelta por la API; aun así, hay que documentar esa diferencia al interpretar resultados.

Una cifra publicada para la ciudad, una agregación del departamento de Santo Tomé y el valor de una celda de ERA5 no son necesariamente equivalentes. Pueden diferir por cobertura espacial, instrumento, método y período. En los gráficos y el texto se debe identificar siempre cuál de esas fuentes se usa.

Los datos reportados por prensa se consideran una pista documental hasta que se encuentre y compruebe la fuente primaria. Dos o tres años no alcanzan para afirmar una tendencia climática. Para eso hace falta una serie consistente y un análisis estadístico apropiado.

## Pendientes antes de cerrar la investigación

- Confirmar si hay registros observados de una estación cercana y documentar ubicación y continuidad.
- Ejecutar los scripts, revisar la respuesta de la API, los metadatos y los gráficos.
- Comparar años comunes entre reanálisis y registros locales sin tratarlos como idénticos.
- Verificar cualquier cifra de prensa contra su fuente primaria si es posible.
- Preparar el informe editorial después de revisar los resultados, las limitaciones y las fuentes.
