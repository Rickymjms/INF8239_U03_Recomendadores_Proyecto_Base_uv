# Dataset Card · MovieLens

## Fuente, fecha, versión y hash

| Campo | Valor |
|---|---|
| Proveedor | GroupLens Research, Universidad de Minnesota |
| Conjunto | MovieLens Latest Small (`ml-latest-small`) |
| URL de descarga | https://files.grouplens.org/datasets/movielens/ml-latest-small.zip (valor por defecto en `config.py`; puede sustituirse con la variable de entorno `MOVIELENS_URL`) |
| Documentación oficial | https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html |
| Fecha de generación del conjunto | 26 de septiembre de 2018 (según el README oficial) |
| Período de las interacciones | 29 de marzo de 1996 – 24 de septiembre de 2018 |
| Fecha de descarga | [COMPLETAR: fecha y hora de la ejecución de `scripts/download_data.py`] |
| SHA-256 del ZIP descargado | [COMPLETAR: valor impreso por `scripts/download_data.py`] |

El README oficial describe este conjunto como un *development dataset*: puede cambiar con el tiempo y no es apropiado para compartir resultados de investigación como referencia (*benchmark*). Por ello se registra el hash de los bytes descargados, que identifica la versión exacta utilizada en este laboratorio.

## Licencia y cita

Harper, F. M., & Konstan, J. A. (2015). DOI: 10.1145/2827872.

Referencia completa (según el README oficial): F. Maxwell Harper y Joseph A. Konstan. 2015. *The MovieLens Datasets: History and Context*. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. https://doi.org/10.1145/2827872

**Condiciones de uso.** El conjunto puede utilizarse con fines de investigación bajo las condiciones del README incluido en el ZIP (`data/raw/ml-latest-small/README.txt`), que en síntesis son:

- No declarar ni insinuar el respaldo de la Universidad de Minnesota ni de GroupLens Research.
- Reconocer el uso del conjunto en las publicaciones que resulten de él, citando el artículo anterior.
- Redistribuir el conjunto, incluidas sus transformaciones, solo bajo estas mismas condiciones.
- No usarlo con fines comerciales ni lucrativos sin permiso previo de un profesor del proyecto GroupLens de la Universidad de Minnesota.

La Universidad de Minnesota y los investigadores no garantizan la exactitud de los datos, su idoneidad para un propósito particular ni la validez de los resultados obtenidos con ellos. Contacto: grouplens-info@umn.edu.

Este laboratorio es de uso académico y es consistente con dichas condiciones.

## Archivos y diccionario

El ZIP contiene cuatro archivos CSV con codificación UTF-8 y una fila de encabezado. El proyecto carga únicamente `ratings.csv` y `movies.csv` (`load_movielens`); `tags.csv` y `links.csv` se extraen, pero no se utilizan.

| Archivo | ¿Usado? | Contenido | Tamaño (según el README) |
|---|---|---|---|
| `ratings.csv` | Sí | Una valoración de una película por un usuario | 100,836 valoraciones |
| `movies.csv` | Sí | Título y géneros de cada película | 9,742 películas |
| `tags.csv` | No | Etiquetas libres aplicadas por los usuarios | 3,683 aplicaciones de etiquetas |
| `links.csv` | No | Identificadores equivalentes en IMDb y TMDb | Una fila por película |

**`ratings.csv`**

| Columna | Tipo | Descripción |
|---|---|---|
| `userId` | entero | Identificador anónimo del usuario |
| `movieId` | entero | Identificador de la película, consistente entre archivos |
| `rating` | decimal | Valoración de 0.5 a 5.0 estrellas, en incrementos de 0.5 |
| `timestamp` | entero | Segundos desde el 1 de enero de 1970 (UTC) |

**`movies.csv`**

| Columna | Tipo | Descripción |
|---|---|---|
| `movieId` | entero | Identificador de la película |
| `title` | texto | Título con el año de estreno entre paréntesis; el README advierte que pueden existir errores e inconsistencias |
| `genres` | texto | Lista de géneros separados por `\|`; algunas películas figuran como `(no genres listed)` |

## Procedimiento de descarga

1. `uv run python scripts/download_data.py` llama a `download_zip(MOVIELENS_URL, ROOT / "data/raw")`, que:
   - descarga el ZIP con un tiempo máximo de espera de 60 s y detiene la ejecución ante un error HTTP;
   - calcula el SHA-256 de los bytes descargados y lo imprime;
   - verifica que cada archivo del ZIP se extraiga dentro del directorio de destino (protección contra rutas inseguras);
   - extrae el contenido en `data/raw/ml-latest-small`.
