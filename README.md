# P09 · Deuda técnica en software académico latinoamericano

**Revista destino:** CLEIej
**Línea:** A · **GPU:** Nula · **Días asignados:** 18-19 ago

## Estado
- [ ] Ficha de revista completa (JOURNAL.md)
- [ ] Datos descargados (data/raw/)
- [ ] Experimento ejecutado (día 1)
- [ ] Redacción y figuras (día 2)
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
