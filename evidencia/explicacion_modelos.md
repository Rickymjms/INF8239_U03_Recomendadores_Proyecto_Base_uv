# Explicación del Modelo y Fundamentos: Sistemas de Recomendación (LAB08)

Asignatura: INF-8239 Ciencia de Datos II  
Unidad: 03 - Algoritmos y Características Generativas  

---

## 1. Fundamento Conceptual: Recomendar no es adivinar gustos
Un sistema recomendador **no predice gustos abstractos**, sino que **ordena alternativas** para una persona en un contexto determinado. La salida del sistema depende directamente de qué interacciones fueron observadas, qué candidatos se permitieron y qué objetivo se optimizó. Un resultado en el *Top-N* no representa una verdad universal ni garantiza la satisfacción absoluta del usuario.

### Términos Operativos Clave
* **Usuario:** Entidad para la cual se personaliza una list.
* **Ítem:** Elemento candidato a ser recomendado (ej. una película).
* **Feedback Explícito:** Preferencia declarada formalmente, como una valoración numérica (ej. estrellas en MovieLens).
* **Baseline:** Política simple y robusta que sirve como referencia mínima de comparación.
* **Cold Start (Arranque en frío):** Limitación ante la falta de interacciones previas para usuarios o ítems nuevos.
* **Cobertura:** Proporción del catálogo total que el sistema es capaz de mostrar en las recomendaciones.
* **Sobre-especialización:** Fenómeno donde el sistema repite en exceso características ya conocidas, atrapando al usuario en una "burbuja de contenido".

---

## 2. Arquitectura y Componentes del LAB08

El desarrollo del laboratorio se divide en fases metodológicas claras para garantizar la reproducibilidad y el rigor científico:

1. **Auditoría de Datos (MovieLens):** Permite verificar las dimensiones del dataset, la escasez (*sparsity* ~1.7%) y la distribución de las valoraciones, asegurando que no existan inconsistencias en las claves foráneas o marcas temporales (*timestamps*).
2. **Baseline de Popularidad Suavizada:** 
   * Se utiliza un promedio ponderado que combina la media de cada ítem con la media global. 
   * *Propósito:* Evitar que películas con una sola valoración extrema (ej. 5.0 estrellas dadas por un único usuario) dominen injustamente el ranking global por encima de clásicos avalados por cientos de opiniones.
3. **Recomendador por Contenido (TF-IDF y Similitud Coseno):**
   * Transforma los géneros de las películas en vectores numéricos mediante la frecuencia de términos (*TF-IDF*), reduciendo el peso de categorías excesivamente frecuentes.
   * Calcula la **similitud coseno** para identificar qué ítems comparten características descriptivas similares en el espacio de metadatos, sin requerir perfiles históricos de otros usuarios.

---

## 3. Interpretación de Resultados y Limitaciones

Al analizar las salidas generadas en los reportes (como `content_recommendations.csv`), se deben tener en cuenta las siguientes consideraciones analíticas:

* **Ausencia de la consulta:** La película consultada nunca debe aparecer en su propio Top-10, evitando redundancias innecesarias.
* **Empates técnicos (`content_score = 1.0`):** Se producen cuando varias películas comparten exactamente la misma combinación de géneros y metadatos vectorizados. El modelo puramente basado en contenido no evalúa la calidad narrativa ni la recepción del público, solo la cercanía geométrica de sus etiquetas.
* **Riesgo de Sobre-especialización:** Al seguir estrictamente los atributos de entrada, el recomendador restringe la diversidad. Si un usuario consulta una película de animación infantil, todo su Top-10 estará compuesto exclusivamente por ese nicho, ignorando géneros alternativos que podrían resultarle interesantes.

---

## 4. Conclusiones y Decisiones Metodológicas

* **Lo que podemos concluir:** Los metadatos permiten calcular similitudes de forma inmediata y robusta incluso cuando las interacciones son escasas (atenuando parcialmente el arranque en frío de ítems). Sin embargo, una alta similitud geométrica **no garantiza satisfacción ni novedad**.
* **Siguiente paso / Experimento:** Migrar desde un modelo estrictamente basado en contenido hacia un enfoque híbrido o de **factorización matricial** (como se aborda en el LAB09), permitiendo incorporar patrones colectivos derivados del comportamiento de otros usuarios.

