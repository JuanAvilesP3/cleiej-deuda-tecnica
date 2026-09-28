# Ficha de Instrucciones de Envío — Paper P9

## 1. Identificación de la Revista y Política Editorial
- **Revista destino:** *CLEI Electronic Journal* (CLEIej)
- **Entidad editora:** Centro Latinoamericano de Estudios en Informática (CLEI), Montevideo, Uruguay / Latinoamérica.
- **ISSN:** 0717-5000 (En línea).
- **Indexación oficial:** Scopus, SciELO, DOAJ, Latindex Catálogo 2.0, DBLP, Google Scholar.
- **Portal oficial de envíos (OJS):** [https://cleiei.clei.org/index.php/cleiej/about/submissions](https://cleiei.clei.org/index.php/cleiej/about/submissions)
- **Modalidad de revisión por pares:** **Simple Ciego (Single-Blind Peer Review)**. La política editorial oficial de CLEIej establece que los manuscritos no deben anonimizarse; los datos de autores y filiaciones se incluyen en la portada del artículo bajo la clase oficial `cleiej.cls`.
- **Sección en OJS:** **Regular Research Paper**.
- **Cobra APC (Article Processing Charges)?:** **NO ($0 USD)**. Revista 100% Diamond Open Access sin cobro por procesamiento ni publicación.

---

## 2. Metadatos del Manuscrito (para carga en el formulario OJS)

### Título del artículo:
```text
Technical Debt in Latin American Academic Software: A Matched-Sample Comparison with Open-Source Controls
```

### Resumen en inglés (Abstract):
```text
Software produced in university courses and capstone projects is widely assumed to carry more technical debt than comparable open-source work, but this assumption has rarely been tested quantitatively for the Latin American context specifically. We identify 274 GitHub repositories authored by contributors affiliated with Latin American universities (via keyword search plus contributor-location verification) and pair them with 275 non-academic control repositories matched by language and size, then compare nine static metrics (cyclomatic complexity, lines of code, code duplication, a test-file-presence proxy for coverage, and, for the Java subset, coupling, cohesion, and inheritance depth) with Mann-Whitney U tests, Holm correction, and Cliff's delta. Contrary to our initial hypothesis, academic code shows significantly lower cyclomatic complexity than the control group (median 2.16 vs. 3.12, Cliff's delta = -0.37, medium effect, p < 10^-11 after correction), not higher. Inheritance depth is significantly higher in academic Java code, as hypothesized (delta = +0.29, p = 0.003). Coupling, cohesion, duplication, and test-file presence show no significant difference after correction. We report this inverted finding directly rather than reframing the study around it, and discuss the most likely explanation: our size-matched control sample, drawn from small non-labeled repositories rather than mature open-source projects, is itself closer to informal or learning-stage code than to production software, which narrows, and in one dimension reverses, the gap the original hypothesis expected. A follow-up analysis with SonarQube Community itself (installed from its standalone ZIP distribution, without Docker or administrator privileges, on a 415-repository subset) corroborates the complexity finding independently (complexity per function: delta = -0.458, medium effect, p < 10^-14) and finds academic code has a lower SonarQube-native technical debt ratio (delta = -0.142, p = 0.025), consistent with, not contradicting, the lower-complexity result. On the same sub-sample, a self-admitted technical debt (SATD) comment count (TODO/FIXME-style markers) runs in the direction the original hypothesis expected: academic repositories more often contain at least one such marker than control repositories do (42.2% vs. 23.0%, Cliff's delta = +0.190, p < 0.001), even though the underlying code is structurally simpler.
```

### Palabras clave (Keywords):
```text
Technical debt, Software engineering education, Empirical software engineering, Latin American software, Code complexity, GitHub mining, SonarQube, Code smells
```

---

## 3. Autores y Filiación Institucional Oficial (Orden Estricto)
1. **Isaac David Torres-Paredes** (*Autor de correspondencia*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `isaac.torres@espoch.edu.ec`
   - *ORCID:* [0009-0001-7057-9316](https://orcid.org/0009-0001-7057-9316)
2. **Juan Pablo Aviles-Esparza**
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `juan.aviles@espoch.edu.ec`
   - *ORCID:* [0009-0007-0058-8069](https://orcid.org/0009-0007-0058-8069)
3. **Italo Javier Tenempaguay-Granizo**
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `italo.tenempaguay@espoch.edu.ec`
   - *ORCID:* [0009-0001-5753-4279](https://orcid.org/0009-0001-5753-4279)

---

## 4. Archivos a Subir en la Plataforma OJS (Paso a Paso)
- **Paso 2 de OJS (Upload Submission / Archivo de Envío Principal):**
  - Subir: [`paper/P9_CLEIej_manuscript.pdf`](file:///c:/Users/Juan/Desktop/PAPERS/09-cleiej-deuda-tecnica/paper/P9_CLEIej_manuscript.pdf) (11 páginas compiladas bajo la clase oficial `cleiej.cls`, incluye banner oficial `cleiejbanner.jpg` y figuras vectoriales).
- **Paso 4 de OJS (Upload Supplementary Files / Archivos Complementarios):**
  1. `paper/cover_letter.md` (Carta formal dirigida al Editor en Jefe de CLEIej).
  2. `paper/declaraciones.md` (Declaraciones de autoría CRediT, ética COPE de uso de IA, disponibilidad de datos en Zenodo y ausencia de conflictos).
  3. Paquete comprimido con fuentes completas de LaTeX: [`paquetes_envio/P09_CLEIej_paquete_envio.zip`](file:///c:/Users/Juan/Desktop/PAPERS/paquetes_envio/P09_CLEIej_paquete_envio.zip) (contiene `main.tex`, `refs.bib`, `cleiej.cls`, `cleiejbanner.jpg`, `IEEEtran.bst`, subcarpeta `figures/` con las 8 figuras vectoriales y raster de 300 DPI, `cover_letter.md`, `declaraciones.md`, `README.md`).

---

## 5. Revisores Pares Sugeridos (3 Expertos Latinoamericanos en Ingeniería de Software)
1. **Prof. Dr. Marco Tulio Valente**  
   - *Filiación:* Department of Computer Science, Universidade Federal de Minas Gerais (UFMG), Belo Horizonte, Brasil.  
   - *Correo electrónico:* `mtov@dcc.ufmg.br`  
   - *Especialidad:* Ingeniería de software empírica, deuda técnica, minería de repositorios GitHub y calidad de código.
2. **Prof. Dr. Cristian Mateos**  
   - *Filiación:* ISISTAN Research Institute, CONICET / Universidad Nacional del Centro de la Provincia de Buenos Aires (UNICEN), Tandil, Argentina.  
   - *Correo electrónico:* `cmateos@exa.unicen.edu.ar`  
   - *Especialidad:* Métricas orientadas a objetos, calidad de código fuente, herramientas de análisis estático.
3. **Prof. Dr. Claudia López**  
   - *Filiación:* Department of Informatics, Universidad Técnica Federico Santa María (UTFSM), Valparaíso, Chile.  
   - *Correo electrónico:* `claudia@inf.utfsm.cl`  
   - *Especialidad:* Ingeniería de software empírica, colaboración en desarrollo de software y educación en informática.

---

## 6. Enlaces de Reproducibilidad y Datos Abiertos
- **Repositorio público en GitHub:** [https://github.com/JuanAvilesP3/cleiej-deuda-tecnica.git](https://github.com/JuanAvilesP3/cleiej-deuda-tecnica.git)
- **Depósito de datos y código en Zenodo:** [https://doi.org/10.5281/zenodo.22907774](https://doi.org/10.5281/zenodo.22907774) (DOI: `10.5281/zenodo.22907774`).

---

## 7. Lista de Chequeo Previa al Envío (Checklist)
- [x] Manuscrito compilado a 11 páginas (en el rango oficial requerido por CLEIej de 8 a 15 páginas).
- [x] Redactado íntegramente en inglés con estructura estándar de artículo de investigación.
- [x] Figuras en alta resolución alojadas en la subcarpeta `figures/` e insertadas como `figures/figX...`.
- [x] Cero errores y cero advertencias de BibTeX bajo el estilo `IEEEtran.bst`.
- [x] Validación empírica adicional con SonarQube Community ejecutado en modo standalone sobre 415 repositorios.
- [x] Verificación de sesgo de deserción en SonarQube confirmada como estadísticamente no significativa ($p = 0.343$ y $p = 0.118$).
- [x] Filiación institucional corregida con acentuación oficial LaTeX (`Polit\'ecnica`).
