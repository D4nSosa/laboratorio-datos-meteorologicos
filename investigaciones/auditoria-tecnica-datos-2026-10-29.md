# Auditoría técnica y de datos — 2026-10-29

## Alcance

Revisión del flujo de descarga INTA-SIGA, del script de cobertura y del sitio estático existente. Esta auditoría inspecciona código, metadatos y resultados publicados; no sustituye una validación meteorológica contra pluviómetros de referencia ni una inspección instrumental de cada estación.

## Estado verificado

- GitHub Actions run 40905465960: `success`.
- Descarga del CSV fuente, comprobación SHA-256, estructura de 38 columnas y 1.177.258 filas: pasos completados.
- El script produjo cobertura por estación, agregados anuales exploratorios y un recorte de 51.819 filas.
- Catálogo: 182 estaciones; estaciones con registros en el consolidado: 180.
- Fechas inválidas detectadas: 0.
- Repeticiones de la clave estación-fecha detectadas: 99.

## Hallazgos y riesgos

### 1. Integridad estructural no equivale a calidad meteorológica

El SHA-256 y la validación CSV demuestran que se archivó el objeto esperado y que su estructura puede leerse. No demuestran calibración, ausencia de errores instrumentales, unidades homogéneas ni continuidad de las series. El origen archivado es una consolidación comunitaria que declara basarse en SIGA-INTA, no una descarga oficial íntegra bajo control de este repositorio.

### 2. Hay 99 repeticiones de estación-fecha

El script las detecta pero conserva todas las filas al calcular sumas anuales. Si algunas son duplicados reales, los agregados pueden sobrecontar. Por eso `precipitacion-anual-estaciones.csv` debe tratarse como exploratorio y no publicarse como precipitación anual validada hasta inspeccionar los registros repetidos y confirmar la frecuencia de observación.

### 3. El recorte llamado «cercanas a Virasoro» no se determina por distancia

El script usa una lista fija de siete IDs. El catálogo confirma, por ejemplo, A872908 en Cerro Azul y A872971 en Ituzaingó, pero también incluye A872910 en San Vicente y NH0460/A872916 en la zona de Corrientes/El Sombrerito, mucho más alejadas. Por lo tanto el nombre del archivo no debe interpretarse como un conjunto de las estaciones más próximas. Debe calcularse distancia geográfica desde coordenadas y documentarse el radio o el criterio usado.

### 4. La variable y la frecuencia deben confirmarse

El código suma `precipitacion_pluviometrica` por año, aunque la frecuencia y unidad no se validan en el propio flujo. Los máximos por fila tampoco deben describirse como máximos diarios hasta comprobar que cada fila representa un día y que las unidades son comparables. Los valores cero se conservan como observados; no se convierten faltantes en cero.

### 5. Cobertura temporal desigual

El resumen muestra series con inicios y finales distintos, además de faltantes. Una comparación regional debe limitarse a períodos comunes y registrar la proporción de cobertura por estación/año. La cantidad de filas por estación no equivale por sí sola a completitud.

### 6. Sitio público y repositorio privado son dos cuestiones distintas

El repositorio está configurado como privado según la respuesta de la API. El contenido de `docs/` ya incluye un sitio estático, pero eso no confirma que GitHub Pages esté publicado. Para publicar una página pública desde un repositorio privado, la disponibilidad depende del plan y de la configuración de Pages. No se debe dar una URL por publicada hasta verificar el estado real.

## Clasificación de confianza

- **Verificado técnicamente:** descarga reproducible, SHA-256, forma del CSV, número de filas/columnas, ejecución del script.
- **Exploratorio:** estadísticas anuales derivadas del consolidado INTA-SIGA.
- **Pendiente:** resolver duplicados, confirmar unidades/frecuencia, selección por distancia, análisis de completitud, contraste con fuentes oficiales/estaciones de referencia y comprobar publicación de Pages.
- **ERA5:** reanálisis de una celda próxima a Virasoro; útil como línea de base espacialmente aproximada, no como medición de una estación local.
- **Santo Tomé:** serie departamental de una fuente distinta; debe mantenerse separada de la serie ERA5 y de registros puntuales.

## Próximas acciones recomendadas

1. Añadir un control automatizado de duplicados y bloquear agregados «validados» si quedan claves estación-fecha repetidas.
2. Sustituir la lista fija de estaciones cercanas por selección calculada con latitud/longitud y distancias en km.
3. Documentar definición, unidad y frecuencia de cada variable antes de sumar.
4. Construir un catálogo de fuentes con estado, cobertura, última actualización y limitaciones.
5. Publicar la interfaz como tablero de exploración que etiquete cada capa como observación, agregado administrativo o reanálisis.
6. Volver a ejecutar las pruebas y revisar la vista pública después de cualquier despliegue.