## 5. Auditoría de Datos (Exploración del Dataset)

Al ejecutar la descarga y auditoría de los datos (`audit_data.py`), se obtienen las métricas descriptivas del conjunto de interacciones. Su correcta interpretación es fundamental antes de modelar:

* **Universo Observado (610 usuarios y 9,724 ítems valorados):** Estos números definen exclusivamente el universo de datos que el sistema ha observado. No representan a toda la población mundial ni a la totalidad del catálogo cinematográfico existente.
* **Densidad Baja (1.69%):** La escasez (*sparsity*) refleja que la inmensa mayoría de las combinaciones posibles entre un usuario y una película no tienen una valoración registrada. Es crucial entender que la ausencia de calificación **no significa rechazo**; simplemente indica que no hay interacción observada.
* **Distribución de Ratings (Media = 3.50):** Las valoraciones van de 0.5 a 5.0, con una media y mediana de 3.50. Este sesgo hacia valoraciones positivas suele reflejar un fenómeno de **autoselección**: las personas tienden a valorar aquello que ya decidieron consumir previamente porque les atraía.
* **Marcas temporales (Timestamps):** El rango temporal registrado permite organizar los datos cronológicamente, lo cual es vital para simular una evaluación temporal realista sin utilizar interacciones futuras para predecir el pasado.

---

## 6. Ejecución del Baseline de Popularidad

Al ejecutar el recomendador basado en popularidad (`lab08_content.py`), el sistema no personaliza la lista por usuario, sino que ofrece un *Top-10* general basado en el consenso colectivo.

* **El problema de la media simple:** Si ordenáramos las películas solo por su `mean` (promedio de estrellas), una película desconocida con una única valoración de 5.0 estrellas dominaría el ranking automáticamente.
* **La solución (Promedio Suavizado):** El modelo emplea un `weighted_score` que combina la media específica de cada película con la media global de todo el catálogo. 
* **Interpretación de los resultados:** 
  * Películas como *The Shawshank Redemption (1994)* lideran la lista porque acumulan **evidencia suficiente** (317 valoraciones, promedio 4.42) para recibir una puntuación suavizada altamente estable (4.39). 
  * Si comparamos dos películas con medias semejantes, el algoritmo de suavizado siempre favorecerá a aquella que posea un mayor conteo (`count`) de valoraciones, garantizando que el ranking refleje una popularidad robusta y confiable.


  ## 7. Interpretación del Modelo por Contenido (Análisis de Resultados)

El recomendador por contenido del proyecto representa los géneros de las películas mediante **TF-IDF** y calcula su cercanía utilizando la **similitud coseno**. Es vital entender que en este contexto, una recomendación significa que los ítems «comparten características registradas», no necesariamente que «le gustarán al usuario».

A partir del archivo `content_recommendations.csv` (generado tras consultar similitudes para *Toy Story*), extraemos las siguientes conclusiones metodológicas:

### 1. y 2. Verificación de la consulta en el Top-10
* **Observación:** Al revisar el archivo, el Top-10 comienza con *Turbo (2013)* y termina con *Monsters, Inc. (2001)*. La película ancla de la consulta (*Toy Story*) **no aparece** en la lista.
* **Explicación:** El algoritmo está diseñado para excluir el ítem de referencia de los resultados. Esto evita redundancias obvias, ya que el objetivo es sugerir alternativas no vistas a partir de un elemento conocido, no recomendarle al usuario la misma película que ya está evaluando.

### 3. Géneros que explican las primeras posiciones
* **Observación:** Absolutamente todas las películas del Top-10 poseen exactamente la misma cadena de géneros: `Adventure|Animation|Children|Comedy|Fantasy`.
* **Explicación:** Debido a que el modelo utiliza una representación TF-IDF limitada a los campos disponibles (los géneros), las películas que comparten esta combinación exacta de términos son matemáticamente proyectadas en la misma dirección vectorial. Los géneros compartidos actúan como la justificación local de la recomendación.

