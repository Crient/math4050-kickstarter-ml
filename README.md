# MATH4050 Kickstarter machine learning final project

Independent MATH4050 extension by Gechleng Lim, starting from the finished
[DATA3125 source commit](https://github.com/Crient/data3125-kickstarter-analysis/tree/21a6242b3ec3a5c78f3d9d3de5af00189edc7c1a).
The repository retains that Git history and the complete committed DATA3125
foundation. The DATA3125 repository remains the separate course submission.

**Status: setup complete; all MATH4050 model experiments are pending.**
Open [code/03_math4050_model_comparison.ipynb](code/03_math4050_model_comparison.ipynb)
to begin. Its only executable cells locate the project and load/validate the
committed CSV. No models, searches, PCA, or new model results run during setup.

## Learning workflow

Work through one model at a time with ChatGPT: explain the method, copy a small
code block, run it, examine the output/errors, and discuss what happened.
Then vary complexity and interpret training versus validation performance.
Automated cleanup and finalization come after the experiments are understood.

The comparison notebook has prompts for the majority baseline, Logistic
Regression, Decision Tree, Random Forest, KNN, SVM, PCA with a downstream
classifier, bias–variance, final comparison/error analysis, and limitations.
All model sections remain Markdown prompts for subsequent learning sessions.

## Dataset and evaluation design

The committed CSV contains **63,075 unique campaigns**: **20,581** launched in
2024, **25,706** in 2025, and **16,788** in 2026. Its SHA-256 is
`b6c852abfce2d0dced78816e348edc59b3b919485f0401e123d7764a77fb3e2e`.
The notebook checks the hash, schema, unique IDs, year counts, dates and feature
validity using the inherited validation function. Setup does not rebuild data.

Use exactly five predictors: `funding_goal_usd`, `duration_days`, `launch_month`,
`main_category`, and `country`. Success is 1; failure is 0. ID, launch year,
timestamps and outcomes are never predictors; backers and final pledges are
excluded. Launch year determines the split; success is the target.

Train on 2024 and tune/select using 2025 validation, keeping all learned
preprocessing inside the training pipeline. This includes scaling, category
encoding and PCA; fit each inside its training fold when using cross-validation.
After freezing models/parameters, refit on 2024–2025 and compare on 2026.
**2026 is a reused evaluation benchmark:** its results were already inspected
in DATA3125. It cannot support a claim of fresh, untouched test performance,
and it must not guide tuning or model selection.

This is a **launch-year split**. Outcomes can cross calendar boundaries, and
all snapshots were collected in 2026; this does not simulate knowledge available
on January 1. Scraped goal/category fields are not proven unchanged since launch.

The cohort comes from ten uneven Web Robots snapshots from January–October
2026. Within a campaign/snapshot, retain the first observation in sorted
CSV-part order, then retain the latest available snapshot for the campaign.
Conflicting duplicate values remain a limitation of that deterministic rule.
Keep successful/failed 2024–2026 launches with deadline before
**2026-10-02 00:00 UTC** and state-change timestamp at/after launch and before
that cutoff: eligibility through the end of October 1, 2026 UTC. Later-finishing,
live, canceled and suspended campaigns are excluded. This is an observed,
nonrandom sample with cutoff selection, especially near the latest launch dates.

Evaluate accuracy alongside **failure-class (0) precision, recall and F1**.
Use actual rows/predicted columns and label order [0, 1] in confusion matrices.
Explain undefined baseline precision and any `zero_division=0` convention.
Unknown categories/countries need explicit handling and cautions: inherited
one-hot encoding ignores unseen values, producing an all-zero block for that
field, which does not identify a comparable known category. Results describe
observational associations, with no causal or deployment-performance claims.

## Local setup and execution

Use Python 3.13 and the existing pinned requirements:

```bash
git clone https://github.com/Crient/math4050-kickstarter-ml.git kickstarter-math4050-final-project
cd kickstarter-math4050-final-project
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python code/run_notebook.py comparison
```

Alternatively, open the comparison notebook and select this folder's `.venv`
as the Python/Jupyter kernel, then Run All. Paths support starting in the root
or `code/`. The runner uses the active environment with a temporary kernelspec.
No API key or raw archives are needed for the comparison setup.

## Folder structure

```text
AGENTS.md                          # MATH4050 scope and honest evaluation rules
README.md
requirements.txt                   # inherited pinned dependencies
sources.json                       # original archive provenance
docs/DATA3125_README.md             # unchanged source README and methodology
code/
  01_data_prep.ipynb                # inherited DATA3125 foundation
  02_analysis_and_prediction.ipynb  # inherited DATA3125 results/demo
  03_math4050_model_comparison.ipynb # start learning here; experiments pending
  kickstarter.py                   # inherited helpers; loading performs no fit
  run_notebook.py                   # comparison, analysis, prep
  verify_project.py                # inherited DATA3125 artifact checks only
  scripts/download_snapshots.py
  tests/test_project.py             # inherited DATA3125 regression checks
data/
  kickstarter_cleaned_2024_2026.csv  # verified committed cohort
  *.json                           # inherited DATA3125 audits/results
visualizations/                    # six inherited DATA3125 reference figures
reports/.gitkeep                   # reserved for later report writing
```

Future MATH4050 figures/results may use additional files or subfolders without
overwriting the DATA3125 foundation. `.venv/`, caches, and `raw_snapshots/` stay
ignored. Git does not contain the original ZIPs; the ten local DATA3125 archives
remain untouched in the original workspace. Their URLs/integrity metadata are
preserved in `sources.json`. No archive download/copy is needed in this pass.

## DATA3125 reference results

The existing executed notebooks, six figures, and JSON results are inherited
**DATA3125 reference results**, not MATH4050 experiments. In that work, 2025
validation selected the depth-5 Decision Tree for its in-notebook demo. The
2026 reference accuracies were 76.3% for always-success, 80.5% for Logistic
Regression, and 80.0% for the tree. The tree's failure recall was only 37.6%.
These already-inspected results explain why 2026 is a reused benchmark here.

See [the preserved DATA3125 README](docs/DATA3125_README.md) for original
findings, raw-rebuild methodology and verification history. Its relative file
links and commands refer to paths from the repository root. That document
describes the source project; its final-evaluation language and verification
history do not establish new MATH4050 results. Do not run inherited `analysis`
or `prep` merely to execute the new comparison scaffold.

The original demo stays inside `02_analysis_and_prediction.ipynb`: it scores
one editable row with an already-fitted Decision Tree, without retraining on
each edit. Word/PDF report writing remains a later phase.
