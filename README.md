# Documentación y Análisis del Modelo: Sistemas de Recomendación (LAB08)

**Asignatura:** INF-8239 Ciencia de Datos II  
**Unidad:** 03 - Algoritmos y Características Generativas  
**Laboratorio:** LAB08 - MovieLens, popularidad y recomendación por contenido  

---

## 1. Fundamento Conceptual: Recomendar no es adivinar gustos

Un sistema recomendador **no predice gustos abstractos**, sino que **ordena alternativas** para una persona en un contexto determinado. La salida del sistema depende directamente de qué interacciones fueron observadas, qué candidatos se permitieron y qué objetivo se optimizó. Un resultado en el *Top-N* no representa una verdad universal ni garantiza la satisfacción absoluta del usuario.

### Términos Operativos Clave
* **Usuario:** Entidad para la cual se personaliza una lista.
* **Ítem:** Elemento candidato a ser recomendado (ej. una película).
* **Feedback Explícito:** Preferencia declarada formalmente, como una valoración numérica (ej. estrellas en MovieLens).
* **Baseline:** Política simple y robusta que sirve como referencia mínima de comparación.
* **Cold Start (Arranque en frío):** Limitación ante la falta de interacciones previas para usuarios o ítems nuevos.
* **Sobre-especialización:** Fenómeno donde el sistema repite en exceso características ya conocidas, atrapando al usuario en una "burbuja de contenido".

---

## 2. Auditoría de Datos (Exploración del Dataset)

Al ejecutar la descarga y auditoría de los datos (`audit_data.py`), se obtienen las siguientes métricas descriptivas del conjunto de interacciones:

* **Universo Observado (610 usuarios y 9,724 ítems valorados):** Estos números definen exclusivamente el universo de datos que el sistema ha observado. No representan a toda la población mundial ni a la totalidad del catálogo cinematográfico existente.
* **Densidad Baja (1.69%):** La escasez (*sparsity*) refleja que la inmensa mayoría de las combinaciones posibles entre un usuario y una película no tienen una valoración registrada. Es crucial entender que la ausencia de calificación **no significa rechazo**; simplemente indica que no hay interacción observada.
* **Distribución de Ratings (Media = 3.50):** Las valoraciones van de 0.5 a 5.0. Este sesgo hacia valoraciones positivas suele reflejar un fenómeno de **autoselección**: las personas tienden a valorar aquello que ya decidieron consumir previamente.
* **Marcas temporales (Timestamps):** El rango temporal registrado permite organizar los datos cronológicamente, vital para simular una evaluación temporal realista sin utilizar interacciones futuras.

---

## 3. Ejecución del Baseline de Popularidad

Al ejecutar el recomendador basado en popularidad (`lab08_content.py`), el sistema ofrece un *Top-10* general basado en el consenso colectivo.

* **El problema de la media simple:** Si ordenáramos las películas solo por su promedio de estrellas (`mean`), una película desconocida con una única valoración de 5.0 dominaría el ranking automáticamente.
* **La solución (Promedio Suavizado):** El modelo emplea un `weighted_score` que combina la media específica de cada película con la media global de todo el catálogo. 
* **Interpretación de los resultados:** Películas como *The Shawshank Redemption (1994)* lideran la lista porque acumulan **evidencia suficiente** (317 valoraciones) para recibir una puntuación suavizada altamente estable (4.39). Si comparamos dos películas con medias semejantes, el algoritmo siempre favorecerá a aquella que posea un mayor conteo de valoraciones.

---

## 4. Interpretación del Modelo por Contenido

El recomendador por contenido representa los géneros de las películas mediante **TF-IDF** y calcula su cercanía utilizando la **similitud coseno**. Una recomendación significa que los ítems «comparten características registradas», no necesariamente que «le gustarán al usuario».

A partir de los resultados de consulta para *Toy Story (1995)*, extraemos las siguientes conclusiones metodológicas:

