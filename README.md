# Documentación y Análisis del Modelo: Sistemas de Recomendación (LAB08)

**Asignatura:** INF-8239 Ciencia de Datos II  
**Unidad:** 03 - Algoritmos y Características Generativas  
**Autor académico:** Edwin Ramón José Nolasco
**Replicado y realizado por:** Manuel De Jesus Mañana Santana
**Universidad:** Universidad Autónoma de Santo Domingo (UASD)  
**Gestor de entorno:** `uv` (Python 3.12)  
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

## Creación del Corte Temporal y Experimento Base (LAB09)

Para evitar fugas de datos (*data leakage*) y simular una evaluación realista del futuro a partir del pasado, se implementó un corte temporal reservando la última valoración de cada usuario elegible.

### Comando Ejecutado
```bash
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75

### Resultados Obtenidos

- **RMSE ($1.0264$):** Refleja la precisión en la estimación numérica de las valoraciones de estrellas. Permite cuantificar el error promedio del modelo colaborativo en la matriz latente.
- **HitRate@10 ($0.0375$):** Mide el acierto en el ordenamiento del Top-10, indicando el porcentaje de usuarios cuyo ítem real retenido apareció en las primeras diez posiciones sugeridas.
- **Cobertura del Catálogo ($7.75$):** Cuantifica la diversidad de ítems distintos que el sistema es capaz de recomendar al conjunto global de usuarios.
- **Costo Computacional ($21.81$ s):** Representa el tiempo de entrenamiento requerido para optimizar los 20 factores latentes en 12 épocas mediante descenso de gradiente estocástico (SGD).
- **Política de Arranque en Frío (Cold Start):** Configurada mediante popularidad por cantidad y media (no personalizada) como mecanismo de respaldo (*fallback*) para usuarios sin historial previo.

### Conclusión Metodológica

Este experimento base demuestra que un modelo basado en factorización matricial y un enfoque híbrido (alpha = 0.75) equilibra la afinidad colectiva de la comunidad con las características descriptivas del contenido, permitiendo evaluar de forma objetiva tanto el error de predicción (RMSE) como la utilidad en el ranking (HitRate@10).

##  Construcción y Explicación del Modelo Híbrido

Para equilibrar los patrones de interacción colectiva con las características descriptivas de las películas, el sistema combina la puntuación colaborativa normalizada y la señal de contenido mediante el parámetro de ponderación alpha.

### Comparación Controlada de Parámetros
Se mantuvieron constantes la semilla, el corte temporal, los factores ($20$) y las épocas ($12$), evaluando dos configuraciones opuestas:

1. **Enfoque basado en Contenido (alpha = 0.25$):**
   * **HitRate@10:** $0.0324$
   * **Cobertura del catálogo:** $10.65%$
   * **Señal dominante:** Atributos de género (TF-IDF y similitud coseno). Favorece la diversidad y cobertura, permitiendo explorar áreas más amplias del catálogo.

2. **Enfoque basado en Colaborativo (alpha = 0.75$):**
   * **HitRate@10:** $0.0375$
   * **Cobertura del catálogo:** $7.75%$
   * **Señal dominante:** Factores latentes de la factorización matricial ($P$ y $Q$). Prioriza las afinidades de la comunidad.

### Selección Justificada por Evidencia
Se selecciona **alpha = 0.75$** basándose en la métrica de éxito en el ranking (*HitRate@10*), ya que demuestra una mayor capacidad de acierto al sugerir el ítem real retenido dentro de las primeras 10 posiciones, superando a la variante basada en contenido a pesar de una reducción marginal en la cobertura del catálogo.

### Política de Arranque en Frío (*Cold Start*)
Para los usuarios o ítems nuevos que carecen de historial suficiente en la matriz de interacciones, el sistema aplica un mecanismo de respaldo (*fallback*) basado en popularidad suavizada (conteo y media), garantizando una respuesta operativa no personalizada.

## Evaluación de Tres Perfiles de Usuario (LAB09)

### A. Usuario con Historial Amplio (userId: 414 | Valoraciones en train: 2,697)
* **Comprobación de exclusión:** Se verificó de forma estricta que la lista de recomendaciones **excluye todos los ítems vistos** previamente en el entrenamiento (`True` tanto para alpha=0.25$ como para alpha=0.75).
* **Estabilidad y Coincidencia:** Se registró una coincidencia del **4/10** en el Top-10 entre ambas configuraciones de alpha. Esto demuestra que, al poseer un historial robusto, los factores latentes colaborativos y las señales de contenido convergen parcialmente, manteniendo una alta consistencia en las sugerencias de alta calidad (ej. *12 Angry Men*, *Life Is Beautiful*).

### B. Usuario con Historial Pequeño (userId: 595 | Valoraciones en train: 19)
* **Comprobación de exclusión:** Al igual que en el perfil amplio, la lista **excluye correctamente los ítems vistos** en su historial reducido (`True`).
* **Estabilidad y Dependencia:** La coincidencia en el Top-10 entre alpha=0.25 y alpha=0.75 también se sitúa en **4/10**. Sin embargo, la selección de títulos muestra mayor sensibilidad debido a la escasez de datos (*sparsity*), donde las ponderaciones de contenido y factores latentes alternan el orden de clásicos como *Casablanca*, *Pulp Fiction* y *12 Angry Men*.

### C. Usuario Nuevo / Arranque en Frío (userId: 611 | No presente en entrenamiento)
* **Comprobación del Fallback:** Ante la ausencia total de interacciones en la matriz, el sistema activa de forma automática el mecanismo de respaldo (*fallback*) basado en popularidad suavizada (conteo y media de valoraciones).
* **Declaración Oficial:** Se verifica y certifica formalmente que **la lista generada NO es personalizada** (ej. *Forrest Gump*, *The Shawshank Redemption*, *Pulp Fiction*, *The Matrix*), garantizando una respuesta operativa inmediata y segura para la interfaz sin comprometer falsamente la personalización.

### Registro de Evidencia
Los resultados detallados de la evaluación por rangos, perfiles y ponderaciones de alpha se encuentran debidamente documentados y exportados en el archivo:
* `reports/profiles_check.csv`

## 7. Comparación de costo y utilidad (tabla de Pareto y Green AI)

Se evaluaron seis configuraciones (factores 10, 20 y 40 × épocas 6 y 12) con tres semillas (42, 123 y 999) y α = 0.75. La utilidad se midió con HitRate@10; el costo, con las épocas de entrenamiento y el tamaño del modelo serializado. El tiempo medido varió hasta 8 s entre semillas y ejecuciones de una misma configuración (p. ej., 40/12: 16.2 a 24.4 s), por lo que se reporta como evidencia complementaria y no como criterio de dominancia.

| Factores | Épocas | HitRate@10 | RMSE | Cobertura | Tiempo medio (s) | Tamaño (MB) | ¿Dominada? |
|---|---|---|---|---|---|---|---|
| 10 | 6 | 0.0142 | 1.1069 | 13.81 % | 11.13 | 1.05 | No |
| 20 | 6 | 0.0187 | 1.0985 | 17.74 % | 9.66 | 1.84 | No |
| 40 | 6 | 0.0233 | 1.0864 | 20.70 % | 8.24 | 3.41 | No |
| 10 | 12 | 0.0420 | 1.0359 | 5.62 % | 19.99 | 1.05 | No |
| 20 | 12 | 0.0324 | 1.0282 | 7.40 % | 18.39 | 1.84 | Sí (por 10/12) |
| 40 | 12 | 0.0386 | 1.0198 | 9.71 % | 20.65 | 3.41 | Sí (por 10/12) |

**Mejora marginal por épocas.** Pasar de 6 a 12 épocas duplica el cómputo (factor 2.03 en el tiempo medio), eleva el HitRate medio de 0.019 a 0.038 y reduce el RMSE en cerca de 0.07, con el mismo sentido en los tres niveles de factores. A cambio, la cobertura cae de 14–21 % a 6–10 %, es decir, las recomendaciones se concentran en menos ítems.

**Mejora marginal por factores.** A 12 épocas, pasar de 10 a 40 factores multiplica por 3.2 el tamaño (1.05 a 3.41 MB) sin mejora detectable del HitRate (−0.003, dentro del ruido). El RMSE mejora 0.016 y la cobertura sube cuatro puntos porcentuales.

**Decisión.** Se selecciona 10 factores y 12 épocas: ofrece el HitRate medio más alto con el menor tamaño y el mismo cómputo que las demás configuraciones de 12 épocas. Las diferencias de HitRate entre ellas no son estadísticamente distinguibles (unos 25, 19 y 23 usuarios de 587), por lo que la elección se sustenta en el costo. Limitaciones: es la configuración de menor cobertura y no se probaron más de 12 épocas.

## Revisión de riesgos

Los riesgos se cuantificaron con la configuración seleccionada (10 factores, 12 épocas, semilla 42), sobre 587 usuarios evaluables y un catálogo de 9,701 películas, para α = 0.25 y α = 0.75. Con la semilla 42 las métricas coinciden con las del paso 7 (HitRate@10 de 0.0307 y cobertura de 5.77 % con α = 0.75).

| Métrica | α = 0.25 | α = 0.75 |
|---|---|---|
| HitRate@10 | 0.0290 | 0.0307 |
| Cobertura del catálogo | 8.38 % | 5.77 % |
| Ítems distintos recomendados | 813 | 560 |
| Cuota de los 10 ítems más recomendados | 23.6 % | 31.1 % |
| Recomendaciones en el 20 % más popular | 90.6 % | 92.9 % |
| Percentil de popularidad de lo recomendado (historial: 0.910) | 0.924 | 0.944 |
| Diversidad intralista del Top-10 (historial: 0.751) | 0.452 | 0.719 |

La diferencia de HitRate entre ambos valores de α corresponde a un solo usuario (17 frente a 18 aciertos de 587), por lo que no es concluyente.

###  Popularidad dominante (riesgo principal)

Entre el 90.6 % y el 92.9 % de las recomendaciones corresponde al 20 % de las películas más valoradas, proporción superior a la que ese grupo concentra en las valoraciones observadas (77.0 %). El percentil medio de popularidad de lo recomendado (0.924 con α = 0.25 y 0.944 con α = 0.75) supera levemente al de los historiales (0.910), lo que indica una amplificación moderada del sesgo preexistente en los datos. Una misma película aparece en el Top-10 de cerca del 40 % de los usuarios (237 y 226 de 587; la más frecuente con α = 0.75 es *The Godfather*), y los 10 ítems más recomendados ocupan entre el 23.6 % y el 31.1 % de las 5,870 posiciones. La cobertura (5.8 %–8.4 %) está muy por debajo del máximo teórico de 60.5 % (5,870 posiciones sobre 9,701 ítems), y el índice de Gini de la exposición (0.98–0.99) contrasta con un mínimo posible cercano a 0.40.

Mitigación propuesta (no probada en este laboratorio): reordenamiento con penalización de popularidad, tope de exposición por ítem y reporte de la cobertura junto con el HitRate, con un umbral mínimo previo a cualquier despliegue.

### Burbuja de filtro

Con α = 0.25, la diversidad intralista del Top-10 es 0.452, equivalente al 60 % de la de una muestra del historial (0.751); con α = 0.75 es 0.719 (96 %). Dar más peso al contenido incrementa la cobertura y reduce la concentración, pero homogeneiza las listas por género: existe un intercambio entre el riesgo de popularidad y el de burbuja, sin una opción dominante. Además, para el usuario 595 (19 valoraciones) con α = 0.75 aparecen dos películas de la saga *The Godfather* y dos de *The Lord of the Rings*, lo que evidencia redundancia por franquicia. No se midió la serendipia.

Mitigación propuesta: seleccionar α considerando ambas métricas e incorporar una cuota de exploración o de diversificación de géneros.

### Sesgo de selección

La matriz usuario-ítem tiene una densidad de 1.69 %; el 77.0 % de las valoraciones se concentra en el 20 % de los ítems y el 62.6 % de las películas tiene menos de 5 valoraciones. Los ítems populares presentan una calificación media mayor (3.59) que el resto (3.22), lo cual es consistente con que las personas valoran lo que deciden consumir. Solo se observan valoraciones de ítems consumidos, por lo que la ausencia de valoración no equivale a rechazo. Asimismo, el HitRate considera acierto únicamente el ítem retenido de cada usuario (corte temporal de una interacción), por lo que subestima la relevancia real de las demás recomendaciones.

Mitigación: interpretar las métricas de forma comparativa y no como tasas de satisfacción.

### Ausencia de demografía

MovieLens Latest Small solo contiene identificadores anónimos y no incluye variables demográficas; además, sus usuarios valoraron al menos 20 películas. Por ello no pueden afirmarse resultados por grupos poblacionales ni evaluarse equidad demográfica, y los hallazgos no deben generalizarse a usuarios menos activos o fuera de la población observada.

Como indicador de heterogeneidad (no como sustituto de la demografía) se calculó el HitRate@10 por nivel de actividad (baja, media y alta). Con α = 0.25 fue 0.045, 0.025 y 0.016; con α = 0.75, 0.035, 0.035 y 0.021. Cada grupo acumula entre 3 y 9 aciertos, por lo que las diferencias no son concluyentes.

### Retroalimentación

No se midió, pues el sistema no está desplegado y el entrenamiento utiliza un conjunto estático. En un uso real, la concentración observada podría reforzarse si los ítems más recomendados acumularan más interacciones, las cuales luego alimentarían el reentrenamiento.

Mitigación propuesta: registrar la exposición de cada recomendación, reservar una fracción de exploración y reentrenar con monitoreo de cobertura y diversidad.

### Síntesis

- **Riesgo principal:** popularidad dominante, por contar con evidencia cuantitativa en toda la población evaluada y estar vinculado a la configuración seleccionada, que presenta la menor cobertura de las probadas.
- **Mitigación:** penalizar la popularidad en el reordenamiento, limitar la exposición por ítem y reportar la cobertura junto con el HitRate.



# Declaración de Uso Responsable de IA

## Propósito y Alcance

Esta declaración acompaña a la práctica del LAB08 (Sistema de Recomendación de Películas) y documenta el uso de herramientas de Inteligencia Artificial (IA) en el proceso de aprendizaje, desarrollo y documentación. Su objetivo es garantizar la transparencia y la alineación con los principios éticos de la asignatura, reconociendo la procedencia de los resultados y las decisiones tomadas durante el ejercicio.

## Declaración de Uso

1.  **Uso de IA como asistente de documentación:**
  - Se utilizó asistencia de IA (modelo de lenguaje) para organizar, estructurar y redactar los hallazgos de las pruebas de consola, la interpretación de la interfaz interactiva y la formulación del archivo README.md.
  - El modelo de lenguaje actuó bajo el rol de asistente de estudio, sin reemplazar la ejecución directa del código ni la interpretación crítica de los resultados.

2.  **Ejecución y Verificación Autónoma:**
  - Todos los comandos de entorno (uv), descarga de datos, ejecución de modelos (lab08\_content.py) y pruebas funcionales (streamlit\_app.py) fueron ejecutados directamente por el estudiante en su entorno local (Windows/WSL/macOS).
  - La IA no fue utilizada para generar el código base del repositorio original, el cual fue proporcionado por la cátedra.
  - La IA no fue utilizada para evadir los pasos de evaluación manuales, sino para documentar las observaciones extraídas durante la ejecución del paso 8 (Prueba funcional con Streamlit).

3.  **Comprensión y Responsabilidad:**
  - El estudiante asume la responsabilidad total de las interpretaciones documentadas en relación con los conceptos de similitud coseno, vectorización TF-IDF, el problema de sobre-especialización y los límites del baseline de popularidad suavizada, tal como se describen en la Unidad 03.
  - Las conclusiones redactadas reflejan un entendimiento genuino de los resultados arrojados por los algoritmos analizados en el LAB08.

4.  **Integridad Académica:**
  - Esta declaración confirma que el trabajo presentado respeta las normativas de la Universidad Autónoma de Santo Domingo (UASD) en materia de probidad académica.
  - El uso de la IA se limitó al apoyo en redacción y organización de las notas de estudio, cumpliendo con la directriz de que la herramienta debe potenciar el análisis crítico y no sustituir la labor investigativa del estudiante.

-----
*Firma: Manuel De Jesus Mañana Santana* 
*Fecha: Octubre 2026*
