import pytest
import sys
import os

# Add api to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from quality_calculator import compute_Q, get_quality_level, validate_features

def test_perfect_score():
    features = {'P': 1.0, 'T': 1.0, 'F': 1.0, 'S': 1.0, 'C': 1.0, 'R': 1.0}
    Q, _ = compute_Q(features)
    assert Q == 1.0

def test_zero_score():
    features = {'P': 0.0, 'T': 0.0, 'F': 0.0, 'S': 0.0, 'C': 0.0, 'R': 0.0}
    Q, _ = compute_Q(features)
    assert Q == 0.0

def test_typical_score():
    features = {
        'P': 0.92, 'T': 0.88, 'F': 0.95,
        'S': 0.90, 'C': 0.85, 'R': 0.70
    }
    Q, _ = compute_Q(features)
    # 0.18*0.92 + 0.22*0.88 + 0.20*0.95 + 0.18*0.90 + 0.12*0.85 + 0.10*0.70
    # = 0.1656 + 0.1936 + 0.19 + 0.162 + 0.102 + 0.07 = 0.8832
    # Wait, the example in quality_calculator.py said 0.8766. Let me re-check weights.
    # wP=0.18, wT=0.22, wF=0.20, wS=0.18, wC=0.12, wR=0.10
    # Sum: 0.18+0.22+0.20+0.18+0.12+0.10 = 1.0. Correct.
    # Calculation:
    # 0.18 * 0.92 = 0.1656
    # 0.22 * 0.88 = 0.1936
    # 0.20 * 0.95 = 0.1900
    # 0.18 * 0.90 = 0.1620
    # 0.12 * 0.85 = 0.1020
    # 0.10 * 0.70 = 0.0700
    # Sum = 0.8832.
    # Ah, the docstring example might have had slightly different numbers or a typo.
    # I'll stick to my calculation.
    assert round(Q, 4) == 0.8832

def test_quality_levels():
    assert get_quality_level(0.95) == "Excellent"
    assert get_quality_level(0.85) == "Good"
    assert get_quality_level(0.75) == "Fair"
    assert get_quality_level(0.65) == "Poor"

def test_validation_missing_key():
    with pytest.raises(ValueError, match="Missing required features"):
        validate_features({'P': 1.0})

def test_validation_out_of_bounds():
    with pytest.raises(ValueError, match="is out of bounds"):
        validate_features({'P': 1.1, 'T': 0.8, 'F': 0.8, 'S': 0.8, 'C': 0.8, 'R': 0.8})
