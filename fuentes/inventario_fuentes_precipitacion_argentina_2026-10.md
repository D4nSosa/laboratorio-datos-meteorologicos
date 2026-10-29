# Inventario de fuentes de precipitación y datos meteorológicos — Argentina

**Fecha de relevamiento:** 29 de octubre de 2026  
**Proyecto:** Laboratorio de Datos Meteorológicos y Territoriales  
**Responsable:** DAN SOSA

## Objetivo

Identificar fuentes públicas reutilizables para ampliar la investigación desde Gobernador Virasoro hacia Corrientes, el NEA y el país, distinguiendo mediciones de estaciones, agregaciones administrativas, reanálisis y productos modelados. El relevamiento prioriza acceso directo, cobertura espacial, series históricas, formatos y necesidades de solicitud institucional.

## Resultado ejecutivo

No se identificó una única base pública que garantice todas las series pluviométricas históricas de Argentina. La estrategia recomendada es federar fuentes y conservar metadatos de procedencia.

Hallazgos de mayor utilidad:

1. **ICAA publicó el 27/10/2026** un aviso de acceso directo a estaciones hidrometeorológicas en tiempo real en Corrientes. El aviso indica que el mapa integra redes del SNIH, Red Agrometeorológica INTA, Red de Monitoreo Iberá, Red Hidrológica Nacional, RMET y SiNaRaMe. Esto vuelve especialmente útil el acceso provincial como catálogo de estaciones activas y variables, pero no demuestra que se ofrezcan series históricas descargables completas.
2. **SNIH** ofrece datos históricos consolidados y datos de tiempo cuasi real. Su descripción institucional consultada identifica como redes integradas a la Subsecretaría de Recursos Hídricos y la Red de Monitoreo Iberá; el acceso debe evaluarse estación por estación y distinguiendo datos validados de lecturas crudas.
3. **INA / DSIyAH** ofrece una API documentada para listar redes, estaciones, variables y series, y descargar datos en CSV, XML, JSON y GeoJSON. El alcance descrito es la Cuenca del Plata; es una fuente importante para el NEA, pero no una cobertura nacional completa.
4. **SMN / Datos Argentina** publica un catálogo de estaciones meteorológicas y datasets meteorológicos horarios. El dataset horario descrito incluye temperatura, presión, viento y humedad, pero no precipitación entre los campos documentados. No debe asumirse que ese archivo contiene lluvia histórica; la descarga de datos del SMN y los productos específicos de precipitación deben verificarse por separado.
5. **INTA-SIGA** dispone de un paquete abierto para consultar metadatos de estaciones y descargar sus datos (funciones siga_estaciones(), siga_datos() y siga_descargar()). La cobertura y los períodos dependen de cada estación; se necesita una ejecución reproducible del paquete para obtener el catálogo completo.
6. **Ministerio de Producción de Corrientes / Departamento de Economía Agraria** ofrece un portal provincial con datos mensuales y diarios, un catálogo de fuentes y datos de ocho estaciones según sus metadatos publicados. La cobertura incluye localidades/estaciones de Corrientes, incluida Virasoro. Es una fuente provincial de alto valor, pero sus registros deben conservarse separados de series puntuales del SMN o ERA5.

## Inventario de fuentes

