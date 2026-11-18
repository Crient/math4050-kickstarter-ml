# MATH4050 Kickstarter machine learning extension

This is the independent MATH4050 workspace, based on DATA3125 commit
`21a6242b3ec3a5c78f3d9d3de5af00189edc7c1a` from
https://github.com/Crient/data3125-kickstarter-analysis.
Keep all MATH4050 changes in this folder/repository. Leave the separate
DATA3125 submission, starter, and job-application-agent workspace alone.

- This initial pass is setup only. The user learns each model by copying and
  running small blocks with ChatGPT, examining outputs and errors, and discussing
  complexity and bias–variance. Do not implement or run model training, tuning,
  PCA fitting, new model results, or automated finalization until requested in
  those later learning sessions.
- Use `code/03_math4050_model_comparison.ipynb` for the comparison. Additional
  notebooks and MATH4050 figures are permitted as the project develops; the
  DATA3125 two-notebook/six-figure limit does not apply here.
- Preserve the inherited preparation/analysis notebooks, cleaned CSV, six
  reference figures, results JSON files, source manifest, and foundation code.
  Label their outputs as DATA3125 reference results. Use separate filenames or
  a MATH4050 subfolder for future results and figures.
- Use this project's local `.venv`. From the repository root, run the new
  setup with `python code/run_notebook.py comparison`. Inherited `analysis` and
  `prep` commands remain available but rerun DATA3125 work; setup does not need
  them. The inherited verifier checks DATA3125 reference artifacts only.
- Preserve the verified 63,075 unique campaigns: 20,581 launched in 2024,
  25,706 in 2025, and 16,788 in 2026. Setup uses the committed CSV, without
  rebuilding it or downloading raw archives. Keep any original ZIPs intact and
  ignored in `raw_snapshots/`; the original DATA3125 archives stay untouched.
- Preserve the documented deduplication: first observation in sorted CSV-part
  order within campaign/snapshot, followed by latest available snapshot per
  campaign. This deterministic choice does not resolve conflicting records.
- Preserve the end-of-October-1-2026 UTC deadline/outcome eligibility cutoff
  (`2026-10-02 00:00 UTC`, exclusive) and all sampling/retrospective limitations.
- Use exactly five predictors: USD funding goal, duration, launch month, main
  category, country. Success is 1 and failure is 0. Never use outcome fields,
  backers, final pledged amounts, IDs, timestamps, or launch year as predictors.
  Launch year is for splitting only; outcome is the target only.
- Fit learned preprocessing (including scaling, encoding, imputation and PCA)
  on training data only, inside pipelines. Train candidates on 2024 and tune/
  select using 2025 validation. Freeze the design before refitting on 2024–2025
  and comparing on 2026. If cross-validation is introduced, it must remain
  within 2024–2025 with preprocessing fitted separately inside each fold.
- The 2026 outcomes/results have already been inspected in DATA3125. Call 2026
  a reused evaluation benchmark, never a fresh untouched test set. Do not use
  its performance to tune or choose models.
- Call this a launch-year split. Outcomes can cross calendar boundaries; it is
  not a simulation of knowledge available on January 1. All snapshots were
  collected in 2026, and predictor availability at launch is not established.
- Report accuracy alongside failure-class (0) precision, recall and F1, plus
  confusion matrices with actual rows/predicted columns and class order [0, 1].
  Explain undefined precision and any zero_division convention for baselines.
- Explain unknown categories/countries and encoder behavior, sampling/cutoff
  bias, observational associations, and limits of missed failures. Make no
  causal or deployment-performance claims.
- Preserve the inherited in-notebook demo: reuse its fitted Decision Tree
  pipeline for one editable row; do not retrain on every edit.
- Keep `reports/.gitkeep` ready. Word/PDF writing is a later phase.