1. **Exclusión de la consulta:** La película ancla (*Toy Story*) no aparece en la lista devuelta. El algoritmo excluye el ítem de referencia para evitar redundancias y sugerir alternativas.
2. **Justificación local (Géneros):** Todas las películas del Top-10 (*Turbo*, *Toy Story 2*, *Monsters, Inc.*, etc.) comparten exactamente la misma cadena de géneros: `Adventure|Animation|Children|Comedy|Fantasy`.
3. **Empates técnicos (`content_score = 1.0`):** Un valor de similitud coseno de 1.0 indica gran semejanza vectorial. Sin embargo, el modelo puramente basado en contenido no evalúa la calidad narrativa ni la recepción del público, solo la cercanía geométrica de sus etiquetas.
4. **Sobre-especialización:** La lista resultante es extremadamente homogénea. El modelo sigue de manera demasiado estricta sus características de entrada, atrapando al usuario en un nicho cerrado y reduciendo la capacidad de descubrir contenido diverso.

---

## 5. Ejecución de la Aplicación Local (Prueba Funcional)

Para validar la robustez y transparencia del sistema en un entorno visual (Streamlit), se realizaron consultas con tres películas de géneros distintos:

**1. Consulta: *2 Fast 2 Furious (2003)* | Género: `Action|Crime|Thriller`**
* El recomendador devuelve películas como *The Equalizer* y *Die Hard: With a Vengeance*. Todas presentan un `content_score` idéntico de `1.0`. Es un claro ejemplo de **sobre-especialización**, asumiendo que el usuario solo quiere ver acción policial pura.

**2. Consulta: *300 (2007)* | Género: `Action|Drama|War|IMAX`**
* Aquí observamos puntuaciones fraccionadas (ej. `0.8699`, `0.8141`). Demuestra la naturaleza vectorial de TF-IDF: películas como *Night at the Museum* logran entrar a la lista porque comparten géneros muy pesados en el algoritmo (como `IMAX` y `Action`), aunque difieran en otros.

**3. Consulta: *IT (2017)* | Género: `Horror`**
* Arroja clásicos como *Hellraiser III* y *Hostel* con un Score total de `1.0`. La limitación advertida es vital: que a un espectador le guste el terror moderno no garantiza que disfrute otros subgéneros englobados bajo la misma etiqueta general.

**Conclusión de la Interfaz:**
La interfaz cumple con el requerimiento de explicabilidad al mostrar explícitamente el **método** ("TF-IDF y similitud coseno") y la **limitación estructural** ("Riesgo: sobre-especialización; no garantiza preferencia individual"). Esto reduce la fricción, permitiendo al usuario comprender que la homogeneidad de la lista es un límite inherente a los metadatos y no un error.

---

## 6. Preparación para la Publicación (README.md)

Para garantizar la portabilidad y el despliegue del proyecto (por ejemplo, en Streamlit Community Cloud), se documentó el siguiente `README.md` en la raíz del repositorio, especificando los comandos de arranque y las restricciones de licencia de los datos.

```text
# Sistema de Recomendación de Películas (LAB08)

Este proyecto implementa un sistema de recomendación de películas utilizando un baseline de popularidad suavizada y un recomendador basado en contenido (TF-IDF y similitud coseno). Incluye una interfaz interactiva construida con Streamlit.

## Instrucciones de Inicio (Arranque de la Aplicación)

El proyecto utiliza rutas relativas, por lo que puede ejecutarse desde cualquier directorio raíz. 

**Para desarrollo local (usando `uv`):**
1. Instala las dependencias y sincroniza el entorno: `uv sync`
2. Descarga y audita los datos (requiere internet para ~1MB):
   `uv run python scripts/download_data.py`
   `uv run python scripts/audit_data.py`
3. Inicia la aplicación visual:
   `uv run streamlit run app/streamlit_app.py`

**Para despliegue en la nube (usando requirements):**
`pip install -r requirements-cloud.txt`
`streamlit run app/streamlit_app.py`

## Restricciones y Origen del Dataset (MovieLens)

Este repositorio no aloja datos crudos ni credenciales. Los datos se obtienen en tiempo de ejecución.
* **Fuente:** GroupLens Research, University of Minnesota (MovieLens Latest Small).
* **Identidad y Uso:** Valoraciones anónimas (0.5 a 5 estrellas). Uso estrictamente académico/investigación. No comercial.
* **Referencia obligatoria:** F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. https://doi.org/10.1145/2827872
```