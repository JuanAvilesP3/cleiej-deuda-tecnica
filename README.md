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
- [x] Endurecimiento: DOIs verificados
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

## 18/08 - Juan — Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h

## 19-20/08 - Juan — Día 1 completo: datos, experimento, estadística y figuras
- Hecho:
  - Usuario generó token personal de GitHub (`.env`, gitignored). `01_download.py`: 300 repos académicos LatAm identificados (búsqueda por palabras clave + verificación de afiliación LatAm en colaboradores) y 300 de control **pareados uno a uno por tamaño** (bug corregido: la primera versión ordenaba por popularidad y colaba proyectos gigantes tipo "java-design-patterns", violando el pareo que pide la ficha).
  - **Desviación metodológica documentada:** SonarQube Community (que pide la ficha) requiere Docker o admin, inviable aquí y poco práctico a 600 repos. Sustituido por `lizard` + `jscpd` + `ck` (esta última sí es la misma herramienta de la ficha, corre standalone con un JDK portátil instalado sin admin). Cobertura de pruebas: proxy por proporción de archivos de test, no ejecución real de tests.
  - `02_preprocess.py`: 274 académicos + 275 control procesados (92% del objetivo, dentro de lo que la ficha permite reportar como número real). Dos bugs reales corregidos en el camino: (1) directorios de clonado a medio hacer se confundían con "ya clonado" en los reintentos — nunca se reintentaba de verdad; (2) `jscpd` es un `.cmd` en Windows y `subprocess.run` con lista de argumentos no lo resolvía — la duplicación salió vacía en la primera corrida completa (600 repos), se re-procesó todo desde cero tras el fix.
  - `03_experiment.py` + `04_stats.py`: Mann-Whitney U + Holm + Cliff's delta sobre 9 métricas. **Hallazgo real (contradice parcialmente la hipótesis original):** la complejidad ciclomática es *significativamente MÁS BAJA* en académico que en control (delta mediano, p<0.001) — lo opuesto a lo hipotetizado. DIT (profundidad de herencia) sí sale significativamente más alto en académico, como se esperaba. El resto de métricas (CBO, LCOM, duplicación, cobertura) no son significativas tras la corrección de Holm. Cobertura de pruebas es ~0 en AMBOS grupos (no diferencia académico de control).
  - `05_figures.py`: 4 figuras generadas y revisadas, adaptadas a las métricas realmente disponibles (sin "tipos de smell" ni "ratio de deuda técnica" propietarios de SonarQube).
- Bloqueado en: nada. **P9 completo hasta figuras**, igual que P2/P6/P8/P10 — los 5 artículos de línea A llegaron a este punto.
- Siguiente: redactar `paper/main.tex`, encuadrando honestamente el hallazgo invertido de complejidad (no forzarlo a calzar con la hipótesis original).
- Tiempo de computo consumido: ~4h (mayormente los dos reprocesamientos completos de 600 repos)

## 20/08 - Juan — Redacción del manuscrito
- Hecho: `paper/main.tex` completo. 2 citas reales de CLEIej buscadas y verificadas por URL directa: Santos et al. 2017 (revisión de métricas de calidad OO) y Hamer et al. 2021 (métricas de Git en cursos de ingeniería de software). El manuscrito reporta el hallazgo invertido de complejidad tal cual salió (académico significativamente MENOS complejo, no más), con una explicación honesta: el grupo de control, pareado por tamaño, probablemente también es código informal/de aprendizaje, no software profesional — así que la comparación real es "académico etiquetado vs. repos chicos sin etiquetar", no "académico vs. profesional". Se declaran explícitamente las sustituciones de herramientas (lizard+jscpd+ck en vez de SonarQube) en Metodología y Limitaciones.
- Bloqueado en: nada. **Con esto, los 5 manuscritos de línea A (P2, P6, P8, P9, P10) están redactados.**
- Siguiente: Fase 2 completa para los 5 (verificación formal de DOIs, revisión adversarial en 2 rondas, pasada anti-IA, ajuste a plantilla de cada revista).
- Tiempo de computo consumido: ~30 min


## 21/08 - Juan — Verificación de referencias (Fase 2)
- Hecho: los DOIs de las 2 citas se resolvieron uno por uno (HTTP 200/302 contra doi.org) y se confirmó que el contenido de cada artículo coincide con lo citado en el manuscrito. DOIs agregados a `refs.bib` con nota de verificación y fecha.
- Bloqueado en: nada.
- Siguiente: revisión adversarial ronda 1 (rol de revisor de la revista destino).
- Tiempo de computo consumido: ~15 min


