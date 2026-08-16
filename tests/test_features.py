import numpy as np
import pytest

from uwb_cir.anomaly import BaselineAnomalyDetector
from uwb_cir.features import cosine_similarity, l2_distance, peak_count, total_energy


def test_l2_distance_zero_for_same_signal():
    cir = np.array([1.0, 2.0, 3.0])
    assert l2_distance(cir, cir) == 0.0


def test_cosine_similarity_same_signal():
    cir = np.array([1.0, 2.0, 3.0])
    assert abs(cosine_similarity(cir, cir) - 1.0) < 1e-9


def test_total_energy():
    assert total_energy([1.0, 2.0, 3.0]) == 14.0


def test_peak_count():
    assert peak_count([0.0, 1.0, 0.0, 2.0, 0.0], threshold_ratio=0.4) == 2


def test_baseline_anomaly_detector():
    baseline = np.zeros(8)
    current = np.ones(8)
    detector = BaselineAnomalyDetector(baseline=baseline, threshold=1.0, method="l2")
    result = detector.predict(current)
    assert result.is_anomaly is True


@pytest.mark.parametrize("invalid_value", [np.nan, np.inf, -np.inf])
def test_cir_features_reject_non_finite_values(invalid_value):
    with pytest.raises(ValueError, match="finite"):
        total_energy([1.0, invalid_value, 2.0])


def test_cir_features_reject_empty_sequences():
    with pytest.raises(ValueError, match="empty"):
        total_energy([])


def test_baseline_detector_rejects_non_finite_values():
    with pytest.raises(ValueError, match="finite"):
        BaselineAnomalyDetector(baseline=[1.0, np.nan, 2.0])


def test_baseline_detector_rejects_non_finite_current():
    detector = BaselineAnomalyDetector(baseline=[1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match="finite"):
        detector.predict([1.0, np.inf, 3.0])
