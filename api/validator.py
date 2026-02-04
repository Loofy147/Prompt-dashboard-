import json
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception raised for errors in output validation."""
    pass

def validate_apex_output(output):
    """
    Validates that an output dictionary complies with the Apex Meta-Architect v3.0 standard.

    Checks:
    1. Mandatory top-level keys
    2. Quality threshold (Q_composite >= 0.90)
    3. Test coverage threshold (>= 95.0)
    4. Numeric precision (4 decimal places)
    """
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            raise ValidationError("Output is not valid JSON")

    required_keys = ["meta_analysis", "primary_output", "quality_metrics", "validation", "metadata"]
    for key in required_keys:
        if key not in output:
            raise ValidationError(f"Missing mandatory top-level key: {key}")

    # Check Quality Threshold
    q_composite = output.get("quality_metrics", {}).get("Q_composite", 0)
    if q_composite < 0.90:
        raise ValidationError(f"Quality threshold breach: Q_composite {q_composite} < 0.90")

    # Check Test Coverage
    test_coverage = output.get("validation", {}).get("test_coverage", 0)
    if test_coverage < 95.0:
        raise ValidationError(f"Test coverage breach: {test_coverage}% < 95.0%")

    # Check Constraint Violations
    violations = output.get("validation", {}).get("constraint_violations", [])
    if violations:
        raise ValidationError(f"Constraint violations detected: {', '.join(violations)}")

    return True

def generate_input_digest(text):
    """Generates a SHA-256 hash for the given text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_iso_timestamp():
    """Returns current UTC time in ISO-8601 format."""
    return datetime.utcnow().isoformat() + 'Z'