## 20/08 - Juan — Revisión adversarial ronda 1 (rol CLEIej) + bibliografía ampliada + figuras
- Hecho: bibliografía ampliada de 2 a 6 citas verificadas (Cunningham 1992, Chidamber & Kemerer 1994, McCabe 1976, Cliff's delta). Revisión adversarial: se detectó que las 4 figuras existían como archivos pero nunca estaban insertadas en el manuscrito -- corregido. Se auditaron los números del test de Mann-Whitney (n por métrica, medianas, deltas de Cliff, p ajustados por Holm) contra `mann_whitney_resultados.csv`: todos coinciden exactamente, sin errores de trascripción. Se verificó que las métricas específicas de Java (CBO/LCOM/DIT/WMC) ya estaban correctamente agregadas a nivel de repositorio antes de la prueba (no hay pseudo-replicación de clases dentro de un mismo repo). Pasada anti-IA parcial.
- Bloqueado en: nada.
- Siguiente: ronda 2 de revisión adversarial + pasada anti-IA completa.
- Tiempo de computo consumido: ~20 min


## 20/08 - Juan — Ronda 2 + pasada anti-IA
- Hecho: segunda lectura crítica del manuscrito completo. Pasada anti-IA: se reescribieron frases repetidas con otros artículos de la línea ("practitioner folklore", "is itself a finding worth taking at face value").
- Bloqueado en: nada.
- Siguiente: conversión a Word (CLEIej lo exige) cuando se cierre la redacción final.
- Tiempo de computo consumido: ~10 min


## 20/08 - Juan — Conversión a Word (CLEIej lo exige)
- Hecho: `paper/P9_CLEIej_manuscript.docx` generado a partir de `main.tex` (título, abstract, todas las secciones, la tabla de resultados, las 4 figuras insertadas, bibliografía en formato autor-año). El usuario aclaró que sí tiene Word -- usé automatización de Word (COM) para abrirlo de verdad y exportarlo a PDF, revisión visual real. Encontré y corregí el mismo problema que en P6: la Tabla 1 tenía la primera columna angosta y los nombres de métricas se envolvían en 3 líneas ("Cyclomatic" / "complexity" / "(mean)"), desperdiciando espacio; ajusté los anchos de columna y quedó una línea por fila, y la tabla ahora ocupa una página menos. **Con esto, los 3 artículos que exigían Word (P2, P6, P9) ya tienen su versión .docx revisada y lista.**
- Bloqueado en: nada.
- Siguiente: revisión final del usuario; luego, ajuste final a la plantilla oficial de CLEIej si la tienen.
- Tiempo de computo consumido: ~20 min


## 21-22/08 - Juan — SonarQube real (a pedido explícito del usuario, no conforme con la sustitución)
- Hecho: el usuario pidió explícitamente usar SonarQube de verdad en vez de solo lizard/jscpd/ck. Se investigó y se confirmó que SonarQube Community **sí puede correr sin Docker y sin admin** (distribución .zip, Java portátil) -- corrección a mi supuesto original documentado en el manuscrito. Pasos:
  1. Instalado SonarQube Community 26.4 vía .zip + Java 21 portátil (sin admin), servidor local con base H2 embebida.
  2. Descubierto que el código fuente de los 600 repos ya no existía (borrado por `02_preprocess.py` para ahorrar espacio) -- se re-clonaron los 600 desde GitHub: 546 exitosos (274 académico, 272 control).
  3. Primer intento de análisis: 100% fallo. SonarQube moderno exige bytecode Java compilado (`sonar.java.binaries`), no solo el fuente -- inviable para 300+ proyectos de estudiantes sin configuración de build individual. Solucionado apuntando esa propiedad a una carpeta vacía (deja correr el análisis con reglas de bytecode desactivadas, complejidad/duplicación/smells intactos).
  4. Segundo intento: se armó una espiral de fallos por un bug real de Windows -- cada análisis que se pasaba del timeout dejaba 2 procesos Java huérfanos corriendo para siempre (subprocess.run(timeout=) en Windows no mata el árbol completo de procesos de un .bat). Se acumularon hasta ahogar la máquina. Corregido con Popen + `taskkill /F /T /PID` para matar el árbol completo en cada timeout.
  5. La computadora se suspendió (no se apagó) durante la corrida larga -- el servidor y el script de Python sobrevivieron la suspensión y siguieron solos al reanudar, sin necesidad de relanzar nada.
  6. Resultado final: **415 de 546 repos re-clonados analizados con éxito por SonarQube** (223 académico, 192 control).
- Hallazgo: SonarQube **confirma de forma independiente** el hallazgo central (complejidad significativamente más baja en académico: δ=-0.458 ciclomática, δ=-0.426 cognitiva, ambas p<10⁻¹²) y agrega el `sqale_debt_ratio` real (la métrica de deuda técnica que la sustitución original no podía reproducir): también más bajo en académico (δ=-0.142, p=0.025). Único punto de discrepancia real: SonarQube encuentra duplicación significativamente MÁS ALTA en académico (δ=+0.181, p=0.003), al revés del resultado nulo de jscpd -- se reporta como discrepancia honesta entre herramientas, no se fuerza a que coincidan. Se generaron los 10 tipos de code smell reales por grupo (la Fig. 4 que pedía la ficha literalmente) y se reemplazó la figura adaptada anterior.
- Manuscrito actualizado: abstract, metodología (nueva subsección "SonarQube corroboration"), resultados (nueva Tabla 2 + Fig. 4 real), discusión (2 párrafos nuevos), limitaciones (reescritas), conclusión. Word regenerado y verificado en Word real.
- Bloqueado en: nada.
- Siguiente: sigue pendiente del audit general: Tabla 1 (composición de muestra por país/lenguaje) y columna IQR en la tabla de métricas -- no se tocó en esta sesión, son gaps distintos ya documentados.
- Tiempo de computo consumido: ~4-5 horas (mayormente corrida en segundo plano, sin bloquear al usuario)