### 4. Empates en la puntuación (`content_score = 1.0`)
* **Observación:** Las 10 películas recomendadas tienen un score idéntico de `1.0`.
* **Explicación:** Un valor de similitud coseno cercano a 1 indica una gran semejanza bajo la representación TF-IDF utilizada, pero **no equivale a una probabilidad de aceptación**. El empate técnico ocurre porque todas comparten los mismos géneros disponibles de la consulta; sin embargo, esto no implica que obras como *Toy Story 2* y *The Adventures of Rocky and Bullwinkle* sean equivalentes en calidad, narrativa o recepción del público. El modelo no tiene forma de desempatar usando variables de calidad porque carece de esos datos.

### 5. El problema de la Sobre-especialización
* **Observación:** La lista resultante es extremadamente homogénea. 
* **Explicación:** Este es un ejemplo clásico de **sobre-especialización**. El modelo está siguiendo de manera demasiado consistente sus características de entrada. Al basarse únicamente en los metadatos exactos de *Toy Story*, el sistema atrapa al usuario en un nicho muy cerrado (comedia de aventura y fantasía animada para niños), lo que produce muy poco descubrimiento o novedad. El sistema es incapaz de recomendar, por ejemplo, una película familiar *live-action* que podría gustarle al mismo espectador, simplemente porque sus etiquetas de género son distintas.


## 8. Ejecución de la Aplicación Local (Prueba Funcional interactiva)

Al ejecutar la aplicación en Streamlit, pasamos de las métricas en consola a simular la experiencia del usuario final. Para validar la robustez y transparencia del sistema, se consultaron tres películas de géneros distintos. En todos los casos, la interfaz cumplió con el requerimiento de explicabilidad al mostrar la fuente ("Recomendador académico"), el método ("TF-IDF y similitud coseno") y la limitación estructural ("Riesgo: sobre-especialización; no garantiza preferencia individual").

### Resultados de la Evaluación Interactiva

**1. Consulta: *2 Fast 2 Furious (2003)***
* **Género inferido:** `Action|Crime|Thriller`
* **Análisis del Top-N:** El recomendador devuelve una lista encabezada por películas como *The Equalizer* y *Die Hard: With a Vengeance*. 
* **Observación matemática:** Todas las recomendaciones del Top-10 presentan un `content_score` idéntico de `1.0`. Esto ocurre porque el modelo encuentra otras películas en el catálogo que comparten exactamente esas tres etiquetas. Es un claro ejemplo de **sobre-especialización**, ya que asume que el usuario solo quiere ver acción policial pura, ignorando otras películas sobre carreras de autos que podrían tener etiquetas ligeramente distintas (ej. solo `Action`).

**2. Consulta: *300 (2007)***
* **Análisis del Top-N:** A diferencia de la primera consulta, aquí observamos puntuaciones fraccionadas (ej. `0.8699`, `0.8141`, `0.7728`). 
* **Observación matemática:** Esto demuestra la naturaleza vectorial de TF-IDF y la similitud coseno. Películas como *Stalingrad* y *300: Rise of an Empire* (`0.869`) comparten la mayoría de los pesos vectoriales (probablemente `Action|Drama|War|IMAX`), mientras que opciones como *Night at the Museum* (`0.814`) o *Harry Potter* (`0.772`) logran colarse en la lista porque comparten géneros muy pesados en el algoritmo (como `IMAX` y `Action`), aunque difieran en otros (aportando `Comedy` o `Fantasy`).

**3. Consulta: *IT (2017)***
* **Género inferido:** `Horror`
* **Análisis del Top-N:** La lista arroja clásicos del terror como *Hellraiser III*, *Hostel* y *Halloween (2007)*.
* **Observación matemática:** Nuevamente, al basarse en una etiqueta tan general y solitaria como `Horror`, el sistemab produce un empate técnico total (Score `1.0`). La limitación de advertencia es crucial aquí: que a un espectador le guste el terror psicológico moderno de *IT* no garantiza en absoluto que disfrute el *gore* extremo de *Human Centipede*, a pesar de que para el algoritmo representen exactamente lo mismo geométricamente[cite: 1].

### Conclusión de la Interfaz
Declarar el método y sus riesgos en la interfaz reduce la fricción. Cuando el usuario recibe recomendaciones muy cerradas (como en *IT* o *2 Fast 2 Furious*), la advertencia visible ("La lista expresa similitud de géneros; no garantiza preferencia individual") le permite comprender que no es un error del sistema, sino un límite inherente de recomendar ítems basándose exclusivamente en etiquetas de metadatos[cite: 4].