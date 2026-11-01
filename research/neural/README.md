# LNM Neural Research Engine

## Estado

Infraestructura experimental preparada; **no hay un modelo entrenado ni una capacidad predictiva operativa** en este repositorio.

## Objetivo

Investigar modelos espacio-temporales especializados que aprendan de secuencias meteorológicas con procedencia y etiquetas verificables. La primera arquitectura de referencia es una CNN por cuadro + GRU temporal para clasificación experimental de secuencias. No se presenta como modelo meteorológico validado.

## Principios

- Cada muestra conserva fuente, producto, hora, resolución, unidades y licencia/condiciones de uso.
- Separar entrenamiento, validación y prueba por evento y, cuando corresponda, por período temporal. Nunca dividir píxeles de una misma tormenta entre conjuntos distintos.
- Conservar ausencias como ausencias; no rellenar silenciosamente.
- Comparar contra líneas base sencillas antes de aceptar una red neuronal.
- Registrar versión de datos, código, hiperparámetros, semillas, métricas y artefactos.
- Aprobar manualmente una versión antes de publicarla; no actualizar pesos automáticamente al recibir datos nuevos.
- Las salidas son experimentales y nunca sustituyen alertas oficiales.

## Formato de muestras

Cada ejemplo del manifiesto JSON contiene sample_id, event_id, asset_path, label, split, source_ids y observed_at. Los archivos NPZ contienen x con forma [tiempo, canales, alto, ancho] e y con etiqueta numérica. Las variables y el orden de canales se declaran en los metadatos del experimento.

## Arquitectura

model.py implementa un codificador convolucional por cuadro y una GRU que modela la secuencia. PyTorch es opcional y no forma parte de las dependencias del sitio web.

## Preparación

Instalar PyTorch compatible con el hardware disponible y ejecutar las validaciones de metadatos. El entrenamiento requiere un conjunto etiquetado suficiente y revisión científica; no se incluye un dataset sintético ni se entrena automáticamente con datos sin clasificar.
