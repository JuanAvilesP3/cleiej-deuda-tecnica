# Technical debt in Latin American academic software

Data and code for the article *Technical Debt in Latin American Academic Software: A Matched-Sample Comparison with Open-Source Controls*, submitted to the *CLEI Electronic Journal* (CLEIej).

**Authors:** Isaac David Torres-Paredes, Juan Pablo Aviles-Esparza, Italo Javier Tenempaguay-Granizo. Software Engineering, Faculty of Informatics and Electronics, Escuela Superior Politécnica de Chimborazo (ESPOCH), Riobamba, Ecuador.

## What the study does

We compare 274 academic GitHub repositories (thesis and course keywords, contributors located in Latin America) with 275 repositories matched by language and size, on nine static metrics measured with lizard, jscpd and ck. A second analysis runs SonarQube Community on a 415-repository subset, and a keyword scan counts self-admitted technical debt in source comments.

## Repository layout

| Path | Content |
|---|---|
| `src/01_download.py` | Search GitHub and select the academic and control samples |
| `src/02_preprocess.py`, `src/03_experiment.py` | Clone, measure (lizard, jscpd, ck) and consolidate the metrics |
| `src/03b_reclone_for_sonarqube.py` to `src/03f_sonarqube_stats.py` | SonarQube analysis and its statistics |
| `src/03g_country_composition.py`, `src/03h_repo_age.py` | Country composition and repository age |
| `src/04_stats.py` to `src/04g_revision_checks.py` | Mann-Whitney tests with Holm correction, language-stratified and age-adjusted analyses, self-admitted debt, jscpd thresholds, SonarQube attrition, size adjustment and a maturity check of the control group |
| `src/05_figures.py`, `src/05b_figure_smells_real.py` | Figures |
| `src/run_all.py` | Runs the pipeline in order and logs package versions to `results/logs/` |
| `data/raw/*.jsonl` | Repository lists, country resolution, clone and SonarQube logs |
| `data/raw/metrics_*.csv` | Per-repository metrics |
| `results/tables/`, `results/figures/` | Every table and figure reported in the article |
| `paper/` | LaTeX source and compiled manuscript |

## Reproducing the analysis

```bash
pip install -r requirements.txt
cp .env.example .env   # add a GitHub token and, for the SonarQube steps, a SonarQube token
python src/run_all.py
```

The SonarQube steps need a local SonarQube Community instance (`SONAR_URL`, default `http://localhost:9000`). The source code of the analyzed repositories is not redistributed; only repository identifiers and derived metrics are shared.

## Citation

Archived on Zenodo: [10.5281/zenodo.22907773](https://doi.org/10.5281/zenodo.22907773) (this DOI always resolves to the latest version).
