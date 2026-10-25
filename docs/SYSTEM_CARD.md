# System Card · Recomendador (LAB09)

## Usuarios y propósito
* **Propósito del sistema:** Generar recomendaciones personalizadas de películas en formato de ranking (*Top-N*) a partir de interacciones históricas y metadatos de contenido, equilibrando la afinidad colectiva con la diversidad de catálogo.
* **Usuarios a los que sirve:** Usuarios activos con historiales de consumo variados y usuarios nuevos bajo políticas de arranque en frío (*cold start*).

## Catálogo y candidatos
* **Universo de ítems:** Compuesto por las $9,742$ películas del catálogo de MovieLens.
* **Generación de candidatos:** Filtrado estricto que excluye los elementos ya visualizados o valorados en el conjunto de entrenamiento, evaluando un subconjunto masivo ordenado mediante factores latentes y similitud basada en contenido.

## Señales utilizadas
* **Señal Colaborativa:** Factores latentes de menor dimensión ($P$ y $Q$) obtenidos mediante factorización matricial para capturar patrones de afinidad colectiva.
* **Señal de Contenido:** Perfiles de género vectorizados mediante **TF-IDF**, evaluados a través de la **similitud de coseno** con respecto al perfil ponderado del usuario.

## Modelos y fallback
* **Modelo principal:** Sistema híbrido ponderado que combina la puntuación colaborativa y de contenido mediante el parámetro alfa ($\alpha = 0.75$).
* **Mecanismo de Respaldo (*Fallback*):** Para usuarios sin historial o en situación de arranque en frío, el sistema desactiva la personalización y activa un respaldo basado en popularidad suavizada (combinando conteo y media global).

## Métricas offline
* **RMSE (Root Mean Squared Error):** Evalúa el error numérico en la estimación de valoraciones (con un promedio estándar óptimo de $\approx 1.02 - 1.03$).
* **HitRate@10:** Mide el acierto en el ordenamiento del *Top-10* en el corte temporal (*temporal split*), alcanzando un rango competitivo de $\approx 0.0375 - 0.0420$.

## Cold start, cobertura y diversidad
* **Arranque en frío:** Gestionado mediante la política de popularidad suavizada no personalizada.
* **Cobertura y Diversidad:** Analizadas mediante diversidad intralista (*ILD*) y distribución de exposición, evaluando el equilibrio entre precisión y concentración de recomendaciones en los éxitos de taquilla (*popularity bias*).

## Riesgos y monitoreo
* **Riesgos identificados:** 
  * *Sesgo de popularidad:* Enfoque excesivo hacia los blockbusters del catálogo.
  * *Burbuja de filtro:* Reducción de la serendipia y la exploración temática.
* **Monitoreo:** Revisiones periódicas de diversidad, seguimiento de *HitRate@10* por terciles de actividad y optimización de costos computacionales bajo principios de **Green AI**.