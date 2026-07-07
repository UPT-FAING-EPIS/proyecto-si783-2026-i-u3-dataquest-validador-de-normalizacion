# Validador de Normalización DB

Extensión oficial para Visual Studio Code del **Validador de Normalización de Bases de Datos Relacionales**.

Esta herramienta te permite validar la estructura de tu base de datos y detectar automáticamente si cumple con las Formas Normales (1FN, 2FN, 3FN), inyectando las recomendaciones directamente en tu código.

## Características

- Soporta archivos `.sql`, `.txt`, `.csv` o cualquier documento con sentencias `CREATE TABLE`.
- Funciona analizando todo el archivo o simplemente la selección de texto actual.
- Usa heurísticas integradas para inferir dependencias funcionales (parciales y transitivas).
- **Inyección de Resultados:** Escribe el diagnóstico al final de tu archivo en un bloque de comentarios SQL (`/* ... */`), ofreciendo sugerencias precisas para corregir tus tablas.

## Uso

1. Abre un archivo con sentencias SQL en Visual Studio Code.
2. Abre la Paleta de Comandos (`Ctrl+Shift+P`).
3. Ejecuta **`Validador DB: Analizar e Inyectar Reporte`**.
4. ¡Revisa el final de tu archivo para ver el reporte generado automáticamente!

## Requisitos
- **Python 3.10+** debe estar instalado en el sistema, ya que la extensión invoca un motor de análisis programado en Python de forma subyacente.

---
**Desarrollado con ❤️ para la comunidad de bases de datos.**
