# Observaciones meteorológicas nacionales INTA-SIGA

El archivo `estaciones-observaciones.csv.gz` es el consolidado de observaciones publicado por el proyecto comunitario [precipitaciones-argentina-inta](https://github.com/marianof2000/precipitaciones-argentina-inta), que indica como fuente SIGA INTA.

Antes de archivar el consolidado se verifica el SHA-256 declarado por el manifiesto de origen, se comprueban las 38 columnas y 1.177.258 filas declaradas, y se valida que el CSV mantenga un número constante de columnas. Ver `observaciones-metadata.json` para las cifras verificadas.

Este control verifica integridad y estructura, no garantiza que cada observación esté completa o validada instrumentalmente. Mantener identificador de estación, fecha y variables originales; no imputar valores faltantes como cero. Consultar `estaciones.json` para la ficha geográfica de las estaciones.

El archivo se conserva comprimido para evitar el límite de tamaño por archivo de GitHub. Descomprimir con `gzip -dk estaciones-observaciones.csv.gz`.
