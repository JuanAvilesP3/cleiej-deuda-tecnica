# P09 · Deuda técnica en software académico latinoamericano

**Revista destino:** CLEIej
**Línea:** A · **GPU:** Nula · **Días asignados:** 18-19 ago

## Estado
- [x] Ficha de revista completa (JOURNAL.md)
- [x] Datos descargados (data/raw/) — 274 repos académicos + 275 control, pareados por tamaño
- [x] Experimento ejecutado (día 1) — métricas de complejidad, duplicación, cobertura (proxy), CK (solo Java)
- [x] Estadística (día 1) — Mann-Whitney U + Holm + Cliff's delta
- [x] Figuras generadas (4/4)
- [ ] Redacción del manuscrito (día 2)
- [ ] Endurecimiento: DOIs verificados
- [ ] Endurecimiento: revisión adversarial ronda 1
- [ ] Endurecimiento: revisión adversarial ronda 2
- [ ] Revisión cruzada
- [ ] Repositorio en GitHub
- [ ] Publicado en Zenodo (DOI)
- [ ] Carta de presentación y declaraciones
- [ ] Entregado al responsable académico

## Protocolo

**Revista destino:** CLEI Electronic Journal (CLEIej)
**Fecha de inicio:** 18/08
**Responsable:** Juan (línea A)

### Pregunta de investigación
¿Qué patrones de deuda técnica caracterizan al software producido en cursos y trabajos de titulación de universidades latinoamericanas, frente a proyectos de código abierto comparables?

### Hipótesis
El software académico tiene cobertura de pruebas cercana a cero, complejidad ciclomática más alta por método, y una proporción distinta de tipos de code smell: más duplicación y menos problemas de concurrencia.

### Variables
- Independientes: grupo (académico / control), lenguaje, tamaño del repositorio
- Dependientes: densidad de smells, ratio de deuda técnica, cobertura, complejidad ciclomática media y máxima, duplicación
- Controladas: lenguaje y decil de tamaño (vía pareo)

### Diseño
- Condiciones experimentales: 300 repositorios académicos + 300 de control, pareados por lenguaje y decil de tamaño
- Repeticiones por condición: n/a (estudio observacional)
- Semilla aleatoria: 42
- Validación: no aplica ML; análisis estadístico no paramétrico

### Prueba estadística
Mann-Whitney U por métrica con corrección de Holm (no asumir normalidad — las métricas de software están muy sesgadas).
- Tamaño del efecto a reportar: Cliff's delta

### Criterio de interés
- Si la hipótesis se confirma: la deuda técnica es sistemáticamente mayor en código académico, con un patrón distinto de smells (más duplicación, menos concurrencia).
- Si se refuta: no hay diferencia significativa, o el patrón de smells es similar al del código abierto general — también es un hallazgo relevante para la comunidad CLEI.

### Datasets
| Nombre | Fuente | Licencia | Verificado |
|--------|--------|----------|------------|
| Repositorios académicos LatAm (construido) | GitHub API + GHArchive | Términos de GitHub | No |
| Repositorios de control (construido) | GitHub API, pareados por lenguaje/tamaño | Términos de GitHub | No |

Filtros: lenguaje (Java/Python/JavaScript), > 500 líneas, ≥ 10 commits, afiliación LatAm declarada o indicios de trabajo académico en nombre/descripción.

### Citas obligatorias de la revista destino
1. (pendiente — extraer de trabajos de ingeniería de software empírica, calidad de código y educación en computación publicados en CLEIej)
2.
3.

## Bitácora

## 18/08 - Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h

## 19-20/08 - Día 1 completo: datos, experimento, estadística y figuras
- Hecho:
  - Usuario generó token personal de GitHub (`.env`, gitignored). `01_download.py`: 300 repos académicos LatAm identificados (búsqueda por palabras clave + verificación de afiliación LatAm en colaboradores) y 300 de control **pareados uno a uno por tamaño** (bug corregido: la primera versión ordenaba por popularidad y colaba proyectos gigantes tipo "java-design-patterns", violando el pareo que pide la ficha).
  - **Desviación metodológica documentada:** SonarQube Community (que pide la ficha) requiere Docker o admin, inviable aquí y poco práctico a 600 repos. Sustituido por `lizard` + `jscpd` + `ck` (esta última sí es la misma herramienta de la ficha, corre standalone con un JDK portátil instalado sin admin). Cobertura de pruebas: proxy por proporción de archivos de test, no ejecución real de tests.
  - `02_preprocess.py`: 274 académicos + 275 control procesados (92% del objetivo, dentro de lo que la ficha permite reportar como número real). Dos bugs reales corregidos en el camino: (1) directorios de clonado a medio hacer se confundían con "ya clonado" en los reintentos — nunca se reintentaba de verdad; (2) `jscpd` es un `.cmd` en Windows y `subprocess.run` con lista de argumentos no lo resolvía — la duplicación salió vacía en la primera corrida completa (600 repos), se re-procesó todo desde cero tras el fix.
  - `03_experiment.py` + `04_stats.py`: Mann-Whitney U + Holm + Cliff's delta sobre 9 métricas. **Hallazgo real (contradice parcialmente la hipótesis original):** la complejidad ciclomática es *significativamente MÁS BAJA* en académico que en control (delta mediano, p<0.001) — lo opuesto a lo hipotetizado. DIT (profundidad de herencia) sí sale significativamente más alto en académico, como se esperaba. El resto de métricas (CBO, LCOM, duplicación, cobertura) no son significativas tras la corrección de Holm. Cobertura de pruebas es ~0 en AMBOS grupos (no diferencia académico de control).
  - `05_figures.py`: 4 figuras generadas y revisadas, adaptadas a las métricas realmente disponibles (sin "tipos de smell" ni "ratio de deuda técnica" propietarios de SonarQube).
- Bloqueado en: nada. **P9 completo hasta figuras**, igual que P2/P6/P8/P10 — los 5 artículos de línea A llegaron a este punto.
- Siguiente: redactar `paper/main.tex`, encuadrando honestamente el hallazgo invertido de complejidad (no forzarlo a calzar con la hipótesis original).
- Tiempo de computo consumido: ~4h (mayormente los dos reprocesamientos completos de 600 repos)

## 20/08 - Redacción del manuscrito
- Hecho: `paper/main.tex` completo. 2 citas reales de CLEIej buscadas y verificadas por URL directa: Santos et al. 2017 (revisión de métricas de calidad OO) y Hamer et al. 2021 (métricas de Git en cursos de ingeniería de software). El manuscrito reporta el hallazgo invertido de complejidad tal cual salió (académico significativamente MENOS complejo, no más), con una explicación honesta: el grupo de control, pareado por tamaño, probablemente también es código informal/de aprendizaje, no software profesional — así que la comparación real es "académico etiquetado vs. repos chicos sin etiquetar", no "académico vs. profesional". Se declaran explícitamente las sustituciones de herramientas (lizard+jscpd+ck en vez de SonarQube) en Metodología y Limitaciones.
- Bloqueado en: nada. **Con esto, los 5 manuscritos de línea A (P2, P6, P8, P9, P10) están redactados.**
- Siguiente: Fase 2 completa para los 5 (verificación formal de DOIs, revisión adversarial en 2 rondas, pasada anti-IA, ajuste a plantilla de cada revista).
- Tiempo de computo consumido: ~30 min
