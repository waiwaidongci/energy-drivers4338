import warnings

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from src.constants.enums import FEATURES


def is_missing(value):
    return value is None or (isinstance(value, float) and not np.isfinite(value))


def missing_count(rows, feature):
    return sum(1 for row in rows if is_missing(row.get(feature)))


def missing_by_feature(rows):
    return {feature: missing_count(rows, feature) for feature in FEATURES}


def rows_with_missing(rows):
    return sum(1 for row in rows if any(is_missing(row.get(feature)) for feature in FEATURES))


def missing_summary(rows):
    return {
        'rows_with_missing': rows_with_missing(rows),
        'cells': sum(missing_count(rows, feature) for feature in FEATURES),
        'by_feature': missing_by_feature(rows),
    }


def median_values(x):
    """Median per column over observed cells; NaN where a column has no observation."""
    values = np.asarray(x, float)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        return np.nanmedian(values, axis=0)


class MedianImputer(BaseEstimator, TransformerMixin):
    """Fill missing feature cells with the median of the rows this stage was fitted on.

    Each fold and the final model fit their own statistics from their own training rows, so a
    validation or sealed cell never informs a training-stage fill. Only when a fold's training
    rows hold no observation at all for a feature does the fill fall back to the median of the
    locked training scope, which is recorded per fold. Missing energy targets are rejected
    before this transformer runs.
    """

    def __init__(self, fallback=None):
        self.fallback = fallback

    def fit(self, X, y=None):
        values = np.asarray(X, float)
        medians = median_values(values)
        self.fallback_features_ = np.isnan(medians).tolist()
        if self.fallback is not None:
            fallback = np.asarray(self.fallback, float)
            if fallback.shape != medians.shape:
                raise ValueError('补值依据与特征数量不一致')
            medians = np.where(np.isnan(medians), fallback, medians)
        if np.isnan(medians).any():
            empty = [index + 1 for index, value in enumerate(medians) if np.isnan(value)]
            raise ValueError(f'训练范围内特征全部缺测（第{empty[0]}项），无法按训练中位数补值')
        if not np.isfinite(medians).all():
            raise ValueError('训练特征必须为有限值')
        self.statistics_ = medians
        self.n_features_in_ = values.shape[1]
        return self

    def transform(self, X):
        values = np.asarray(X, float).copy()
        rows, columns = np.where(np.isnan(values))
        if len(rows):
            values[rows, columns] = self.statistics_[columns]
        return values
