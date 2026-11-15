# DATA3125 Kickstarter project

The user-approved finalization supersedes the starter's checkpoint pauses.
Use this folder as the source of truth. Leave the separate `kickstarter-project`
starter and the job-application-agent workspace alone.

- Keep exactly two notebooks in `code/`, the cleaned CSV in `data/`, six report
  figures in `visualizations/`, and `reports/.gitkeep` for the next report phase.
- Use the local `.venv`. Run notebooks with `python code/run_notebook.py analysis`
  or `python code/run_notebook.py prep` from the repository root.
- Preserve the ten original Web Robots ZIPs in ignored `raw_snapshots/`.
- Preserve the verified 63,075-campaign cohort, documented first-observation /
  latest-snapshot deduplication, and end-of-October-1-2026 UTC eligibility cutoff.
- Use exactly five predictors: USD funding goal, duration, launch month, main
  category, country. Never use outcome fields, backers, or final pledged amounts.
- Fit preprocessing on training data only. Select the demo model using 2025
  validation, then refit fixed models on 2024–2025 and evaluate 2026 once.
- Call this a launch-year split. Outcomes can cross calendar boundaries; it is
  not a simulation of knowledge available on January 1.
- The demo reuses the fitted Decision Tree pipeline and scores one editable row;
  it must not retrain on every edit. Keep the interface inside the notebook.
- Explain failure-class metrics (0), cutoff and sampling bias, unknown categories,
  and observational associations. No causal or deployment-performance claims.
- Word/PDF report writing is the next phase. Keep the report folder ready.
