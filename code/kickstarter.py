"""Shared data checks and the existing five-input scikit-learn pipelines."""
from pathlib import Path
from numbers import Real
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['funding_goal_usd', 'duration_days', 'launch_month', 'main_category', 'country']
NUMERIC = FEATURES[:2]
CATEGORICAL = FEATURES[2:]
EXPORT_COLUMNS = ['id', 'launch_utc', 'deadline_utc', 'launch_year', *FEATURES, 'success']
GOAL_BINS = [0, 1000, 5000, 10000, 25000, 50000, float('inf')]
GOAL_LABELS = ['Under $1,000', '$1,000–<$5,000', '$5,000–<$10,000', '$10,000–<$25,000', '$25,000–<$50,000', '$50,000+']
DURATION_BINS = [0, 14, 30, 45, 60, float('inf')]
DURATION_LABELS = ['Up to 14 days', '>14–30 days', '>30–45 days', '>45–60 days', '>60 days']
FIGURES = ['01_success_by_category.png', '02_success_by_country.png', '03_success_by_funding_goal.png', '04_success_by_duration.png', '05_duration_comparison_by_goal.png', '06_success_by_launch_month_and_year.png']


def validate_cleaned(frame):
    """Fail loudly rather than silently alter the verified cohort."""
    if list(frame.columns) != EXPORT_COLUMNS:
        raise ValueError(f'Unexpected columns: {list(frame.columns)}')
    if frame.empty or frame.isna().any().any():
        raise ValueError('The cleaned data must be nonempty with no missing values.')
    if not frame['id'].is_unique:
        raise ValueError('Campaign IDs must be unique.')
    for field in NUMERIC:
        values = frame[field].to_numpy(dtype=float)
        if not (np.isfinite(values) & (values > 0)).all():
            raise ValueError(f'{field} must be finite and positive.')
    if not frame['launch_month'].isin(range(1, 13)).all():
        raise ValueError('Launch months must be integers from 1 through 12.')
    if not frame['launch_year'].isin([2024, 2025, 2026]).all():
        raise ValueError('Unexpected launch year.')
    if not frame['success'].isin([0, 1]).all():
        raise ValueError('Success must be 0 (failed) or 1 (successful).')
    if not frame['country'].astype(str).str.fullmatch(r'[A-Z]{2}').all():
        raise ValueError('Country must use a two-letter uppercase code.')
    if not frame['main_category'].astype(str).str.strip().ne('').all():
        raise ValueError('Main categories cannot be blank.')
    launch = pd.to_datetime(frame['launch_utc'], utc=True, errors='raise')
    deadline = pd.to_datetime(frame['deadline_utc'], utc=True, errors='raise')
    if not launch.dt.year.eq(frame['launch_year']).all() or not launch.dt.month.eq(frame['launch_month']).all():
        raise ValueError('Launch dates disagree with year or month.')
    if not (deadline < pd.Timestamp('2026-10-02', tz='UTC')).all():
        raise ValueError('Deadline exceeds the study cutoff.')
    if not np.allclose((deadline-launch).dt.total_seconds()/86400, frame['duration_days'], atol=1e-9, rtol=0):
        raise ValueError('Duration disagrees with the source timestamps.')
    return frame


def load_cleaned(path=None):
    frame = pd.read_csv(path or ROOT/'data/kickstarter_cleaned_2024_2026.csv', dtype={'id':'string'})
    return validate_cleaned(frame)


def make_models():
    preprocess = ColumnTransformer([
        ('numeric', StandardScaler(), NUMERIC),
        ('categorical', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL),
    ])
    return {
        'Logistic Regression': Pipeline([('preprocess', clone(preprocess)), ('classifier', LogisticRegression(max_iter=1000))]),
        'Decision Tree': Pipeline([('preprocess', clone(preprocess)), ('classifier', DecisionTreeClassifier(max_depth=5, random_state=42))]),
    }


def evaluate(actual, predicted):
    return {
        'accuracy': float(accuracy_score(actual, predicted)),
        'failure_precision': float(precision_score(actual, predicted, pos_label=0, zero_division=0)),
        'failure_recall': float(recall_score(actual, predicted, pos_label=0, zero_division=0)),
        'failure_f1': float(f1_score(actual, predicted, pos_label=0, zero_division=0)),
        'confusion_matrix': confusion_matrix(actual, predicted, labels=[0, 1]).tolist(),
    }


def score_campaign(fitted_pipeline, campaign):
    """Validate and score one row without fitting or changing the pipeline.

    Unknown category/country values are accepted with an explicit warning; their
    one-hot block is all zeros, not an inferred resemblance to a known group.
    """
    if set(campaign) != set(FEATURES):
        raise ValueError('Provide exactly: '+', '.join(FEATURES))
    row = dict(campaign)
    for field in NUMERIC:
        value = row[field]
        if isinstance(value, (bool, str)) or not isinstance(value, Real) or not np.isfinite(value) or value <= 0:
            raise ValueError(f'{field} must be a finite number greater than zero (without $ or commas).')
    month = row['launch_month']
    if isinstance(month, (bool, str)) or not isinstance(month, Real) or not np.isfinite(month) or int(month) != month or not 1 <= month <= 12:
        raise ValueError('launch_month must be an integer from 1 (January) to 12 (December).')
    row['launch_month'] = int(month)
    if not isinstance(row['main_category'], str) or not row['main_category'].strip():
        raise ValueError('main_category must be a nonempty category name, e.g. Games.')
    row['main_category'] = row['main_category'].strip()
    country = row['country']
    if not isinstance(country, str) or len(country) != 2 or not country.isascii() or not country.isalpha() or country != country.upper():
        raise ValueError('country must be a two-letter uppercase code, e.g. US.')
    frame = pd.DataFrame([row], columns=FEATURES)
    encoder = fitted_pipeline.named_steps['preprocess'].named_transformers_['categorical']
    notes = []
    for field, seen in zip(CATEGORICAL, encoder.categories_):
        if row[field] not in seen:
            notes.append(f'{field}={row[field]!r} was not seen in training; its one-hot block is all zeros. Interpret cautiously.')
    prediction = int(fitted_pipeline.predict(frame)[0])
    return frame, ('Reaches funding goal' if prediction == 1 else 'Misses funding goal'), notes
