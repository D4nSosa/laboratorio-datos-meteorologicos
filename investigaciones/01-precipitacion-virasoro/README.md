# 01 — Precipitaciones en Gobernador Virasoro

## Estado

La primera fase exploratoria y documental está integrada en el [informe documental de Virasoro](informe_documental_virasoro.md). La serie ERA5 de 1991–2025 se descargó y procesó en GitHub Actions. El informe no afirma una tendencia climática local: todavía hace falta obtener y validar registros primarios continuos de una estación observada.

## Pregunta

¿Cómo varían las precipitaciones anuales y el ciclo mensual en el entorno de Gobernador Virasoro, y qué diferencias aparecen entre un reanálisis y los registros locales publicados?

## Fuentes consultadas

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): documentación de ERA5.
- [Tesis de la UNNE sobre yerba mate en Virasoro](https://repositorio.unne.edu.ar/bitstream/handle/123456789/56560/RIUNNE_FCA_FG_Decoppet_MF.pdf?isAllowed=y&sequence=1): datos de un establecimiento para 2019–2022; no son una serie oficial urbana.
- [Referencia climatológica tabulada de la UNNE](https://repositorio.unne.edu.ar/xmlui/bitstream/handle/123456789/56284/RIUNNE_FHUM_AR_Bruniard-Alberto-Falcon.pdf?isAllowed=y&sequence=1): informa 1.419 mm/año, pero el período de referencia debe confirmarse.
- [SMN — observaciones](https://ws2.smn.gob.ar/observaciones): punto de entrada oficial; no garantiza una serie histórica descargable para la localidad.
- [El Litoral — lluvia en Corrientes durante 2024](https://www.ellitoral.com.ar/sociedad/2025-1-11-22-5-0--cuanto-llovio-en-corrientes-durante-el-2024) y [lluvias de mayo de 2025](https://www.ellitoral.com.ar/sociedad/2025-5-29-21-32-0-mayo-cierra-con-un-acumulado-record-de-lluvias-en-algunas-zonas-alcanzo-los-560-mm): referencias periodísticas que requieren cotejo con la fuente primaria.

## Procedimiento reproducible

Con Python 3.12 desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python investigaciones/01-precipitacion-virasoro/scripts/descargar_era5.py
python investigaciones/01-precipitacion-virasoro/scripts/analizar_era5.py
```

El descargador valida que cada día del intervalo 1991–2025 esté presente exactamente una vez, que los valores sean finitos y no negativos, y que los agregados contengan los años y meses esperados. El analizador vuelve a validar la cobertura, los tipos, los meses y la consistencia entre totales mensuales y anuales.

## Límites

ERA5 es un reanálisis espacial; no equivale a una medición de pluviómetro en Gobernador Virasoro. La API devuelve una celda con coordenadas propias, que se registran en los metadatos. Una cifra periodística local, una agregación del departamento de Santo Tomé y el valor de una celda ERA5 no son necesariamente equivalentes.

Los años reportados por prensa se consideran referencias documentales hasta cotejarlos con registros primarios. Dos o tres años no alcanzan para afirmar una tendencia climática ni una causa relacionada con ENSO.

## Estado de cierre de esta fase

La fase exploratoria y documental está procesada y tiene un flujo automatizado. La conclusión sobre tendencia climática local queda fuera del alcance hasta disponer de una serie observada validada y metadatos de estación suficientes.