2. `uv run python scripts/audit_data.py` carga los datos y reporta número de valoraciones, películas y usuarios, rango temporal, densidad y distribución de las valoraciones.
3. `load_movielens` valida al cargar: columnas requeridas en ambos archivos, que toda valoración tenga película correspondiente y que `rating` esté entre 0.5 y 5.0.
4. Las rutas son relativas a la raíz del proyecto; pueden sustituirse con `MOVIELENS_URL` y `MOVIELENS_DIR`.

**Limitación.** El hash se calcula y se registra, pero el código no lo compara con un valor de referencia; por tanto, la descarga no se verifica automáticamente contra una versión conocida.

## Población observada y exclusiones

- **Usuarios:** 610, seleccionados al azar; todos habían valorado al menos 20 películas. Cada usuario se representa solo con un identificador anónimo (según el README).
- **Películas:** solo se incluyen las que tienen al menos una valoración o etiqueta; el README reporta 9,742.
- **Información personal:** no incluye variables demográficas.
- **Catálogo efectivo del modelo:** 9,701 películas, es decir, las que tienen valoraciones en el conjunto de entrenamiento. La diferencia de 41 respecto de `movies.csv` no se verificó; podría deberse a películas con solo etiquetas o cuya única valoración quedó en el conjunto de prueba.
- **Partición temporal (*leave-one-out*):** para cada usuario, su última valoración por marca temporal se reserva como prueba y el resto se usa para entrenar. El historial de entrenamiento va de 19 a 2,697 valoraciones por usuario.
- **Usuarios evaluables:** 587 de 610. Cada usuario conserva al menos 19 valoraciones en entrenamiento, por lo que los 23 excluidos corresponden, por deducción, a casos cuya película de prueba no aparece en el entrenamiento (el código solo evalúa pares con usuario y película conocidos).
- **Archivos no utilizados:** `tags.csv` y `links.csv`.

## Calidad, sesgos y usos prohibidos

**Calidad**

- El README advierte que es un conjunto de desarrollo, que puede cambiar y que no garantiza exactitud ni idoneidad.
- Los títulos se ingresan manualmente o se importan de TMDb y pueden contener errores o inconsistencias.
- La lectura debe hacerse en UTF-8 para mostrar correctamente los caracteres acentuados de los títulos.
- Las validaciones del procedimiento de carga (columnas, claves foráneas y rango de valoraciones) se describen en la sección anterior.

**Sesgos y limitaciones** (cifras calculadas sobre el conjunto de entrenamiento, tras la partición temporal)

| Indicador | Valor |
|---|---|
| Densidad de la matriz usuario-película | 1.69 % |
| Valoraciones concentradas en el 20 % de películas más valoradas | 77.0 % |
| Películas con menos de 5 valoraciones | 62.6 % |
| Calificación media: películas más valoradas / resto | 3.59 / 3.22 |

- **Autoselección:** solo se observan valoraciones de películas que las personas decidieron consumir; la ausencia de valoración no equivale a rechazo.
- **Concentración en popularidad:** la mayor parte de la información recae en pocas películas; la mayoría del catálogo tiene escasa evidencia.
- **Muestra de usuarios:** son usuarios con al menos 20 valoraciones; no representan a quienes interactúan poco.
- **Vigencia:** las interacciones llegan hasta 2018; no reflejan catálogo ni hábitos posteriores.
- **Demografía ausente:** no pueden afirmarse resultados por grupos poblacionales.
- **Evaluación:** con una sola interacción retenida por usuario, el HitRate subestima la relevancia real de las recomendaciones.

**Usos prohibidos o no apropiados**

*Prohibidos por la licencia:*

- Uso comercial o con fines de lucro sin permiso previo de GroupLens.
- Declarar o insinuar respaldo de la Universidad de Minnesota o de GroupLens.
- Redistribuir el conjunto o sus transformaciones bajo condiciones distintas a las de la licencia.

*No apropiados por las limitaciones del dato (criterio de este proyecto):*

- Presentar resultados como referencia compartida de investigación (*benchmark*).
- Afirmar resultados de equidad o desempeño por grupos poblacionales.
- Tomar decisiones sobre personas concretas con base en estas recomendaciones.
- Intentar reidentificar a los usuarios o combinar los datos con otras fuentes con ese fin.
- Generalizar los resultados a otras poblaciones, catálogos o períodos.
