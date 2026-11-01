# Archivo de eventos meteorológicos

Este catálogo registra episodios investigados por el laboratorio. No es un listado automático de alertas ni una base de tormentas confirmadas.

Cada evento futuro debe incluir identificador estable, fenómeno investigado, intervalo UTC, región, estado de revisión y al menos una evidencia trazable (fuente, producto, momento observado y referencia al activo archivado).

Estados permitidos:

- candidate: candidato generado por una búsqueda o algoritmo.
- reviewed: evidencia revisada por una persona responsable.
- confirmed: clasificación respaldada por evidencia suficiente y metodología documentada.
- rejected: candidato descartado, conservado para auditoría.

No clasificar tornados, granizo, superceldas ni otros fenómenos de alto impacto a partir de una sola imagen o de una salida no verificada.

Validar el catálogo con: PYTHONPATH=src python -m lnm events
