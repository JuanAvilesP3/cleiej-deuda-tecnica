# Ficha de Instrucciones de Envío — Paper P9
**Proyecto:** Deuda Técnica en Software Académico Latinoamericano (Comparación con Controles Open-Source)  
**Marco Institucional:** FIE-ESPOCH 2026 (Planificación Oficial de Producción Científica)  
**Fecha de Actualización:** 28 de septiembre de 2026  

---

## 1. Identificación de la Revista y Política Editorial
- **Revista destino:** *CLEI Electronic Journal* (CLEIej)
- **Entidad editora:** Centro Latinoamericano de Estudios en Informática (CLEI), Montevideo, Uruguay / Latinoamérica.
- **ISSN:** 0717-5000 (En línea).
- **Indexación oficial:** Scopus, SciELO, DOAJ, Latindex Catálogo 2.0, DBLP, Google Scholar.
- **Portal oficial de envíos (OJS):** [https://cleiei.clei.org/index.php/cleiej/about/submissions](https://cleiei.clei.org/index.php/cleiej/about/submissions)
- **Editor en Jefe:** Dr. Esteban Clua (`esteban@ic.uff.br`), Universidade Federal Fluminense (UFF), Brasil.
- **Modalidad de revisión por pares:** **Simple Ciego (Single-Blind Peer Review)**. La política editorial oficial de CLEIej establece que los manuscritos no deben anonimizarse; los datos de autores y filiaciones se incluyen en la portada del artículo bajo la clase oficial `cleiej.cls`.
- **Sección en OJS:** **Regular Research Paper**.
- **Cobra APC (Article Processing Charges)?:** **NO ($0 USD)**. Revista 100% Diamond Open Access sin cobro por procesamiento ni publicación. Licencia Creative Commons CC-BY. Evidencia en `JOURNAL.md`.
- **Longitud requerida:** Artículos de investigación regulares de 8 a 15 páginas A4 (nuestro manuscrito cuenta con 11 páginas).
- **Requisito crítico del formulario OJS:** La plataforma web de CLEIej exige un **resumen de máximo 200 palabras** en el formulario de metadatos. Se proporcionan abajo ambas versiones (manuscrito completo y versión concisa para OJS).

---

## 2. Metadatos del Manuscrito (para carga en el formulario OJS)

### Título del artículo:
```text
Technical Debt in Latin American Academic Software: A Matched-Sample Comparison with Open-Source Controls
```

### Resumen Breve para el Formulario Web de OJS (< 200 palabras):
```text
Software produced in university courses and capstone projects is widely assumed to carry more technical debt than open-source projects, but this assumption has rarely been tested empirically in Latin America. We identify 274 GitHub repositories authored by Latin American university students and pair them with 275 size- and language-matched non-academic control repositories across Java, Python, and JavaScript. Comparing nine static software metrics using Mann-Whitney U tests, Holm correction, and Cliff's delta, we find that contrary to expectations, academic software exhibits significantly lower cyclomatic complexity than control repositories (median 2.16 vs. 3.12, delta = -0.37, p < 10^-11). Inheritance depth is significantly higher in academic Java code (delta = +0.29, p = 0.003), while coupling, cohesion, and code duplication show no significant differences. An independent corroboration using standalone SonarQube Community on 415 repositories validates lower cyclomatic complexity (delta = -0.458, p < 10^-14) and lower technical debt ratio (delta = -0.142, p = 0.025), while self-admitted technical debt comments (TODO/FIXME) are more frequent in academic code (42.2% vs. 23.0%, delta = +0.190, p < 0.001). These findings challenge common assumptions about student code quality in Latin America.
```

### Resumen Completo del Manuscrito (Abstract en `main.tex`):
```text
Software produced in university courses and capstone projects is widely assumed to carry more technical debt than comparable open-source work, but this assumption has rarely been tested quantitatively for the Latin American context specifically. We identify 274 GitHub repositories authored by contributors affiliated with Latin American universities (via keyword search plus contributor-location verification) and pair them with 275 non-academic control repositories matched by language and size, then compare nine static metrics (cyclomatic complexity, lines of code, code duplication, a test-file-presence proxy for coverage, and, for the Java subset, coupling, cohesion, and inheritance depth) with Mann-Whitney U tests, Holm correction, and Cliff's delta. Contrary to our initial hypothesis, academic code shows significantly lower cyclomatic complexity than the control group (median 2.16 vs. 3.12, Cliff's delta = -0.37, medium effect, p < 10^-11 after correction), not higher. Inheritance depth is significantly higher in academic Java code, as hypothesized (delta = +0.29, p = 0.003). Coupling, cohesion, duplication, and test-file presence show no significant difference after correction. We report this inverted finding directly rather than reframing the study around it, and discuss the most likely explanation: our size-matched control sample, drawn from small non-labeled repositories rather than mature open-source projects, is itself closer to informal or learning-stage code than to production software, which narrows, and in one dimension reverses, the gap the original hypothesis expected. A follow-up analysis with SonarQube Community itself (installed from its standalone ZIP distribution, without Docker or administrator privileges, on a 415-repository subset) corroborates the complexity finding independently (complexity per function: delta = -0.458, medium effect, p < 10^-14) and finds academic code has a lower SonarQube-native technical debt ratio (delta = -0.142, p = 0.025), consistent with, not contradicting, the lower-complexity result. On the same sub-sample, a self-admitted technical debt (SATD) comment count (TODO/FIXME-style markers) runs in the direction the original hypothesis expected: academic repositories more often contain at least one such marker than control repositories do (42.2% vs. 23.0%, Cliff's delta = +0.190, p < 0.001), even though the underlying code is structurally simpler.
```

### Palabras clave (Keywords):
```text
Technical debt, Software engineering education, Empirical software engineering, Latin American software, Code complexity, GitHub mining, SonarQube, Code smells
```

---

## 3. Autores y Filiación Institucional Oficial (Orden Estricto)
1. **Isaac David Torres-Paredes** (*Primer Autor, Autor de Correspondencia y Tutor Académico*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `isaac.torres@espoch.edu.ec`
   - *ORCID:* [0009-0001-7057-9316](https://orcid.org/0009-0001-7057-9316)
2. **Juan Pablo Aviles-Esparza** (*Coautor*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `juan.aviles@espoch.edu.ec`
   - *ORCID:* [0009-0007-0058-8069](https://orcid.org/0009-0007-0058-8069)
3. **Italo Javier Tenempaguay-Granizo** (*Coautor*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `italo.tenempaguay@espoch.edu.ec`
   - *ORCID:* [0009-0001-5753-4279](https://orcid.org/0009-0001-5753-4279)

---

## 4. Archivos a Subir en la Plataforma OJS (Paso a Paso)
- **Paso 2 de OJS (Upload Submission / Archivo de Envío Principal):**
  - Subir: `P9_CLEIej_manuscript.pdf` (11 páginas compiladas bajo la clase oficial `cleiej.cls`, incluye banner oficial `cleiejbanner.jpg` y figuras vectoriales/raster 300 DPI).
- **Paso 4 de OJS (Upload Supplementary Files / Archivos Complementarios):**
  1. `cover_letter.md` (Carta formal dirigida al Editor en Jefe Dr. Esteban Clua).
  2. `declaraciones.md` (Declaraciones de autoría CRediT, ética COPE de uso de IA, disponibilidad de datos en Zenodo y ausencia de conflictos).
  3. `P09_CLEIej_paquete_envio.zip` (Paquete comprimido con fuentes completas de LaTeX: `main.tex`, `refs.bib`, `cleiej.cls`, `cleiejbanner.jpg`, `IEEEtran.bst`, subcarpeta `figures/` con las 8 figuras, `README.md`).

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
- **Depósito permanente en Zenodo:** [https://doi.org/10.5281/zenodo.23005764](https://doi.org/10.5281/zenodo.23005764) (DOI: `10.5281/zenodo.23005764`).

---

## 7. Lista de Chequeo Previa al Envío (Directrices FIE-ESPOCH 2026)
- [x] Manuscrito compilado a 11 páginas (en el rango oficial requerido por CLEIej de 8 a 15 páginas).
- [x] Redactado íntegramente en inglés con estructura estándar de artículo de investigación.
- [x] 8 figuras de alta resolución alojadas en la subcarpeta `figures/` e insertadas como `figures/figX...`.
- [x] Ninguna figura generada con IA de imágenes (regla dura de la Guía Metodológica).
- [x] Cero errores y cero advertencias de BibTeX bajo el estilo `IEEEtran.bst`.
- [x] Validación empírica adicional con SonarQube Community ejecutado en modo standalone sobre 415 repositorios.
- [x] Verificación de sesgo de deserción en SonarQube confirmada como estadísticamente no significativa ($p = 0.343$ y $p = 0.118$).
- [x] Filiación institucional corregida con acentuación oficial LaTeX (`Polit\'ecnica`).
- [x] Encaje temático explícito con la comunidad de computación latinoamericana (misión central de CLEIej).
- [x] Exclusividad estricta de envío garantizada.