| Fuente | Tipo de dato | Cobertura declarada o conocida | Acceso | Estado en este relevamiento |
|---|---|---|---|---|
| [ICAA — acceso a estaciones](https://icaa.gov.ar/instructivo-acceso-estacion-icaa/) | Observaciones meteorológicas e hidrológicas en tiempo real | Estaciones disponibles en Corrientes; integra varias redes | Mapa web | Acceso y aviso institucional identificados; no se descargó una serie histórica masiva |
| [ICAA — registros meteorológicos](https://icaa.gov.ar/registro-de-datos-meteorologicos/) | Informes/archivos históricos de la estación ICAA en Corrientes Capital | La página consultada enumera meses desde 2012 en adelante, con distinta disponibilidad por período | Página con enlaces por mes | Se identificó un archivo histórico local; no equivale a una serie de Virasoro ni a toda la provincia |
| [SNIH](https://snih.hidricosargentina.gob.ar/) | Registros hidrológicos y meteorológicos de redes integradas | Estaciones incorporadas; no asumir cobertura nacional exhaustiva | Portal de datos | Documentación y alcance institucional revisados; no se exportó una descarga nacional completa |
| [INA / DSIyAH — API](https://alerta.ina.gov.ar/pub/gui/apibase) | Estaciones, variables y series observadas/modeladas | Cuenca del Plata | API HTTP; CSV, XML, JSON, GeoJSON y rásteres | API y recursos documentados; falta extraer y validar inventario completo de estaciones/series |
| [SMN — descarga de datos](https://www.smn.gob.ar/descarga-de-datos) | Observaciones meteorológicas de estaciones oficiales | Red del SMN | Descarga/portal institucional | Punto de acceso identificado; la cobertura histórica de precipitación requiere verificar producto por producto |
| [SMN — listado de estaciones en Datos Argentina](https://datos.gob.ar/dataset/smn-listado-estaciones-meteorologicas-smn) | Catálogo de estaciones, ubicación y códigos | Estaciones del SMN | Archivo descargable, publicado como ZIP | Recurso localizado; no se descargó el ZIP desde esta sesión |
| [SMN — datos meteorológicos horarios](https://datos.gob.ar/dataset/smn-datos-meteorologicos-horarios) | Temperatura, presión, viento y humedad | Estaciones de superficie del país | ZIP | Recurso localizado; los campos descritos no incluyen precipitación |
| [SMN — tiempo presente](https://www.datos.gob.ar/sr/dataset/smn-estado-tiempo-presente/archivo/smn_3.1) | Última observación de variables de la red | Red del SMN | ZIP/portal | Útil para contexto operativo; no sustituye una serie histórica pluviométrica |
| [INTA-SIGA](https://siga.inta.gob.ar/) y [paquete R](https://github.com/AgRoMeteorologiaINTA/siga) | Datos agrometeorológicos y metadatos de estaciones | Según estaciones disponibles | Paquete R y descargas | Se verificó documentación del paquete; no se ejecutó la descarga integral del catálogo en este entorno |
| [Ministerio de Producción de Corrientes — portal](https://deaeconomiactes.github.io/Precipitaciones-Lluvias/) | Registros pluviométricos departamentales, datos diarios y variables de ocho estaciones según metadatos | Provincia de Corrientes | Portal y JSON públicos en GitHub | Se inspeccionaron el catálogo de fuentes y metadatos publicados; no se copió la base completa al repositorio de investigación |
| [Base mensual de Corrientes — rainfall.json](https://github.com/deaeconomiactes/Precipitaciones-Lluvias/blob/main/data/rainfall.json) | Precipitación mensual por departamento | 25 departamentos según metadatos de la fuente; período declarado 1993–2026 | JSON público | Ya analizada en el informe de Santo Tomé; conserva su escala departamental |
| [Base diaria provincial — rainfall-daily.json](https://github.com/deaeconomiactes/Precipitaciones-Lluvias/blob/main/data/rainfall-daily.json) | Registros diarios departamentales | Según cobertura y reglas documentadas por el proyecto fuente | JSON público | Archivo identificado en el catálogo público; falta descargar, auditar cobertura y reconciliar fechas antes de incorporarlo |
| [Portal Nacional de Datos Públicos](https://www.datos.gob.ar/) | Catálogo transversal de datasets | Nacional, según organismo publicador | Catálogo/API | Útil como buscador complementario; no constituye una serie pluviométrica única |
| [API Series de Tiempo](https://www.argentina.gob.ar/datos-abiertos/api-series-de-tiempo) | Indicadores oficiales tabulares | Según series registradas | API/CSV/JSON | Fuente secundaria para indicadores agregados, no presumir que contiene observaciones diarias por estación |
| [Dirección General de Hidráulica y Obras Sanitarias de Buenos Aires](https://www.hidraulica.gob.ar/ema.php?inf=precipitacion&station=) | Datos de estaciones meteorológicas automáticas | Red provincial de Buenos Aires | Portal y planillas históricas | Ejemplo de fuente provincial complementaria; no cubre el país |

## Revisión específica del portal provincial de Corrientes

En el repositorio público de deaeconomiactes/Precipitaciones-Lluvias se inspeccionaron data/source-catalog.json, data/metadata.json y el índice de archivos de data/. Los metadatos publicados declaran:

- 25 departamentos.
- Ocho localidades/estaciones listadas: Bella Vista, Esquina, Ituzaingó, La Cruz, Mercedes, Monte Caseros, Paso de los Libres y Virasoro.
- Base mensual con rango declarado 1993–2026.
- Base diaria histórica y operativa en archivos JSON separados.
- Una tabla stations.json con variables mensuales de lluvia, temperatura, humedad y viento, y un campo de fechas inválidas.

**Precaución de interpretación:** esos metadatos describen el sistema de datos del proyecto fuente; no demuestran que cada localidad tenga una serie continua desde 1993, que cada variable sea de una estación oficial ni que todos los registros tengan igual método de medición. Antes de integrar datos diarios, hay que auditar la estructura, la procedencia por registro, los duplicados, fechas, faltantes y las diferencias entre observación diaria y agregación departamental.

No se incorporó al repositorio una copia completa de los JSON de terceros en esta etapa: son archivos extensos, cambian en el repositorio original y deben usarse con su procedencia y condiciones originales. La fuente ya usada para el análisis de Santo Tomé está documentada por separado. La siguiente descarga reproducible debe conservar fecha de consulta, hash del archivo original y un registro de transformaciones.

## Qué se pudo descargar o verificar en esta sesión

- **Verificado en web:** páginas oficiales de SNIH, INA, SMN/Datos Argentina, ICAA, INTA-SIGA, Datos Abiertos y el portal de Corrientes.
- **Inspeccionado mediante la API pública de GitHub:** catálogo de fuentes (source-catalog.json), metadatos (metadata.json), índice de archivos y una porción del catálogo mensual de estaciones (stations.json) del proyecto provincial de Corrientes.
- **Ya analizado antes de este relevamiento:** rainfall.json del proyecto provincial, con los resultados resumidos en investigaciones/01-precipitacion-virasoro/resultados_santo_tome.md.
- **No descargado como archivo local ni archivado aquí:** ZIP del SMN, catálogo completo SIGA, exportación nacional de SNIH, inventario/series completas de INA y JSON diarios provinciales. En esta sesión el entorno de ejecución no tuvo resolución de red directa para descargar esos archivos; no se afirma que se hayan descargado o validado.

## Prioridades de la siguiente etapa

### Prioridad 1 — obtener catálogos de estaciones y variables

1. Exportar el listado de estaciones del INA/DSIyAH y su listado de variables/series. Filtrar precipitación por unidad y procedimiento, no solo por nombre de estación.
2. Descargar el listado de estaciones del SMN y documentar el producto oficial de descarga de datos históricos que incluya precipitación.
3. Ejecutar el paquete siga del INTA para descargar el catálogo de estaciones y sus metadatos, y determinar qué estaciones tienen precipitación y qué período cubren.
4. Desde el mapa de ICAA, inventariar las estaciones verdes meteorológicas y confirmar cuáles ofrecen histórico descargable, no solo telemetría actual.
5. Descargar y auditar los JSON diarios y el catálogo completo del portal provincial de Corrientes, conservando su procedencia.

### Prioridad 2 — armonizar sin mezclar fuentes

Crear un catálogo maestro de estaciones con: identificador de fuente, nombre original, organismo, latitud/longitud, altitud, provincia, variables, unidad, frecuencia, fecha inicial/final, porcentaje de cobertura, estado de validación, URL, fecha de consulta, licencia/condiciones y hash del archivo fuente.

Los registros deben seguir separados por estación y fuente. No sumar ni promediar valores entre fuentes hasta confirmar que representan la misma estación, intervalo, unidad y procedimiento. Los reanálisis (ERA5) deben permanecer etiquetados como grilla/reanálisis, no como observaciones.

### Prioridad 3 — solicitudes institucionales consolidadas

- **SMN:** solicitar catálogo de estaciones y series históricas de precipitación diaria/mensual de todo el país, incluyendo metadatos, períodos de operación, cambios de ubicación/instrumento, faltantes, control de calidad, formatos, licencia y procedimiento de acceso.
- **Organismo nacional de recursos hídricos / SNIH:** solicitar exportación del inventario nacional de estaciones y series con variable precipitación, cobertura temporal, organismos adheridos, condiciones de descarga y metadatos.
- **ICAA:** mantener abierta la consulta ya derivada al área técnica y, al recibir respuesta, pedir inventario provincial completo y series históricas disponibles de las redes integradas, evitando una nueva consulta separada por localidad.
- **INTA:** si el catálogo abierto no incluye períodos o archivos necesarios, solicitar inventario de estaciones con precipitación y disponibilidad histórica a escala nacional.

## Criterios de calidad

- Distinguir precipitación acumulada diaria, precipitación mensual y datos de evento; no tratarlos como equivalentes.
- Diferenciar observaciones validadas, datos telemétricos crudos, agregaciones administrativas, estimaciones modeladas y reanálisis.
- No completar ausencias con cero. Cero solo es válido si la fuente lo registra explícitamente.
- Verificar calendario, unidades, duplicados, datos negativos, fechas inválidas, cobertura y cambios de instrumento/emplazamiento.
- Comparar estaciones solo con períodos compatibles y metadatos suficientes.
- Citar la fuente original y sus condiciones; no asumir que todos los archivos públicos tienen la misma licencia.
- No afirmar tendencias climáticas locales usando reanálisis o pocos años de datos departamentales como si fueran una serie observada homogénea.

## Fuentes oficiales principales

- ICAA: https://icaa.gov.ar/disponible-acceso-directo-a-datos-de-estaciones-hidro-meteorologicas-en-tiempo-real/
- ICAA histórico: https://icaa.gov.ar/registro-de-datos-meteorologicos/
- SNIH: https://snih.hidricosargentina.gob.ar/
- INA/DSIyAH: https://alerta.ina.gov.ar/pub/gui/apibase
- SMN: https://www.smn.gob.ar/descarga-de-datos
- Estaciones SMN en Datos Argentina: https://datos.gob.ar/dataset/smn-listado-estaciones-meteorologicas-smn
- Datos meteorológicos horarios SMN: https://datos.gob.ar/dataset/smn-datos-meteorologicos-horarios
- INTA-SIGA: https://github.com/AgRoMeteorologiaINTA/siga
- Corrientes: https://deaeconomiactes.github.io/Precipitaciones-Lluvias/
- Datos Abiertos: https://www.datos.gob.ar/
- API Series de Tiempo: https://www.argentina.gob.ar/datos-abiertos/api-series-de-tiempo
