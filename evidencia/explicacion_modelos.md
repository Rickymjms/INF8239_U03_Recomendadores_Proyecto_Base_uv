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