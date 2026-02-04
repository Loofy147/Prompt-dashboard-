import pytest
import json
from validator import validate_apex_output, ValidationError

def test_meta_architect_schema_validation():
    # Mock output following the v3.0 standard
    mock_output = {
        "meta_analysis": {
            "input_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "timestamp_utc": "2026-02-04T00:00:00Z",
            "processing_time_ms": 1250,
            "confidence_score": 0.9950
        },
        "primary_output": {
            "response_type": "technical_spec",
            "content": "Full technical specification content...",
            "word_count": 450,
            "readability_score": 45.5
        },
        "quality_metrics": {
            "P_persona": 1.0,
            "T_tone": 1.0,
            "F_format": 1.0,
            "S_specificity": 1.0,
            "C_constraints": 1.0,
            "R_context": 1.0,
            "Q_composite": 1.0000
        },
        "validation": {
            "schema_compliance": True,
            "constraint_violations": [],
            "edge_cases_handled": ["Large payload", "Missing context fallback"],
            "test_coverage": 98.5
        },
        "metadata": {
            "tokens_consumed": 850,
            "estimated_cost_usd": 0.0125,
            "model_version": "claude-3-5-sonnet-20241022",
            "optimization_iterations": 2
        }
    }

    # This should pass
    assert validate_apex_output(mock_output) is True

def test_meta_architect_quality_breach():
    mock_output = {
        "meta_analysis": {},
        "primary_output": {},
        "quality_metrics": {"Q_composite": 0.8500},  # Below 0.90
        "validation": {"test_coverage": 96.0, "constraint_violations": []},
        "metadata": {}
    }

    with pytest.raises(ValidationError, match="Quality threshold breach"):
        validate_apex_output(mock_output)

def test_meta_architect_coverage_breach():
    mock_output = {
        "meta_analysis": {},
        "primary_output": {},
        "quality_metrics": {"Q_composite": 0.9500},
        "validation": {"test_coverage": 90.0, "constraint_violations": []}, # Below 95.0
        "metadata": {}
    }

    with pytest.raises(ValidationError, match="Test coverage breach"):
        validate_apex_output(mock_output)

def test_store_integration_meta_architect():
    with open('prompt_assets/prompt_store.json', 'r') as f:
        store = json.load(f)

    found_architect = False
    for t in store['templates']:
        if "Apex Meta-Architect" in t['name']:
            found_architect = True
            assert t['Q'] == 1.0
            break

    assert found_architect, "Apex Meta-Architect template not found in store"
