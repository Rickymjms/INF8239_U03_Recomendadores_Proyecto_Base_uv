## Registro y Solución de Incidencia Técnica (Compatibilidad de Tipos)

Durante la ejecución del script híbrido, se presentó una incidencia de incompatibilidad entre matrices dispersas (*sparse matrices*), matrices de NumPy y `scikit-learn`:

**Error en consola:**
```text
TypeError: float() argument must be a string or a real number, not 'csr_matrix'
ValueError: setting an array element with a sequence.
```

**Causa Raíz:** La función de similitud coseno requería arreglos densos planos compatibles, pero recibía objetos tipo `np.matrix` (generados por la suma ponderada del perfil) y `csr_matrix` (de la matriz TF-IDF) directamente.

**Solución aplicada en `scripts/lab09_hybrid.py` (Línea 47):**
```python
# Código corregido:
content_scores = cosine_similarity(profile.A, genre_matrix[candidate_rows].toarray()).ravel()
```

**Explicación:** Se utilizó `.A` para extraer el arreglo denso subyacente del perfil del usuario y `.toarray()` para transformar la matriz dispersa de los candidatos en un formato denso bidimensional compatible.
